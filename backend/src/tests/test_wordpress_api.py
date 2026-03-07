"""Tests for WordPress site registration API (plan 15-01).

Tests POST, GET, and DELETE on /api/wordpress/sites using a mocked
WordPressClient so no real WP site is needed.
"""

from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.auth import AuthService


async def _create_user_and_login(
    db: AsyncSession, client: AsyncClient, email: str = "wptest@example.com"
) -> str:
    """Helper: create a user, log in, return Bearer token."""
    password = "password123"
    hashed = AuthService.get_password_hash(password)
    user = User(email=email, password_hash=hashed)
    db.add(user)
    await db.commit()

    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]  # type: ignore[no-any-return]


FAKE_WP_INFO = {"name": "My WP Site", "description": "A test site", "url": "https://example.com"}


async def test_register_wordpress_site(client: AsyncClient, db: AsyncSession) -> None:
    """POST /api/wordpress/sites should register site and return mcp_token."""
    token = await _create_user_and_login(db, client, "wptest1@example.com")

    with patch(
        "src.api.wordpress.WordPressClient.get_site_info",
        new_callable=AsyncMock,
        return_value=FAKE_WP_INFO,
    ):
        response = await client.post(
            "/api/wordpress/sites",
            json={
                "site_url": "https://example.com",
                "app_username": "admin",
                "app_password": "abcd efgh ijkl mnop",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201, response.text
    data = response.json()
    assert "mcp_token" in data
    assert len(data["mcp_token"]) > 20
    assert data["site_name"] == "My WP Site"
    assert data["site_url"] == "https://example.com"
    assert data["is_active"] is True
    # Password must never appear in the response
    assert "app_password" not in data
    assert "app_password_encrypted" not in data


async def test_register_wordpress_site_bad_credentials(client: AsyncClient, db: AsyncSession) -> None:
    """POST /api/wordpress/sites with unreachable WP returns 400."""
    token = await _create_user_and_login(db, client, "wptest2@example.com")

    with patch(
        "src.api.wordpress.WordPressClient.get_site_info",
        new_callable=AsyncMock,
        side_effect=Exception("connection refused"),
    ):
        response = await client.post(
            "/api/wordpress/sites",
            json={
                "site_url": "https://bad-wp.example.com",
                "app_username": "admin",
                "app_password": "wrong",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 400, response.text
    assert "Cannot connect" in response.json()["detail"]


async def test_list_wordpress_sites(client: AsyncClient, db: AsyncSession) -> None:
    """GET /api/wordpress/sites returns list of registered sites."""
    token = await _create_user_and_login(db, client, "wptest3@example.com")

    # Register a site first
    with patch(
        "src.api.wordpress.WordPressClient.get_site_info",
        new_callable=AsyncMock,
        return_value=FAKE_WP_INFO,
    ):
        reg = await client.post(
            "/api/wordpress/sites",
            json={
                "site_url": "https://list-test.example.com",
                "app_username": "admin",
                "app_password": "secret",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert reg.status_code == 201, reg.text

    response = await client.get(
        "/api/wordpress/sites",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["site_url"] == "https://list-test.example.com" for s in data)


async def test_delete_wordpress_site_sets_inactive(client: AsyncClient, db: AsyncSession) -> None:
    """DELETE /api/wordpress/sites/{id} sets is_active=False (soft delete)."""
    token = await _create_user_and_login(db, client, "wptest4@example.com")

    with patch(
        "src.api.wordpress.WordPressClient.get_site_info",
        new_callable=AsyncMock,
        return_value=FAKE_WP_INFO,
    ):
        reg = await client.post(
            "/api/wordpress/sites",
            json={
                "site_url": "https://delete-test.example.com",
                "app_username": "admin",
                "app_password": "secret",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert reg.status_code == 201, reg.text
    site_id = reg.json()["id"]

    delete_response = await client.delete(
        f"/api/wordpress/sites/{site_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204, delete_response.text

    # Verify the site appears inactive in list (still returned since we return all sites)
    list_response = await client.get(
        "/api/wordpress/sites",
        headers={"Authorization": f"Bearer {token}"},
    )
    sites = list_response.json()
    deleted = next((s for s in sites if s["id"] == site_id), None)
    assert deleted is not None
    assert deleted["is_active"] is False
