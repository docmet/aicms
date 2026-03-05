"""Pydantic schemas for page content sections.

Each section type has its own typed schema. content_draft and content_published
store JSON strings that conform to these schemas. The SECTION_SCHEMAS dict maps
section_type strings to their Pydantic models for validation.

Section types:
  hero         — Full-bleed hero with headline, CTA buttons, optional badge
  features     — Icon grid of features / services
  testimonials — Quote cards from customers
  about        — Two-column: text + optional stats row
  contact      — Contact details (email, phone, address, hours)
  cta          — Full-width call-to-action banner
  pricing      — Pricing plan cards
  custom       — Free-form fallback for any other content
"""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ── Per-section content models ────────────────────────────────────────────────

class CtaButton(BaseModel):
    label: str
    href: str | None = None


class HeroContent(BaseModel):
    """Full-bleed hero section."""

    headline: str
    subheadline: str | None = None
    badge: str | None = None  # Small tag above headline, e.g. "Now in beta"
    cta_primary: CtaButton | None = None
    cta_secondary: CtaButton | None = None


class FeatureItem(BaseModel):
    icon: str | None = None  # Emoji or lucide icon name
    title: str
    description: str | None = None


class FeaturesContent(BaseModel):
    """Icon grid of features or services."""

    headline: str | None = None
    subheadline: str | None = None
    items: list[FeatureItem] = []


class TestimonialItem(BaseModel):
    quote: str
    name: str
    role: str | None = None
    company: str | None = None


class TestimonialsContent(BaseModel):
    """Customer testimonials / social proof."""

    headline: str | None = None
    items: list[TestimonialItem] = []


class StatItem(BaseModel):
    number: str  # String for flexibility, e.g. "500+", "4.9★"
    label: str


class AboutContent(BaseModel):
    """About section: text + optional stats."""

    headline: str
    body: str
    stats: list[StatItem] | None = None


class ContactContent(BaseModel):
    """Contact details."""

    headline: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    hours: str | None = None


class CtaContent(BaseModel):
    """Full-width call-to-action banner."""

    headline: str
    subheadline: str | None = None
    button_label: str
    button_href: str | None = None


class PricingPlan(BaseModel):
    name: str
    price: str               # e.g. "$29", "Free", "Contact us"
    period: str | None = None  # e.g. "/month"
    features: list[str] = []
    cta_label: str = "Get started"
    cta_href: str | None = None
    highlighted: bool = False  # True for the recommended/middle plan


class PricingContent(BaseModel):
    """Pricing plans."""

    headline: str | None = None
    subheadline: str | None = None
    plans: list[PricingPlan] = []


class CustomContent(BaseModel):
    """Free-form section for unstructured content."""

    title: str | None = None
    content: str | None = None  # Plain text; HTML is stripped before storage


# Map section_type -> content schema for validation
SECTION_SCHEMAS: dict[str, type[BaseModel]] = {
    "hero": HeroContent,
    "features": FeaturesContent,
    "testimonials": TestimonialsContent,
    "about": AboutContent,
    "contact": ContactContent,
    "cta": CtaContent,
    "pricing": PricingContent,
    "custom": CustomContent,
}


def parse_section_content(section_type: str, content_json: str | None) -> dict[str, Any]:
    """Parse content JSON and validate against the section type schema.

    Returns a dict. Falls back to raw parsed JSON if the schema does not match
    (lenient for AI edits that may produce partial content).
    Returns {} for null/empty input.
    """
    if not content_json:
        return {}
    try:
        data = json.loads(content_json)
    except json.JSONDecodeError:
        return {}
    schema = SECTION_SCHEMAS.get(section_type)
    if schema:
        try:
            return schema(**data).model_dump()
        except Exception:
            return dict(data)  # Return raw if validation fails
    return dict(data)


# ── API request/response schemas ──────────────────────────────────────────────


class ContentSectionCreate(BaseModel):
    """Schema for creating a new content section."""

    section_type: str = Field(..., min_length=1, max_length=50)
    content_draft: str | None = None  # JSON string
    order: int = 0


class ContentSectionUpdate(BaseModel):
    """Schema for partially updating a content section (all fields optional)."""

    section_type: str | None = Field(None, min_length=1, max_length=50)
    content_draft: str | None = None  # Updates draft only; published unchanged
    order: int | None = None


class ContentSectionUpsert(BaseModel):
    """Upsert-by-section-type: create or update draft content for a section.

    Primary write path for MCP tools. section_type is in the URL.
    Creates the section if it does not exist, otherwise updates content_draft.
    After saving, broadcast SSE to connected preview clients.
    """

    content_draft: str  # JSON string matching the section type schema
    order: int | None = None


class ContentSectionResponse(BaseModel):
    """Schema for content section API response."""

    id: UUID
    page_id: UUID
    section_type: str
    content_draft: str | None = None
    content_published: str | None = None
    has_unpublished_changes: bool
    order: int
    is_deleted: bool
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── PageVersion schemas ───────────────────────────────────────────────────────


class PageVersionResponse(BaseModel):
    """Schema for a published page version."""

    id: UUID
    page_id: UUID
    version_number: int
    snapshot: str  # JSON snapshot of page + sections state at publish time
    published_at: datetime
    published_by: UUID | None = None
    label: str | None = None

    model_config = ConfigDict(from_attributes=True)
