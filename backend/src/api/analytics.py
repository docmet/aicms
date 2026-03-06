"""Analytics API.

Public (no auth):
  POST /api/public/sites/{site_slug}/pageview  — record a pageview

Owner (auth required):
  GET  /api/sites/{site_id}/analytics          — aggregated stats (last N days)
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.analytics import PageView
from src.models.site import Site
from src.models.user import User

public_router = APIRouter()
private_router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────

class PageViewIn(BaseModel):
    page_path: str
    referrer: str | None = None


class PageStatsRow(BaseModel):
    page_path: str
    views: int


class ReferrerRow(BaseModel):
    referrer: str
    views: int


class DailyRow(BaseModel):
    date: str
    views: int


class AnalyticsResponse(BaseModel):
    total_views: int
    unique_pages: int
    top_pages: list[PageStatsRow]
    top_referrers: list[ReferrerRow]
    daily: list[DailyRow]
    days: int


# ── Public: record pageview ────────────────────────────────────────────────────

@public_router.post("/{site_slug}/pageview", status_code=204)
async def record_pageview(
    site_slug: str,
    body: PageViewIn,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Record a pageview — no cookies, no PII stored. Fire-and-forget."""
    result = await db.execute(
        select(Site).where(Site.slug == site_slug, Site.is_deleted.is_(False))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    pv = PageView(
        id=uuid4(),
        site_id=site.id,
        page_path=body.page_path[:500],
        referrer=(body.referrer or "")[:500] or None,
    )
    db.add(pv)
    await db.commit()


# ── Private: analytics dashboard ──────────────────────────────────────────────

async def _get_owned_site(site_id: UUID, current_user: User, db: AsyncSession) -> Site:
    result = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id, Site.is_deleted.is_(False))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@private_router.get("/{site_id}/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    site_id: UUID,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    """Return aggregated analytics for a site."""
    await _get_owned_site(site_id, current_user, db)

    since = datetime.now(UTC) - timedelta(days=days)

    # Total views
    total_res = await db.execute(
        select(func.count()).where(PageView.site_id == site_id, PageView.created_at >= since)
    )
    total_views: int = total_res.scalar_one() or 0

    # Unique pages
    unique_res = await db.execute(
        select(func.count(func.distinct(PageView.page_path))).where(
            PageView.site_id == site_id, PageView.created_at >= since
        )
    )
    unique_pages: int = unique_res.scalar_one() or 0

    # Top pages
    top_pages_res = await db.execute(
        select(PageView.page_path, func.count().label("views"))
        .where(PageView.site_id == site_id, PageView.created_at >= since)
        .group_by(PageView.page_path)
        .order_by(text("views DESC"))
        .limit(10)
    )
    top_pages = [PageStatsRow(page_path=r[0], views=r[1]) for r in top_pages_res.all()]

    # Top referrers (exclude null/empty)
    top_ref_res = await db.execute(
        select(PageView.referrer, func.count().label("views"))
        .where(
            PageView.site_id == site_id,
            PageView.created_at >= since,
            PageView.referrer.isnot(None),
        )
        .group_by(PageView.referrer)
        .order_by(text("views DESC"))
        .limit(10)
    )
    top_referrers = [ReferrerRow(referrer=r[0], views=r[1]) for r in top_ref_res.all()]

    # Daily views (last N days)
    daily_res = await db.execute(
        select(
            func.date_trunc("day", PageView.created_at).label("day"),
            func.count().label("views"),
        )
        .where(PageView.site_id == site_id, PageView.created_at >= since)
        .group_by(text("day"))
        .order_by(text("day ASC"))
    )
    daily = [
        DailyRow(date=r[0].strftime("%Y-%m-%d"), views=r[1])
        for r in daily_res.all()
    ]

    return AnalyticsResponse(
        total_views=total_views,
        unique_pages=unique_pages,
        top_pages=top_pages,
        top_referrers=top_referrers,
        daily=daily,
        days=days,
    )
