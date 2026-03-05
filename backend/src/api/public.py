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
    """Get public site data by slug."""
    # Find site by slug (only non-deleted)
    result = await db.execute(
        select(Site).where(Site.slug == site_slug, Site.is_deleted == False)
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(
            status_code=404,
            detail="Site not found",
        )

    # Get the first published page (landing page, only non-deleted)
    page_result = await db.execute(
        select(Page)
        .where(Page.site_id == site.id, Page.is_published, Page.is_deleted == False)
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

    # Get sections for this page (only non-deleted)
    sections_result = await db.execute(
        select(ContentSection)
        .where(ContentSection.page_id == page.id, ContentSection.is_deleted == False)
        .order_by(ContentSection.order)
    )
    sections = sections_result.scalars().all()

    return {
        "name": site.name,
        "theme_slug": site.theme_slug,
        "sections": [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "content": s.content,
            }
            for s in sections
        ],
    }
