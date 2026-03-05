from typing import Annotated
from uuid import UUID

from datetime import UTC, datetime

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
)

router = APIRouter()


async def get_page_owned_by_user(
    site_id: UUID,
    page_id: UUID,
    current_user: User,
    db: AsyncSession,
    include_deleted: bool = False,
) -> Page:
    """Helper to verify page ownership via site."""
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
        query = query.where(Page.is_deleted == False)
    result = await db.execute(query)
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found or not owned by user",
        )
    return page


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
        **content_in.model_dump(),
        page_id=page_id,
    )
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    return db_content


@router.get(
    "/{site_id}/pages/{page_id}/content", response_model=list[ContentSectionResponse]
)
async def list_content_sections(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False, description="Include deleted sections"),
) -> list[ContentSection]:
    """List all content sections for a specific page."""
    await get_page_owned_by_user(site_id, page_id, current_user, db, include_deleted)
    query = (
        select(ContentSection)
        .where(ContentSection.page_id == page_id)
        .order_by(ContentSection.order)
    )
    if not include_deleted:
        query = query.where(ContentSection.is_deleted == False)
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
        ContentSection.id == content_id, ContentSection.page_id == page_id
    )
    if not include_deleted:
        query = query.where(ContentSection.is_deleted == False)
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
    """Update a content section."""
    await get_page_owned_by_user(site_id, page_id, current_user, db)
    result = await db.execute(
        select(ContentSection).where(
            ContentSection.id == content_id, ContentSection.page_id == page_id
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
            ContentSection.is_deleted == False,
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content section not found",
        )

    # Soft delete
    content.is_deleted = True
    content.deleted_at = datetime.now(UTC)
    db.add(content)
    await db.commit()
