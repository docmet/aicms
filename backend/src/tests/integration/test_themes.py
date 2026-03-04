from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.theme import Theme
from src.models.user import User
from src.services.auth import AuthService


@pytest.mark.asyncio
async def test_theme_listing_and_switching(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Test that themes can be listed and a site's theme can be switched."""
    # 1. Create a user and login
    password = "password123"
    user = User(
        id=uuid4(),
        email="themeuser@example.com",
        password_hash=AuthService.get_password_hash(password),
    )
    db.add(user)
    await db.commit()

    response = await client.post(
        "/api/auth/login",
        data={"username": "themeuser@example.com", "password": password},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed some themes
    t1 = Theme(id=uuid4(), name="Theme 1", slug="theme1", is_active=True)
    t2 = Theme(id=uuid4(), name="Theme 2", slug="theme2", is_active=True)
    t3 = Theme(id=uuid4(), name="Inactive Theme", slug="inactive", is_active=False)
    db.add_all([t1, t2, t3])
    await db.commit()

    # 3. List themes
    response = await client.get("/api/themes/", headers=headers)
    assert response.status_code == 200
    themes = response.json()
    assert len(themes) == 2
    slugs = [t["slug"] for t in themes]
    assert "theme1" in slugs
    assert "theme2" in slugs
    assert "inactive" not in slugs

    # 4. Create a site with default theme
    response = await client.post(
        "/api/sites/",
        headers=headers,
        json={"name": "Theme Test Site", "slug": "theme-test", "theme_slug": "theme1"},
    )
    assert response.status_code == 201
    site_id = response.json()["id"]
    assert response.json()["theme_slug"] == "theme1"

    # 5. Switch theme to theme2
    response = await client.patch(
        f"/api/sites/{site_id}", headers=headers, json={"theme_slug": "theme2"}
    )
    assert response.status_code == 200
    assert response.json()["theme_slug"] == "theme2"

    # 6. Verify public site reflects the new theme
    response = await client.get("/api/public/sites/theme-test")
    assert response.status_code == 200
    assert response.json()["theme_slug"] == "theme2"
