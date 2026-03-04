from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ThemeBase(BaseModel):
    """Base theme schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=50, pattern="^[a-z0-9-]+$")
    config: dict | None = None
    is_active: bool = True


class ThemeResponse(ThemeBase):
    """Schema for theme response."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)
