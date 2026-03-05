"""Public site API — no authentication required.

GET /api/public/sites/{site_slug}
  Returns the published content for the site's landing page.
  Only content_published is served here; drafts are never exposed publicly.
  Returns 404 if site not found; returns empty sections array if no published page exists.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.content import ContentSection
from src.models.page import Page
from src.models.site import Site

router = APIRouter()


@router.get("/{site_slug}", response_model=dict[str, Any])
async def get_public_site(
    site_slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get published site data by slug. Serves content_published only."""
    result = await db.execute(
        select(Site).where(Site.slug == site_slug, Site.is_deleted.is_(False))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Get the first published page (lowest order)
    page_result = await db.execute(
        select(Page)
        .where(Page.site_id == site.id, Page.is_published, Page.is_deleted.is_(False))
        .order_by(Page.order)
        .limit(1)
    )
    page = page_result.scalar_one_or_none()
    if not page:
        return {
            "name": site.name,
            "theme_slug": site.theme_slug,
            "sections": [],
        }

    # Serve only non-deleted sections that have published content
    sections_result = await db.execute(
        select(ContentSection)
        .where(
            ContentSection.page_id == page.id,
            ContentSection.is_deleted.is_(False),
            ContentSection.content_published.isnot(None),
        )
        .order_by(ContentSection.order)
    )
    sections = sections_result.scalars().all()

    return {
        "name": site.name,
        "theme_slug": site.theme_slug,
        "page_title": page.title,
        "sections": [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "content": s.content_published,  # Always serve published content
            }
            for s in sections
        ],
    }
