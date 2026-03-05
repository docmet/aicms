from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContentSectionBase(BaseModel):
    """Base content section schema."""

    section_type: str = Field(..., min_length=1, max_length=50)
    content: str | None = None
    order: int = 0


class ContentSectionCreate(ContentSectionBase):
    """Schema for creating a new content section."""

    pass


class ContentSectionUpdate(BaseModel):
    """Schema for updating a content section."""

    section_type: str | None = Field(None, min_length=1, max_length=50)
    content: str | None = None
    order: int | None = None


class ContentSectionInDB(ContentSectionBase):
    """Schema for content section as stored in database."""

    id: UUID
    page_id: UUID
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentSectionResponse(ContentSectionInDB):
    """Schema for content section response."""

    pass
