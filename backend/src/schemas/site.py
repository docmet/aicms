from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SiteBase(BaseModel):
    """Base site schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    theme_slug: str = Field("default", max_length=50)


class SiteCreate(SiteBase):
    """Schema for creating a new site."""

    pass


class SiteUpdate(BaseModel):
    """Schema for updating a site."""

    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    theme_slug: str | None = Field(None, max_length=50)


class SiteInDB(SiteBase):
    """Schema for site as stored in database."""

    id: UUID
    user_id: UUID
    domain: str | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteResponse(SiteInDB):
    """Schema for site response."""

    pass
