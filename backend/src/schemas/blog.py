"""Pydantic schemas for blog posts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BlogPostCreate(BaseModel):
    title: str
    slug: str | None = None  # auto-derived from title if omitted
    excerpt: str | None = None
    body: str = ""
    author_name: str | None = None
    cover_image_url: str | None = None
    tags: list[str] = []


class BlogPostUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    excerpt: str | None = None
    body: str | None = None
    author_name: str | None = None
    cover_image_url: str | None = None
    tags: list[str] | None = None


class BlogPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    site_id: UUID
    slug: str
    title: str
    excerpt: str | None
    body: str
    author_name: str | None
    cover_image_url: str | None
    tags: list[str]
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    is_published: bool


class BlogPostSummary(BaseModel):
    """Lightweight response for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    excerpt: str | None
    author_name: str | None
    cover_image_url: str | None
    tags: list[str]
    published_at: datetime | None
    created_at: datetime
    is_published: bool
