"""Billing API — Stripe integration.

Routes mounted at /api/billing.

  POST /checkout          — create Stripe Checkout Session, return checkout_url
  POST /verify            — verify session after Stripe redirect, upgrade plan
  GET  /portal            — create Stripe Customer Portal session
  POST /webhook           — Stripe webhook (checkout.session.completed, subscription events)
"""

from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.config import get_settings
from src.database import get_db
from src.models.user import User, UserPlan

router = APIRouter()

PLAN_PRICE_IDS: dict[str, str] = {}  # populated lazily from settings

VALID_PLANS = {"pro", "agency"}


def _get_stripe() -> None:
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Payment not configured")
    stripe.api_key = settings.stripe_secret_key


def _price_id(plan: str) -> str:
    settings = get_settings()
    if plan == "pro":
        return settings.stripe_pro_price_id
    if plan == "agency":
        return settings.stripe_agency_price_id
    raise HTTPException(status_code=400, detail="Invalid plan")


# ── Checkout ──────────────────────────────────────────────────────────────────


class CheckoutResponse(BaseModel):
    checkout_url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    plan: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CheckoutResponse:
    """Create a Stripe Checkout Session and return the hosted checkout URL."""
    if plan not in VALID_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    _get_stripe()
    settings = get_settings()
    success_url = (
        f"{settings.frontend_url}/dashboard/billing"
        f"?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}"
    )
    cancel_url = f"{settings.frontend_url}/dashboard/billing?plan={plan}"

    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": _price_id(plan), "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_email": str(current_user.email),
        "metadata": {"user_id": str(current_user.id), "plan": plan},
        "subscription_data": {
            "metadata": {"user_id": str(current_user.id), "plan": plan}
        },
    }

    # Reuse Stripe customer if we have one
    if current_user.stripe_customer_id:  # type: ignore[truthy-bool]
        params["customer"] = current_user.stripe_customer_id
        del params["customer_email"]

    session = stripe.checkout.Session.create(**params)
    return CheckoutResponse(checkout_url=session.url or "")


# ── Verify (after Stripe redirect) ────────────────────────────────────────────


class VerifyResponse(BaseModel):
    success: bool
    plan: str | None = None


@router.post("/verify", response_model=VerifyResponse)
async def verify_payment(
    session_id: str,
    plan: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VerifyResponse:
    """Retrieve a Stripe Checkout Session and upgrade plan if payment succeeded."""
    if plan not in VALID_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    _get_stripe()

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        return VerifyResponse(success=False)

    if session.payment_status not in ("paid", "no_payment_required"):
        return VerifyResponse(success=False)

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one()
    user.plan = UserPlan(plan)  # type: ignore[assignment]

    # Persist Stripe IDs for future portal access
    if session.customer and not user.stripe_customer_id:  # type: ignore[truthy-bool]
        user.stripe_customer_id = str(session.customer)  # type: ignore[assignment]
    if session.subscription and not user.stripe_subscription_id:  # type: ignore[truthy-bool]
        user.stripe_subscription_id = str(session.subscription)  # type: ignore[assignment]

    db.add(user)
    await db.commit()
    return VerifyResponse(success=True, plan=plan)


# ── Customer Portal ───────────────────────────────────────────────────────────


class PortalResponse(BaseModel):
    portal_url: str


@router.get("/portal", response_model=PortalResponse)
async def customer_portal(
    current_user: Annotated[User, Depends(get_current_user)],
) -> PortalResponse:
    """Create a Stripe Customer Portal session for managing subscriptions."""
    if not current_user.stripe_customer_id:  # type: ignore[truthy-bool]
        raise HTTPException(status_code=400, detail="No active subscription found")

    _get_stripe()
    settings = get_settings()

    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,  # type: ignore[arg-type]
        return_url=f"{settings.frontend_url}/dashboard/settings",
    )
    return PortalResponse(portal_url=session.url)


# ── Webhook ───────────────────────────────────────────────────────────────────


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    stripe_signature: str | None = Header(default=None, alias="stripe-signature"),
) -> dict[str, str]:
    """Handle Stripe webhook events."""
    settings = get_settings()
    body = await request.body()

    # Verify webhook signature if secret is configured
    if settings.stripe_webhook_secret and stripe_signature:
        stripe.api_key = settings.stripe_secret_key
        try:
            event = stripe.Webhook.construct_event(
                body, stripe_signature, settings.stripe_webhook_secret
            )
        except stripe.SignatureVerificationError:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
    else:
        # No secret configured — parse raw (dev only)
        import json

        try:
            data = json.loads(body)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        event = stripe.Event.construct_from(data, stripe.api_key)

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(obj, db)
    elif event_type in ("customer.subscription.deleted", "customer.subscription.paused"):
        await _handle_subscription_ended(obj, db)

    return {"status": "ok"}


async def _handle_checkout_completed(
    session: dict,
    db: AsyncSession,
) -> None:
    metadata = session.get("metadata") or {}
    user_id = metadata.get("user_id")
    plan = metadata.get("plan")

    if not user_id or not plan or plan not in VALID_PLANS:
        return

    from uuid import UUID

    try:
        uid = UUID(user_id)
    except ValueError:
        return

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        return

    user.plan = UserPlan(plan)  # type: ignore[assignment]
    if session.get("customer") and not user.stripe_customer_id:  # type: ignore[truthy-bool]
        user.stripe_customer_id = str(session["customer"])  # type: ignore[assignment]
    if session.get("subscription") and not user.stripe_subscription_id:  # type: ignore[truthy-bool]
        user.stripe_subscription_id = str(session["subscription"])  # type: ignore[assignment]

    db.add(user)
    await db.commit()


async def _handle_subscription_ended(
    subscription: dict,
    db: AsyncSession,
) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(User).where(User.stripe_customer_id == str(customer_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        return

    user.plan = UserPlan.free  # type: ignore[assignment]
    user.stripe_subscription_id = None  # type: ignore[assignment]
    db.add(user)
    await db.commit()
