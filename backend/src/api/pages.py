from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
) -> Site:
    """Helper to verify site ownership."""
    result = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    )
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
        select(Page).where(Page.site_id == site_id, Page.slug == page_in.slug)
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
) -> list[Page]:
    """List all pages belonging to a specific site."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(Page.site_id == site_id).order_by(Page.order)
    )
    return list(result.scalars().all())


@router.get("/{site_id}/pages/{page_id}", response_model=PageResponse)
async def get_page(
    site_id: UUID,
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    """Get a specific page by ID."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(Page.id == page_id, Page.site_id == site_id)
    )
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
    """Delete a page."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(Page).where(Page.id == page_id, Page.site_id == site_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    await db.delete(page)
    await db.commit()
