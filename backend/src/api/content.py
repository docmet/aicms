"""Content section CRUD API.

Routes are mounted at /api/sites/{site_id}/pages/{page_id}/content.

Key endpoints:
  POST   /content                          — create a new section
  GET    /content                          — list sections (draft view)
  GET    /content/{content_id}             — get one section
  PATCH  /content/{content_id}             — update section (draft only)
  DELETE /content/{content_id}             — soft delete
  PUT    /content/by-type/{section_type}   — upsert by type (MCP primary path)
  POST   /content/reorder                  — set absolute order of all sections

After any draft update the backend broadcasts an SSE event to all preview
clients connected to this page so the preview iframe updates sub-second.
"""

import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.content import ContentSection
from src.models.page import Page
from src.models.site import Site
from src.models.user import User
from src.schemas.content import (
    ContentSectionCreate,
    ContentSectionResponse,
    ContentSectionUpdate,
    ContentSectionUpsert,
)
from src.services.preview import preview_manager

router = APIRouter()


# ── Ownership helper ──────────────────────────────────────────────────────────


async def get_page_owned_by_user(
    site_id: UUID,
    page_id: UUID,
    current_user: User,
    db: AsyncSession,
    include_deleted: bool = False,
) -> Page:
    """Verify page ownership via site. Raises 404 if not found or not owned."""
    query = (
        select(Page)
        .join(Site)
        .where(
            Page.id == page_id,
            Page.site_id == site_id,
            Site.user_id == current_user.id,
        )
    )
    if not include_deleted:
        query = query.where(Page.is_deleted.is_(False))
    result = await db.execute(query)
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or not owned by user",
        )
    return page


async def _broadcast_theme(site_id: UUID, theme_slug_draft: str | None, theme_slug: str | None, db: AsyncSession) -> None:
    """Broadcast a theme change to SSE clients on every page of the site."""
    pages_result = await db.execute(
        select(Page).where(Page.site_id == site_id, Page.is_deleted.is_(False))
    )
    pages = pages_result.scalars().all()
    payload = json.dumps({
        "type": "theme_updated",
        "site_id": str(site_id),
        "theme_slug_draft": theme_slug_draft,
        "theme_slug": theme_slug,
    })
    for page in pages:
        await preview_manager.broadcast(UUID(str(page.id)), payload)


async def _broadcast_sections(page_id: UUID, db: AsyncSession) -> None:
    """Fetch all active sections and broadcast to SSE preview clients."""
    sections_result = await db.execute(
        select(ContentSection)
        .where(
            ContentSection.page_id == page_id,
            ContentSection.is_deleted.is_(False),
        )
        .order_by(ContentSection.order)
    )
    sections = sections_result.scalars().all()
    payload = json.dumps({
        "type": "sections_updated",
        "page_id": str(page_id),
        "sections": [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "content_draft": s.content_draft,
                "order": s.order,
                "has_unpublished_changes": s.has_unpublished_changes,
            }
            for s in sections
        ],
    })
    await preview_manager.broadcast(page_id, payload)


# ── CRUD endpoints ────────────────────────────────────────────────────────────


