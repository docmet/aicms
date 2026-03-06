"""Billing API — Revolut Merchant integration.

Routes mounted at /api/billing.

  POST /checkout          — create Revolut order, return checkout_url
  POST /verify            — verify order state, upgrade plan on success
  POST /webhook           — Revolut webhook (updates plan on payment event)
"""

import hashlib
import hmac
import json
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.config import get_settings
from src.database import get_db
from src.models.user import User, UserPlan

router = APIRouter()

PLAN_PRICES = {
    "pro": {"amount": 999, "currency": "USD", "label": "MyStorey Pro — $9.99/mo"},
    "agency": {"amount": 9900, "currency": "USD", "label": "MyStorey Agency — $99/mo"},
}


def _revolut_base_url() -> str:
    settings = get_settings()
    if settings.revolut_sandbox:
        return "https://sandbox-merchant.revolut.com/api/1.0"
    return "https://merchant.revolut.com/api/1.0"


def _revolut_headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.revolut_merchant_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ── Checkout ──────────────────────────────────────────────────────────────────


class CheckoutResponse(BaseModel):
    checkout_url: str
    order_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    plan: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CheckoutResponse:
    """Create a Revolut order and return the hosted checkout URL."""
    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Invalid plan")

    price = PLAN_PRICES[plan]
    settings = get_settings()

    if not settings.revolut_merchant_api_key:
        raise HTTPException(status_code=503, detail="Payment not configured")

    redirect_url = (
        f"{settings.frontend_url}/dashboard/billing"
        f"?payment_complete=true&plan={plan}"
    )
    cancel_url = f"{settings.frontend_url}/dashboard/billing?plan={plan}"

    payload = {
        "amount": price["amount"],
        "currency": price["currency"],
        "description": price["label"],
        "email": str(current_user.email),
        "redirect_url": redirect_url,
        "cancel_url": cancel_url,
        "metadata": {
            "user_id": str(current_user.id),
            "plan": plan,
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_revolut_base_url()}/orders",
            json=payload,
            headers=_revolut_headers(),
            timeout=15,
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="Payment provider error")

    data = resp.json()
    checkout_url = data.get("checkout_url") or data.get("redirect_url", "")
    order_id = data.get("id", "")

    return CheckoutResponse(checkout_url=checkout_url, order_id=order_id)


# ── Verify (after redirect back from Revolut) ─────────────────────────────────


class VerifyResponse(BaseModel):
    success: bool
    plan: str | None = None


@router.post("/verify", response_model=VerifyResponse)
async def verify_payment(
    order_id: str,
    plan: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VerifyResponse:
    """Verify a Revolut order and upgrade user plan if paid."""
    settings = get_settings()

    if not settings.revolut_merchant_api_key:
        raise HTTPException(status_code=503, detail="Payment not configured")

    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Invalid plan")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_revolut_base_url()}/orders/{order_id}",
            headers=_revolut_headers(),
            timeout=15,
        )

    if resp.status_code != 200:
        return VerifyResponse(success=False)

    data = resp.json()
    state = data.get("state", "")

    if state in ("completed", "authorised"):
        result = await db.execute(select(User).where(User.id == current_user.id))
        user = result.scalar_one()
        user.plan = UserPlan(plan)  # type: ignore
        db.add(user)
        await db.commit()
        return VerifyResponse(success=True, plan=plan)

    return VerifyResponse(success=False)


# ── Webhook ───────────────────────────────────────────────────────────────────


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def revolut_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    revolut_signature: str | None = Header(default=None, alias="Revolut-Signature"),
) -> dict[str, str]:
    """Revolut sends payment events here. Verifies HMAC and upgrades user plan."""
    settings = get_settings()
    body = await request.body()

    if settings.revolut_webhook_secret and revolut_signature:
        expected = hmac.new(
            settings.revolut_webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, revolut_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = payload.get("event", "")
    order = payload.get("order", {})
    state = order.get("state", "")
    metadata = order.get("metadata", {})

    if event == "ORDER_COMPLETED" or state in ("completed", "authorised"):
        user_id = metadata.get("user_id")
        plan = metadata.get("plan")
        if user_id and plan and plan in PLAN_PRICES:
            from uuid import UUID

            try:
                uid = UUID(user_id)
            except ValueError:
                return {"status": "ignored"}
            result = await db.execute(select(User).where(User.id == uid))
            user = result.scalar_one_or_none()
            if user:
                user.plan = UserPlan(plan)  # type: ignore
                db.add(user)
                await db.commit()

    return {"status": "ok"}
