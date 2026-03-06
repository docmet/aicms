"""Blog post CRUD API.

Endpoints are mounted at /api/sites/{site_id}/posts.
All write operations require authentication + site ownership.
"""

import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.blog import BlogPost
from src.models.site import Site
from src.models.user import User
from src.schemas.blog import (
    BlogPostCreate,
    BlogPostResponse,
    BlogPostSummary,
    BlogPostUpdate,
)

router = APIRouter()


def _slugify(text: str) -> str:
    """Convert a string to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:180]


async def _get_site_or_404(
    site_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> Site:
    result = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id, ~Site.is_deleted)
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


async def _get_post_or_404(post_id: UUID, site_id: UUID, db: AsyncSession) -> BlogPost:
    result = await db.execute(
        select(BlogPost).where(BlogPost.id == post_id, BlogPost.site_id == site_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@router.post("/{site_id}/posts", response_model=BlogPostResponse, status_code=201)
async def create_post(
    site_id: UUID,
    body: BlogPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BlogPost:
    """Create a new blog post (draft)."""
    await _get_site_or_404(site_id, current_user, db)

    slug = body.slug or _slugify(body.title)

    # Ensure slug uniqueness within site
    base_slug = slug
    counter = 1
    while True:
        existing = await db.execute(
            select(BlogPost).where(BlogPost.site_id == site_id, BlogPost.slug == slug)
        )
        if not existing.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    post = BlogPost(
        id=uuid4(),
        site_id=site_id,
        slug=slug,
        title=body.title,
        excerpt=body.excerpt,
        body=body.body,
        author_name=body.author_name,
        cover_image_url=body.cover_image_url,
        tags=body.tags,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/{site_id}/posts", response_model=list[BlogPostSummary])
async def list_posts(
    site_id: UUID,
    published_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BlogPost]:
    """List all blog posts for a site (newest first)."""
    await _get_site_or_404(site_id, current_user, db)

    stmt = select(BlogPost).where(BlogPost.site_id == site_id)
    if published_only:
        stmt = stmt.where(BlogPost.published_at.isnot(None))
    stmt = stmt.order_by(BlogPost.created_at.desc())

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{site_id}/posts/{post_id}", response_model=BlogPostResponse)
async def get_post(
    site_id: UUID,
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BlogPost:
    """Get a single blog post."""
    await _get_site_or_404(site_id, current_user, db)
    return await _get_post_or_404(post_id, site_id, db)


@router.patch("/{site_id}/posts/{post_id}", response_model=BlogPostResponse)
async def update_post(
    site_id: UUID,
    post_id: UUID,
    body: BlogPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BlogPost:
    """Update a blog post."""
    await _get_site_or_404(site_id, current_user, db)
    post = await _get_post_or_404(post_id, site_id, db)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    post.updated_at = datetime.now(UTC)  # type: ignore[assignment]
    await db.commit()
    await db.refresh(post)
    return post


@router.post("/{site_id}/posts/{post_id}/publish", response_model=BlogPostResponse)
async def publish_post(
    site_id: UUID,
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BlogPost:
    """Publish a blog post (sets published_at to now)."""
    await _get_site_or_404(site_id, current_user, db)
    post = await _get_post_or_404(post_id, site_id, db)

    now = datetime.now(UTC)
    post.published_at = now  # type: ignore[assignment]
    post.updated_at = now  # type: ignore[assignment]
    await db.commit()
    await db.refresh(post)
    return post


@router.post("/{site_id}/posts/{post_id}/unpublish", response_model=BlogPostResponse)
async def unpublish_post(
    site_id: UUID,
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BlogPost:
    """Unpublish a blog post (clears published_at)."""
    await _get_site_or_404(site_id, current_user, db)
    post = await _get_post_or_404(post_id, site_id, db)

    post.published_at = None  # type: ignore[assignment]
    post.updated_at = datetime.now(UTC)  # type: ignore[assignment]
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{site_id}/posts/{post_id}", status_code=204)
async def delete_post(
    site_id: UUID,
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a blog post."""
    await _get_site_or_404(site_id, current_user, db)
    post = await _get_post_or_404(post_id, site_id, db)
    await db.delete(post)
    await db.commit()
