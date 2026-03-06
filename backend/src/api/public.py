"""Public site API — no authentication required.

GET /api/public/sites/{site_slug}
  Returns site metadata + all published pages (for nav) + sections of the
  first published page (homepage). content_published only; drafts never exposed.

GET /api/public/sites/{site_slug}/pages/{page_slug}
  Returns sections for a specific published page by slug.

Both return 404 if site/page not found or not published.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.blog import BlogPost
from src.models.content import ContentSection
from src.models.page import Page
from src.models.site import Site
from src.models.user import User, UserPlan

router = APIRouter()


def _sections_payload(sections: list[ContentSection]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(s.id),
            "section_type": s.section_type,
            "content": s.content_published,
        }
        for s in sections
    ]


async def _get_site_or_404(site_slug: str, db: AsyncSession) -> Site:
    result = await db.execute(
        select(Site).where(Site.slug == site_slug, Site.is_deleted.is_(False))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


async def _site_shows_badge(site: Site, db: AsyncSession) -> bool:
    """Returns True if the site owner is on the free plan (badge required)."""
    result = await db.execute(select(User).where(User.id == site.user_id))
    owner = result.scalar_one_or_none()
    if not owner:
        return True
    return str(owner.plan) == UserPlan.free


async def _get_published_pages(site: Site, db: AsyncSession) -> list[Page]:
    result = await db.execute(
        select(Page)
        .where(Page.site_id == site.id, Page.is_published, Page.is_deleted.is_(False))
        .order_by(Page.order)
    )
    return list(result.scalars().all())


async def _get_page_sections(page: Page, db: AsyncSession) -> list[ContentSection]:
    result = await db.execute(
        select(ContentSection)
        .where(
            ContentSection.page_id == page.id,
            ContentSection.is_deleted.is_(False),
            ContentSection.content_published.isnot(None),
        )
        .order_by(ContentSection.order)
    )
    return list(result.scalars().all())


def _nav_pages(pages: list[Page]) -> list[dict[str, str]]:
    return [{"title": str(p.title), "slug": str(p.slug)} for p in pages]


@router.get("/{site_slug}", response_model=dict[str, Any])
async def get_public_site(
    site_slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Returns site info + all published pages (for nav) + homepage sections."""
    site = await _get_site_or_404(site_slug, db)
    pages = await _get_published_pages(site, db)
    show_badge = await _site_shows_badge(site, db)

    if not pages:
        return {
            "name": site.name,
            "theme_slug": site.theme_slug,
            "pages": [],
            "page_title": None,
            "page_slug": None,
            "sections": [],
            "show_badge": show_badge,
        }

    homepage = pages[0]
    sections = await _get_page_sections(homepage, db)

    return {
        "name": site.name,
        "theme_slug": site.theme_slug,
        "pages": _nav_pages(pages),
        "page_title": homepage.title,
        "page_slug": homepage.slug,
        "sections": _sections_payload(sections),
        "show_badge": show_badge,
    }


@router.get("/{site_slug}/pages/{page_slug}", response_model=dict[str, Any])
async def get_public_site_page(
    site_slug: str,
    page_slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Returns sections for a specific published page."""
    site = await _get_site_or_404(site_slug, db)

    page_result = await db.execute(
        select(Page).where(
            Page.site_id == site.id,
            Page.slug == page_slug,
            Page.is_published,
            Page.is_deleted.is_(False),
        )
    )
    page = page_result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    pages = await _get_published_pages(site, db)
    sections = await _get_page_sections(page, db)
    show_badge = await _site_shows_badge(site, db)

    return {
        "name": site.name,
        "theme_slug": site.theme_slug,
        "pages": _nav_pages(pages),
        "page_title": page.title,
        "page_slug": page.slug,
        "sections": _sections_payload(sections),
        "show_badge": show_badge,
    }


# ── Public blog endpoints (no auth, published-only) ──────────────────────────

def _post_summary(post: BlogPost) -> dict[str, Any]:
    return {
        "id": str(post.id),
        "slug": post.slug,
        "title": post.title,
        "excerpt": post.excerpt,
        "author_name": post.author_name,
        "cover_image_url": post.cover_image_url,
        "tags": post.tags or [],
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


@router.get("/{site_slug}/blog", response_model=list[dict[str, Any]])
async def get_public_blog_index(
    site_slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all published blog posts for a site (newest first)."""
    site = await _get_site_or_404(site_slug, db)

    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.site_id == site.id, BlogPost.published_at.isnot(None))
        .order_by(BlogPost.published_at.desc())
    )
    posts = list(result.scalars().all())
    return [_post_summary(p) for p in posts]


@router.get("/{site_slug}/blog/{slug}", response_model=dict[str, Any])
async def get_public_blog_post(
    site_slug: str,
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a single published blog post by slug."""
    site = await _get_site_or_404(site_slug, db)

    result = await db.execute(
        select(BlogPost).where(
            BlogPost.site_id == site.id,
            BlogPost.slug == slug,
            BlogPost.published_at.isnot(None),
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        **_post_summary(post),
        "body": post.body,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }
