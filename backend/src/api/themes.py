from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.theme import Theme
from src.models.user import User
from src.schemas.theme import ThemeResponse

router = APIRouter()


@router.get("/", response_model=list[ThemeResponse])
async def list_themes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Theme]:
    """List all active themes available for sites."""
    result = await db.execute(select(Theme).where(Theme.is_active))
    return list(result.scalars().all())


@router.get("/{theme_slug}", response_model=ThemeResponse)
async def get_theme(
    theme_slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Theme:
    """Get a specific theme by slug."""
    result = await db.execute(
        select(Theme).where(Theme.slug == theme_slug, Theme.is_active)
    )
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    return theme
