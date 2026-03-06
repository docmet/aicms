import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models import User


class OAuthAuthorizeRequest(BaseModel):
    code_challenge: str | None = None
    code_challenge_method: str | None = None

router = APIRouter(tags=["mcp"])

# Short-lived OAuth authorization codes.
# Stores: code -> (mcp_token, expires_at, code_challenge, code_challenge_method)
# code_challenge / method are None when the client doesn't use PKCE.
_oauth_codes: dict[str, tuple[str, datetime, str | None, str | None]] = {}


def _verify_pkce(code_verifier: str, code_challenge: str, method: str) -> bool:
    """Verify a PKCE code_verifier against a stored code_challenge."""
    if method == "S256":
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return computed == code_challenge
    if method == "plain":
        return code_verifier == code_challenge
    return False


def _clean_expired_codes() -> None:
    now = datetime.now(UTC)
    expired = [k for k, (_, exp, *_rest) in _oauth_codes.items() if now > exp]
    for k in expired:
        del _oauth_codes[k]


@router.post("/register")
async def register_mcp_client(
    client_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register a new MCP client - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://mcp_server:8000/register",
            json={**client_data, "user_id": str(current_user.id)},
            headers={"X-User-ID": str(current_user.id)},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "MCP server error",
            )

    return response.json()  # type: ignore


@router.get("/clients")
async def get_mcp_clients(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    """List user's MCP clients - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://mcp_server:8000/clients",
            headers={"X-User-ID": str(current_user.id)},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "MCP server error",
            )

    return response.json()  # type: ignore


@router.post("/oauth-authorize")
async def oauth_authorize(
    body: OAuthAuthorizeRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Issue a short-lived OAuth code tied to the user's MCP credential.

    Called by the /connect frontend page after the user logs in and clicks
    'Allow'. Returns a single-use code that the MCP server exchanges for
    the user's MCP token at /token.
    """
    _clean_expired_codes()

    # Get or create the user's MCP credential via the MCP server
    async with httpx.AsyncClient() as client:
        list_resp = await client.get(
            "http://mcp_server:8000/clients",
            headers={"X-User-ID": str(current_user.id)},
        )
        clients = list_resp.json() if list_resp.status_code == 200 else []

        if clients:
            mcp_token: str = clients[0]["token"]
        else:
            reg_resp = await client.post(
                "http://mcp_server:8000/register",
                json={"name": "My AI Connection", "tool_type": "claude", "user_id": str(current_user.id)},
                headers={"X-User-ID": str(current_user.id)},
            )
            if reg_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to create MCP credential")
            mcp_token = reg_resp.json()["token"]

    code = secrets.token_urlsafe(32)
    code_challenge = body.code_challenge if body else None
    code_challenge_method = body.code_challenge_method if body else None
    _oauth_codes[code] = (mcp_token, datetime.now(UTC) + timedelta(minutes=5), code_challenge, code_challenge_method)
    return {"code": code}


@router.get("/exchange-code")
async def exchange_code(
    code: str = Query(...),
    code_verifier: str | None = Query(None),
) -> dict[str, str]:
    """Exchange a short-lived OAuth code for an MCP token.

    Called internally by the MCP server's /token endpoint. No user auth
    required — the code itself is the credential (single-use, 5 min TTL).
    """
    _clean_expired_codes()
    entry = _oauth_codes.pop(code, None)
    if not entry:
        raise HTTPException(status_code=401, detail="Invalid or expired code")
    mcp_token, expires_at, stored_challenge, stored_method = entry
    if datetime.now(UTC) > expires_at:
        raise HTTPException(status_code=401, detail="Code expired")
    if stored_challenge:
        if not code_verifier:
            raise HTTPException(status_code=400, detail="code_verifier required")
        if not _verify_pkce(code_verifier, stored_challenge, stored_method or "S256"):
            raise HTTPException(status_code=400, detail="Invalid code_verifier")
    return {"token": mcp_token}


@router.delete("/clients/{client_id}")
async def delete_mcp_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete MCP client - proxy to MCP server"""

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://mcp_server:8000/clients/{client_id}",
            headers={"X-User-ID": str(current_user.id)},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else "MCP server error",
            )

    return response.json()  # type: ignore
