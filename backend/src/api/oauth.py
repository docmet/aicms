"""OAuth endpoints for MCP server authentication"""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/authorize")
async def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    code_challenge: str | None = Query(None),
    code_challenge_method: str | None = Query(None),
    state: str | None = Query(None),
    scope: str | None = Query(None),
) -> RedirectResponse:
    """OAuth authorization endpoint for Claude Desktop"""

    # For now, we'll auto-approve since this is for personal use
    # In production, you'd show a consent screen

    # Generate an authorization code
    import secrets

    auth_code = secrets.token_urlsafe(32)

    # Store the code temporarily (in production, use Redis or database)
    # For now, we'll just redirect with the code

    # Build redirect URL with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url)


@router.post("/token")
async def token(
    grant_type: str = Query(...),
    code: str = Query(...),
    client_id: str | None = Query(None),
    code_verifier: str | None = Query(None),
    redirect_uri: str | None = Query(None),
) -> dict[str, str | int]:
    """OAuth token endpoint - exchange auth code for access token"""

    # For now, we'll accept any code and return a mock token
    # In production, you'd validate the code and return a proper JWT

    return {
        "access_token": "mock-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "mock-refresh-token",
    }
