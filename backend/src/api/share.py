"""Shareable preview links API.

Owner (auth required):
  POST /api/sites/{site_id}/share   — create a 24h preview link

Public (no auth):
  GET  /api/share/{token}           — fetch draft page content if not expired
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.content import ContentSection
from src.models.page import Page
from src.models.share_preview import SharePreview
from src.models.site import Site
from src.models.user import User

private_router = APIRouter()
public_router = APIRouter()

PREVIEW_TTL_HOURS = 24


class ShareCreateRequest(BaseModel):
    page_id: str | None = None
    ttl_hours: int = PREVIEW_TTL_HOURS


class ShareResponse(BaseModel):
    token: str
    expires_at: datetime
    url: str


async def _get_owned_site(site_id: UUID, current_user: User, db: AsyncSession) -> Site:
    result = await db.execute(
        select(Site).where(
            Site.id == site_id, Site.user_id == current_user.id, Site.is_deleted.is_(False)
        )
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@private_router.post("/{site_id}/share", response_model=ShareResponse)
async def create_share_link(
    site_id: UUID,
    body: ShareCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShareResponse:
    """Generate a token-protected shareable preview link (default 24h expiry)."""
    site = await _get_owned_site(site_id, current_user, db)

    page_uuid: UUID | None = None
    if body.page_id:
        page_uuid = UUID(body.page_id)
        pg_result = await db.execute(
            select(Page).where(Page.id == page_uuid, Page.site_id == site_id)
        )
        if not pg_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Page not found")

    ttl = max(1, min(body.ttl_hours, 168))  # 1h–7 days
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(hours=ttl)

    sp = SharePreview(
        id=uuid4(),
        token=token,
        site_id=site.id,
        page_id=page_uuid,
        expires_at=expires_at,
    )
    db.add(sp)
    await db.commit()

    return ShareResponse(
        token=token,
        expires_at=expires_at,
        url=f"/share/{token}",
    )


@public_router.get("/{token}", response_model=dict[str, Any])
async def get_share_preview(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return draft page content for a valid, non-expired share token."""
    result = await db.execute(
        select(SharePreview).where(SharePreview.token == token)
    )
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Preview link not found")

    expires = sp.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if datetime.now(UTC) > expires:
        raise HTTPException(status_code=410, detail="Preview link has expired")

    site_result = await db.execute(
        select(Site).where(Site.id == sp.site_id, Site.is_deleted.is_(False))
    )
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Find the page to preview
    page: Page | None = None
    if sp.page_id:
        pg_result = await db.execute(
            select(Page).where(Page.id == sp.page_id, Page.is_deleted.is_(False))
        )
        page = pg_result.scalar_one_or_none()

    if not page:
        # Fall back to first page
        pg_result = await db.execute(
            select(Page)
            .where(Page.site_id == site.id, Page.is_deleted.is_(False))
            .order_by(Page.order)
            .limit(1)
        )
        page = pg_result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="No page found")

    # Get ALL pages for nav
    all_pages_result = await db.execute(
        select(Page)
        .where(Page.site_id == site.id, Page.is_deleted.is_(False))
        .order_by(Page.order)
    )
    all_pages = all_pages_result.scalars().all()

    # Get draft sections (share previews show drafts)
    sections_result = await db.execute(
        select(ContentSection)
        .where(
            ContentSection.page_id == page.id,
            ContentSection.is_deleted.is_(False),
        )
        .order_by(ContentSection.order)
    )
    sections = sections_result.scalars().all()

    return {
        "name": site.name,
        "theme_slug": site.theme_slug_draft or site.theme_slug,
        "pages": [{"title": str(p.title), "slug": str(p.slug)} for p in all_pages],
        "page_title": page.title,
        "page_slug": page.slug,
        "sections": [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "content": s.content_draft,
            }
            for s in sections
            if s.content_draft
        ],
        "show_badge": False,
        "_preview": True,
        "_expires_at": str(sp.expires_at),
    }
