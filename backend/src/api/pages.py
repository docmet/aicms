"""Pages CRUD API + publish / version management.

Routes mounted at /api/sites/{site_id}/pages.

Standard CRUD:
  POST   /{site_id}/pages                            — create page
  GET    /{site_id}/pages                            — list pages
  GET    /{site_id}/pages/{page_id}                  — get page
  PATCH  /{site_id}/pages/{page_id}                  — update page metadata
  DELETE /{site_id}/pages/{page_id}                  — soft delete

Publish / versioning:
  POST   /{site_id}/pages/{page_id}/publish          — publish draft (copies draft→published, creates PageVersion)
  GET    /{site_id}/pages/{page_id}/versions         — list version history (max 5)
  POST   /{site_id}/pages/{page_id}/revert/{ver_id}  — revert draft to a saved version
"""

import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.content import _broadcast_sections, _broadcast_theme
from src.database import get_db
from src.models.content import ContentSection
from src.models.page import Page
from src.models.page_version import MAX_VERSIONS_PER_PAGE, PageVersion
from src.models.site import Site
from src.models.user import User
from src.schemas.content import PageVersionResponse
from src.schemas.page import PageCreate, PageResponse, PageUpdate

router = APIRouter()


# ── Ownership helper ──────────────────────────────────────────────────────────


async def get_site_owned_by_user(
    site_id: UUID,
    current_user: User,
    db: AsyncSession,
    include_deleted: bool = False,
) -> Site:
    """Verify site ownership. Raises 404 if not found or not owned."""
    query = select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    if not include_deleted:
        query = query.where(Site.is_deleted.is_(False))
    result = await db.execute(query)
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    return site


# ── Standard CRUD ─────────────────────────────────────────────────────────────


