"""WordPress site registration and management API."""

import secrets
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.user import User
from src.models.wordpress_site import WordPressSite
from src.schemas.wordpress import (
    WordPressSiteCreate,
    WordPressSiteResponse,
    WordPressSiteUpdate,
)
from src.services.wordpress_client import WordPressClient

router = APIRouter(prefix="/wordpress", tags=["wordpress"])


@router.post("/sites", response_model=WordPressSiteResponse, status_code=status.HTTP_201_CREATED)
async def register_wordpress_site(
    site_in: WordPressSiteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WordPressSite:
    """Register a new WordPress site with Application Password credentials."""
    site_url = str(site_in.site_url).rstrip("/")

    # Probe the WP site to validate credentials and get site info
    client = WordPressClient(
        site_url=site_url,
        username=site_in.app_username,
        password=site_in.app_password,
    )
    try:
        wp_info = await client.get_site_info()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot connect to WordPress site. Check URL and Application Password.",
        )

    site_name: str | None = wp_info.get("name")

    mcp_token = secrets.token_urlsafe(48)

    db_site = WordPressSite(
        user_id=current_user.id,
        site_url=site_url,
        app_username=site_in.app_username,
        app_password_encrypted=site_in.app_password,
        site_name=site_name,
        mcp_token=mcp_token,
        is_active=True,
    )
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.get("/sites", response_model=list[WordPressSiteResponse])
async def list_wordpress_sites(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[WordPressSite]:
    """List all active WordPress sites for the current user."""
    result = await db.execute(
        select(WordPressSite).where(
            WordPressSite.user_id == current_user.id,
        )
    )
    return list(result.scalars().all())


@router.get("/sites/{site_id}", response_model=WordPressSiteResponse)
async def get_wordpress_site(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WordPressSite:
    """Get a single WordPress site by ID."""
    result = await db.execute(
        select(WordPressSite).where(WordPressSite.id == site_id)
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress site not found")
    if db_site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return db_site


@router.patch("/sites/{site_id}", response_model=WordPressSiteResponse)
async def update_wordpress_site(
    site_id: UUID,
    site_in: WordPressSiteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WordPressSite:
    """Update a WordPress site's credentials or URL."""
    result = await db.execute(
        select(WordPressSite).where(WordPressSite.id == site_id)
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress site not found")
    if db_site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    credentials_changed = site_in.site_url is not None or site_in.app_password is not None

    if site_in.site_url is not None:
        db_site.site_url = site_in.site_url.rstrip("/")  # type: ignore[assignment]
    if site_in.app_username is not None:
        db_site.app_username = site_in.app_username  # type: ignore[assignment]
    if site_in.app_password is not None:
        db_site.app_password_encrypted = site_in.app_password  # type: ignore[assignment]
    if site_in.is_active is not None:
        db_site.is_active = site_in.is_active  # type: ignore[assignment]

    # Re-probe WP if URL or password changed, and generate new mcp_token
    if credentials_changed:
        client = WordPressClient(
            site_url=str(db_site.site_url),
            username=str(db_site.app_username),
            password=str(db_site.app_password_encrypted),
        )
        try:
            wp_info = await client.get_site_info()
            db_site.site_name = wp_info.get("name")  # type: ignore[assignment]
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot connect to WordPress site. Check URL and Application Password.",
            )
        db_site.mcp_token = secrets.token_urlsafe(48)  # type: ignore[assignment]

    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wordpress_site(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft-delete a WordPress site by setting is_active=False."""
    result = await db.execute(
        select(WordPressSite).where(WordPressSite.id == site_id)
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress site not found")
    if db_site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db_site.is_active = False  # type: ignore[assignment]
    db.add(db_site)
    await db.commit()