@router.post(
    "/{site_id}/pages/{page_id}/content",
    response_model=ContentSectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_content_section(
    site_id: UUID,
    page_id: UUID,
    content_in: ContentSectionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContentSection:
    """Create a new content section for a specific page."""
    await get_page_owned_by_user(site_id, page_id, current_user, db)

    db_content = ContentSection(
        page_id=page_id,
        section_type=content_in.section_type,
        content_draft=content_in.content_draft,
        order=content_in.order,
    )
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    await _broadcast_sections(page_id, db)
    return db_content


@router.get(
    "/{site_id}/pages/{page_id}/content",
    response_model=list[ContentSectionResponse],
)
async def list_content_sections(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False, description="Include soft-deleted sections"),
) -> list[ContentSection]:
    """List all content sections for a specific page (draft view)."""
    await get_page_owned_by_user(site_id, page_id, current_user, db, include_deleted)
    query = (
        select(ContentSection)
        .where(ContentSection.page_id == page_id)
        .order_by(ContentSection.order)
    )
    if not include_deleted:
        query = query.where(ContentSection.is_deleted.is_(False))
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{site_id}/pages/{page_id}/content/{content_id}",
    response_model=ContentSectionResponse,
)
async def get_content_section(
    site_id: UUID,
    page_id: UUID,
    content_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False),
) -> ContentSection:
    """Get a specific content section by ID."""
    await get_page_owned_by_user(site_id, page_id, current_user, db, include_deleted)
    query = select(ContentSection).where(
        ContentSection.id == content_id,
        ContentSection.page_id == page_id,
    )
    if not include_deleted:
        query = query.where(ContentSection.is_deleted.is_(False))
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content section not found",
        )
    return content


@router.patch(
    "/{site_id}/pages/{page_id}/content/{content_id}",
    response_model=ContentSectionResponse,
)
async def update_content_section(
    site_id: UUID,
    page_id: UUID,
    content_id: UUID,
    content_in: ContentSectionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContentSection:
    """Update a content section draft (does not affect published content)."""
    await get_page_owned_by_user(site_id, page_id, current_user, db)
    result = await db.execute(
        select(ContentSection).where(
            ContentSection.id == content_id,
            ContentSection.page_id == page_id,
            ContentSection.is_deleted.is_(False),
        )
    )
    db_content = result.scalar_one_or_none()
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content section not found",
        )

    update_data = content_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_content, field, value)

    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    await _broadcast_sections(page_id, db)
    return db_content


@router.delete(
    "/{site_id}/pages/{page_id}/content/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_content_section(
    site_id: UUID,
    page_id: UUID,
    content_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete a content section."""
    await get_page_owned_by_user(site_id, page_id, current_user, db)
    result = await db.execute(
        select(ContentSection).where(
            ContentSection.id == content_id,
            ContentSection.page_id == page_id,
            ContentSection.is_deleted.is_(False),
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content section not found",
        )

    content.is_deleted = True  # type: ignore
    content.deleted_at = datetime.now(UTC)  # type: ignore
    db.add(content)
    await db.commit()
    await _broadcast_sections(page_id, db)


# ── Upsert by section type (primary MCP write path) ──────────────────────────


@router.put(
    "/{site_id}/pages/{page_id}/content/by-type/{section_type}",
    response_model=ContentSectionResponse,
)
async def upsert_content_section_by_type(
    site_id: UUID,
    page_id: UUID,
    section_type: str,
    content_in: ContentSectionUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContentSection:
    """Create or update a section by type (no UUID required).

    If a section with this type already exists for the page, its content_draft
    is updated. Otherwise a new section is created. This is the primary write
    path used by MCP tools — AI tools never need to track section UUIDs.

    Broadcasts SSE update to all connected preview clients after saving.
    """
    await get_page_owned_by_user(site_id, page_id, current_user, db)

    result = await db.execute(
        select(ContentSection).where(
            ContentSection.page_id == page_id,
            ContentSection.section_type == section_type,
            ContentSection.is_deleted.is_(False),
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.content_draft = content_in.content_draft  # type: ignore
        if content_in.order is not None:
            existing.order = content_in.order  # type: ignore
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        section = existing
    else:
        # Determine default order (append after existing sections)
        count_result = await db.execute(
            select(ContentSection).where(
                ContentSection.page_id == page_id,
                ContentSection.is_deleted.is_(False),
            )
        )
        existing_count = len(count_result.scalars().all())

        section = ContentSection(
            page_id=page_id,
            section_type=section_type,
            content_draft=content_in.content_draft,
            order=content_in.order if content_in.order is not None else existing_count,
        )
        db.add(section)
        await db.commit()
        await db.refresh(section)

    await _broadcast_sections(page_id, db)
    return section
