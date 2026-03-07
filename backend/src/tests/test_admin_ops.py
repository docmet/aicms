"""Tests for admin operations: GET /api/admin/sites endpoint and admin MCP tools (OPS-01/02/03).

These tests are stubs marked xfail until plan 14-06 adds:
- GET /api/admin/sites endpoint in backend/src/api/admin.py
- get_platform_stats, list_all_sites, trigger_deployment MCP tools in server.py

Once plan 14-06 is complete, remove xfail markers and fill in full assertions.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.auth import AuthService


async def _create_admin_user(db: AsyncSession) -> tuple[str, str]:
    """Helper: create an admin user directly in DB. Returns (email, password)."""
    email = "admin-ops-test@example.com"
    password = "password123"
    hashed = AuthService.get_password_hash(password)
    user = User(email=email, password_hash=hashed, is_admin=True)
    db.add(user)
    await db.commit()
    return email, password


@pytest.mark.xfail(
    reason="GET /api/admin/sites endpoint not yet added — requires plan 14-06",
    strict=False,
)
async def test_admin_sites_endpoint(
    client: AsyncClient, db: AsyncSession
) -> None:
    """GET /api/admin/sites should return all active sites with user_email and user_plan."""
    email, password = await _create_admin_user(db)
    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    r = await client.get(
        "/api/admin/sites",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, f"Expected 200 but got {r.status_code}: {r.text}"
    data = r.json()
    assert isinstance(data, list)
    if data:
        row = data[0]
        assert "user_email" in row
        assert "user_plan" in row
        assert "slug" in row


@pytest.mark.xfail(
    reason="get_platform_stats MCP tool not yet added — requires plan 14-06",
    strict=False,
)
async def test_platform_stats(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Stub: get_platform_stats tool should return user/site/page counts and plan breakdown.

    Full implementation: call the tool via MCP HTTP endpoint and assert response structure.
    TODO: expand after plan 14-06 is complete.
    """
    # Placeholder — fails until MCP tool exists
    pytest.fail("TODO: implement after plan 14-06 adds get_platform_stats tool")


@pytest.mark.xfail(
    reason="list_all_sites MCP tool not yet added — requires plan 14-06",
    strict=False,
)
async def test_list_all_sites(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Stub: list_all_sites tool should return cross-user site list.

    TODO: expand after plan 14-06 is complete.
    """
    pytest.fail("TODO: implement after plan 14-06 adds list_all_sites tool")


@pytest.mark.xfail(
    reason="trigger_deployment MCP tool not yet added — requires plan 14-06",
    strict=False,
)
async def test_trigger_deployment(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Stub: trigger_deployment tool should call Coolify API and return status.

    TODO: expand with httpx mock after plan 14-06 is complete.
    """
    pytest.fail("TODO: implement after plan 14-06 adds trigger_deployment tool")
