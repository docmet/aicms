from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PageBase(BaseModel):
    """Base page schema."""

    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    is_published: bool = True
    order: int = 0


class PageCreate(PageBase):
    """Schema for creating a new page."""

    pass


class PageUpdate(BaseModel):
    """Schema for updating a page."""

    title: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    is_published: bool | None = None
    order: int | None = None


class PageInDB(PageBase):
    """Schema for page as stored in database."""

    id: UUID
    site_id: UUID
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PageResponse(PageInDB):
    """Schema for page response."""

    pass