@router.post(
    "/{site_id}/pages",
    response_model=PageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_page(
    site_id: UUID,
    page_in: PageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Create a new page for a specific site."""
    await get_site_owned_by_user(site_id, current_user, db)

    result = await db.execute(
        select(Page).where(Page.site_id == site_id, Page.slug == page_in.slug).limit(1)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page with this slug already exists in this site",
        )

    db_page = Page(**page_in.model_dump(), site_id=site_id)
    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page


@router.get("/{site_id}/pages", response_model=list[PageResponse])
async def list_pages(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False, description="Include soft-deleted pages"),
) -> list[Page]:
    """List all pages belonging to a specific site."""
    await get_site_owned_by_user(site_id, current_user, db, include_deleted)
    query = select(Page).where(Page.site_id == site_id).order_by(Page.order)
    if not include_deleted:
        query = query.where(Page.is_deleted.is_(False))
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{site_id}/pages/{page_id}", response_model=PageResponse)
async def get_page(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False),
) -> Page:
    """Get a specific page by ID."""
    await get_site_owned_by_user(site_id, current_user, db, include_deleted)
    query = select(Page).where(Page.id == page_id, Page.site_id == site_id)
    if not include_deleted:
        query = query.where(Page.is_deleted.is_(False))
    result = await db.execute(query)
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )
    return page


@router.patch("/{site_id}/pages/{page_id}", response_model=PageResponse)
async def update_page(
    site_id: UUID,
    page_id: UUID,
    page_in: PageUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Update page metadata (title, slug, order). Does not publish."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(Page.id == page_id, Page.site_id == site_id)
    )
    db_page = result.scalar_one_or_none()
    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    update_data = page_in.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != db_page.slug:
        slug_result = await db.execute(
            select(Page).where(
                Page.site_id == site_id, Page.slug == update_data["slug"]
            )
        )
        if slug_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page with this slug already exists in this site",
            )

    for field, value in update_data.items():
        setattr(db_page, field, value)

    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page


@router.delete("/{site_id}/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete a page."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(
            Page.id == page_id,
            Page.site_id == site_id,
            Page.is_deleted.is_(False),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    page.is_deleted = True  # type: ignore
    page.deleted_at = datetime.now(UTC)  # type: ignore
    db.add(page)
    await db.commit()


# ── Publish / versioning ──────────────────────────────────────────────────────


@router.post("/{site_id}/pages/{page_id}/publish", response_model=PageResponse)
async def publish_page(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Publish the current draft of a page.

    - Copies content_draft -> content_published for every active section
    - Creates a PageVersion snapshot of the full page + sections state
    - Enforces MAX_VERSIONS_PER_PAGE by deleting the oldest version on overflow
    - Sets page.is_published = True and page.last_published_at = now
    """
    site = await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(
            Page.id == page_id,
            Page.site_id == site_id,
            Page.is_deleted.is_(False),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Publish pending theme draft (site-level, applies on any page publish)
    if site.theme_slug_draft is not None:
        site.theme_slug = site.theme_slug_draft  # type: ignore
        site.theme_slug_draft = None  # type: ignore
        db.add(site)

    # Fetch all active sections
    sections_result = await db.execute(
        select(ContentSection)
        .where(
            ContentSection.page_id == page_id,
            ContentSection.is_deleted.is_(False),
        )
        .order_by(ContentSection.order)
    )
    sections = sections_result.scalars().all()

    # Copy draft → published for every section
    for section in sections:
        section.content_published = section.content_draft  # type: ignore
        db.add(section)

    # Determine next version number
    versions_result = await db.execute(
        select(PageVersion)
        .where(PageVersion.page_id == page_id)
        .order_by(PageVersion.version_number.desc())
        .limit(1)
    )
    latest_version = versions_result.scalar_one_or_none()
    next_version_number = (latest_version.version_number + 1) if latest_version else 1

    # Build snapshot JSON
    snapshot = json.dumps({
        "page": {
            "id": str(page.id),
            "title": page.title,
            "slug": page.slug,
        },
        "sections": [
            {
                "section_type": s.section_type,
                "content": s.content_draft,
                "order": s.order,
            }
            for s in sections
        ],
    })

    # Create version record
    version = PageVersion(
        id=uuid4(),
        page_id=page_id,
        version_number=next_version_number,
        snapshot=snapshot,
        published_by=current_user.id,
    )
    db.add(version)

    # Enforce MAX_VERSIONS_PER_PAGE: delete oldest version(s) on overflow
    all_versions_result = await db.execute(
        select(PageVersion)
        .where(PageVersion.page_id == page_id)
        .order_by(PageVersion.version_number.asc())
    )
    all_versions = all_versions_result.scalars().all()
    # +1 because we added a new version above (not yet flushed)
    excess = len(all_versions) + 1 - MAX_VERSIONS_PER_PAGE
    if excess > 0:
        for old_version in all_versions[:excess]:
            await db.delete(old_version)

    # Mark page as published
    page.is_published = True  # type: ignore
    page.last_published_at = datetime.now(UTC)  # type: ignore
    db.add(page)

    await db.commit()
    await db.refresh(page)

    # Broadcast updated sections (all has_unpublished_changes now False) and
    # cleared theme draft so the admin editor and preview update instantly.
    await _broadcast_sections(page_id, db)
    await _broadcast_theme(
        site_id,
        None,  # theme_slug_draft is cleared on publish
        str(site.theme_slug) if site.theme_slug else None,
        db,
    )

    return page


@router.get(
    "/{site_id}/pages/{page_id}/versions",
    response_model=list[PageVersionResponse],
)
async def list_page_versions(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PageVersion]:
    """List published versions for a page (newest first, max 5)."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(PageVersion)
        .where(PageVersion.page_id == page_id)
        .order_by(PageVersion.version_number.desc())
        .limit(MAX_VERSIONS_PER_PAGE)
    )
    return list(result.scalars().all())


@router.post(
    "/{site_id}/pages/{page_id}/revert/{version_id}",
    response_model=PageResponse,
)
async def revert_page_to_version(
    site_id: UUID,
    page_id: UUID,
    version_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Revert page draft to a saved version.

    Loads the snapshot from the specified PageVersion and copies each section's
    content back into content_draft. The page is NOT automatically published —
    the user/AI still needs to call /publish to make the reverted content live.
    Sections in the snapshot that no longer exist are re-created.
    """
    await get_site_owned_by_user(site_id, current_user, db)

    # Load page
    page_result = await db.execute(
        select(Page).where(
            Page.id == page_id,
            Page.site_id == site_id,
            Page.is_deleted.is_(False),
        )
    )
    page = page_result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Load version
    version_result = await db.execute(
        select(PageVersion).where(
            PageVersion.id == version_id,
            PageVersion.page_id == page_id,
        )
    )
    version = version_result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    snapshot = json.loads(str(version.snapshot))
    snapshot_sections = snapshot.get("sections", [])

    # For each section in snapshot, upsert into content_draft
    for snap_sec in snapshot_sections:
        section_type = snap_sec["section_type"]
        content = snap_sec.get("content")
        order = snap_sec.get("order", 0)

        existing_result = await db.execute(
            select(ContentSection).where(
                ContentSection.page_id == page_id,
                ContentSection.section_type == section_type,
                ContentSection.is_deleted.is_(False),
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.content_draft = content  # type: ignore
            existing.order = order  # type: ignore
            db.add(existing)
        else:
            new_section = ContentSection(
                id=uuid4(),
                page_id=page_id,
                section_type=section_type,
                content_draft=content,
                order=order,
            )
            db.add(new_section)

    await db.commit()
    await db.refresh(page)

    # Broadcast the reverted sections so admin editor and preview update instantly.
    await _broadcast_sections(page_id, db)

    return page
