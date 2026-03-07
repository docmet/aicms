"""Pydantic schemas for WordPress site integration."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class WordPressSiteCreate(BaseModel):
    """Schema for registering a new WordPress site."""

    site_url: HttpUrl
    app_username: str
    app_password: str


class WordPressSiteResponse(BaseModel):
    """Schema returned to clients — never includes app_password_encrypted."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    site_url: str
    site_name: str | None
    mcp_token: str
    is_active: bool
    created_at: datetime


class WordPressSiteUpdate(BaseModel):
    """Schema for updating a WordPress site registration."""

    site_url: str | None = None
    app_username: str | None = None
    app_password: str | None = None
    is_active: bool | None = None
