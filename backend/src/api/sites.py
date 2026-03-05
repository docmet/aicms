from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.site import Site
from src.models.user import User
from src.schemas.site import SiteCreate, SiteResponse, SiteUpdate

router = APIRouter()


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_in: SiteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Site:
    """Create a new site for the current user."""
    # Check if slug is already taken
    result = await db.execute(select(Site).where(Site.slug == site_in.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site with this slug already exists",
        )

    db_site = Site(
        **site_in.model_dump(),
        user_id=current_user.id,
    )
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.get("/", response_model=list[SiteResponse])
async def list_sites(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False, description="Include deleted sites"),
) -> list[Site]:
    """List all sites belonging to the current user."""
    query = select(Site).where(Site.user_id == current_user.id)
    if not include_deleted:
        query = query.where(Site.is_deleted.is_(False))
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_deleted: bool = Query(default=False),
) -> Site:
    """Get a specific site by ID, if it belongs to the current user."""
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


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: UUID,
    site_in: SiteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Site:
    """Update a site belonging to the current user."""
    result = await db.execute(
        select(Site).where(
            Site.id == site_id, Site.user_id == current_user.id, Site.is_deleted.is_(False),
        )
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    update_data = site_in.model_dump(exclude_unset=True)

    # If slug is being updated, check if it's already taken
    if "slug" in update_data and update_data["slug"] != db_site.slug:
        slug_result = await db.execute(
            select(Site).where(Site.slug == update_data["slug"], Site.is_deleted.is_(False),)
        )
        if slug_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site with this slug already exists",
            )

    for field, value in update_data.items():
        setattr(db_site, field, value)

    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete a site belonging to the current user."""
    result = await db.execute(
        select(Site).where(
            Site.id == site_id, Site.user_id == current_user.id, Site.is_deleted.is_(False),
        )
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Soft delete
    site.is_deleted = True  # type: ignore
    site.deleted_at = datetime.now(UTC)  # type: ignore
    db.add(site)
    await db.commit()
