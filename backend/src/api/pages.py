from typing import Annotated
from uuid import UUID

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.page import Page
from src.models.site import Site
from src.models.user import User
from src.schemas.page import PageCreate, PageResponse, PageUpdate

router = APIRouter()


async def get_site_owned_by_user(
    site_id: UUID,
    current_user: User,
    db: AsyncSession,
    include_deleted: bool = False,
) -> Site:
    """Helper to verify site ownership."""
    query = select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    if not include_deleted:
        query = query.where(Site.is_deleted == False)
    result = await db.execute(query)
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    return site


@router.post(
    "/{site_id}/pages", response_model=PageResponse, status_code=status.HTTP_201_CREATED
)
async def create_page(
    site_id: UUID,
    page_in: PageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Create a new page for a specific site."""
    await get_site_owned_by_user(site_id, current_user, db)

    # Check if slug is already taken within this site
    result = await db.execute(
        select(Page).where(Page.site_id == site_id, Page.slug == page_in.slug).limit(1)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page with this slug already exists in this site",
        )

    db_page = Page(
        **page_in.model_dump(),
        site_id=site_id,
    )
    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page


@router.get("/{site_id}/pages", response_model=list[PageResponse])
async def list_pages(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False, description="Include deleted pages"),
) -> list[Page]:
    """List all pages belonging to a specific site."""
    await get_site_owned_by_user(site_id, current_user, db, include_deleted)
    query = select(Page).where(Page.site_id == site_id).order_by(Page.order)
    if not include_deleted:
        query = query.where(Page.is_deleted == False)
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
        query = query.where(Page.is_deleted == False)
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
    """Update a page."""
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

    # If slug is being updated, check if it's already taken in this site
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
            Page.id == page_id, Page.site_id == site_id, Page.is_deleted == False
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Soft delete
    page.is_deleted = True
    page.deleted_at = datetime.now(UTC)
    db.add(page)
    await db.commit()
