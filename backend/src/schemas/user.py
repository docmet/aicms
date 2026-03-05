from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.user import UserPlan


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    password: str | None = None


class UserInDB(UserBase):
    """Schema for user as stored in database."""

    id: UUID
    is_admin: bool
    plan: UserPlan
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Schema for user response."""

    pass


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for data stored in token."""

    email: str | None = None
    id: str | None = None
