from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.site import Site
from src.models.user import User
from src.services.auth import AuthService


@pytest.mark.asyncio
async def test_multi_user_site_isolation(client: AsyncClient, db: AsyncSession) -> None:
    """Test that users cannot access or modify each other's sites."""
    # Create two users
    u1_password = "password123"
    u1 = User(
        id=uuid4(),
        email="user1@example.com",
        password_hash=AuthService.get_password_hash(u1_password),
    )
    u2_password = "password123"
    u2 = User(
        id=uuid4(),
        email="user2@example.com",
        password_hash=AuthService.get_password_hash(u2_password),
    )
    db.add_all([u1, u2])
    await db.commit()

    # Create a site for user 1
    site1 = Site(id=uuid4(), user_id=u1.id, name="User 1 Site", slug="user1-site")
    db.add(site1)
    await db.commit()

    # Get token for user 2
    response = await client.post(
        "/api/auth/login",
        data={"username": "user2@example.com", "password": u2_password},
    )
    u2_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {u2_token}"}

    # User 2 tries to GET User 1's site
    response = await client.get(f"/api/sites/{site1.id}", headers=headers)
    assert response.status_code == 404

    # User 2 tries to UPDATE User 1's site
    response = await client.patch(
        f"/api/sites/{site1.id}", headers=headers, json={"name": "Hacked Site"}
    )
    assert response.status_code == 404

    # User 2 tries to DELETE User 1's site
    response = await client.delete(f"/api/sites/{site1.id}", headers=headers)
    assert response.status_code == 404

    # User 2 lists sites (should not see site 1)
    response = await client.get("/api/sites/", headers=headers)
    assert response.status_code == 200
    sites = response.json()
    assert len(sites) == 0
    assert all(s["id"] != str(site1.id) for s in sites)
