import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.auth import AuthService


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db: AsyncSession) -> None:
    """Test user registration endpoint."""
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db: AsyncSession) -> None:
    """Test user login endpoint."""
    # Create a user first
    password = "password123"
    hashed_password = AuthService.get_password_hash(password)
    user = User(email="login@example.com", password_hash=hashed_password)
    db.add(user)
    await db.commit()

    response = await client.post(
        "/api/auth/login",
        data={"username": "login@example.com", "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
