"""Admin API — platform management endpoints.

Requires is_admin=True on the authenticated user.

Routes (all under /api/admin):
  GET  /stats                    — platform-wide counts
  GET  /users                    — list all users with site count
  GET  /sites                    — list all active sites across all users
  PATCH /users/{user_id}         — update email / password / is_admin
  DELETE /users/{user_id}        — delete user + all their data
  POST /impersonate/{user_id}    — get a short-lived JWT for any user (admin only)
"""

import asyncio
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models import Site
from src.models.content import ContentSection
from src.models.page import Page
from src.models.user import User, UserPlan
from src.schemas.user import UserResponse
from src.services.auth import AuthService
from src.services.email import EmailService

router = APIRouter()


# ── Guards ─────────────────────────────────────────────────────────────────────

async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# ── Schemas ────────────────────────────────────────────────────────────────────

class UserWithStats(BaseModel):
    id: UUID
    email: str
    is_admin: bool
    plan: str
    site_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PlatformStats(BaseModel):
    total_users: int
    total_sites: int
    total_pages: int
    total_sections: int


class AdminSiteRow(BaseModel):
    id: UUID
    name: str
    slug: str
    user_email: str
    user_plan: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_admin: bool | None = None
    plan: UserPlan | None = None


class ImpersonateResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_email: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=PlatformStats)
async def get_stats(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformStats:
    """Platform-wide aggregate counts."""
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    total_sites = (await db.execute(
        select(func.count()).select_from(Site).where(Site.is_deleted.is_(False))
    )).scalar_one()
    total_pages = (await db.execute(
        select(func.count()).select_from(Page).where(Page.is_deleted.is_(False))
    )).scalar_one()
    total_sections = (await db.execute(
        select(func.count()).select_from(ContentSection).where(ContentSection.is_deleted.is_(False))
    )).scalar_one()

    return PlatformStats(
        total_users=total_users,
        total_sites=total_sites,
        total_pages=total_pages,
        total_sections=total_sections,
    )


@router.get("/users", response_model=list[UserWithStats])
async def list_users(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UserWithStats]:
    """List all users with their active site count."""
    # Subquery: count active sites per user
    site_counts = (
        select(Site.user_id, func.count(Site.id).label("site_count"))
        .where(Site.is_deleted.is_(False))
        .group_by(Site.user_id)
        .subquery()
    )

    rows = await db.execute(
        select(User, func.coalesce(site_counts.c.site_count, 0).label("site_count"))
        .outerjoin(site_counts, User.id == site_counts.c.user_id)
        .order_by(User.created_at.desc())
    )

    result = []
    for user, site_count in rows.all():
        result.append(
            UserWithStats(
                id=user.id,
                email=str(user.email),
                is_admin=bool(user.is_admin),
                plan=str(user.plan),
                site_count=int(site_count),
                created_at=user.created_at,  # type: ignore[arg-type]
            )
        )
    return result


@router.get("/sites", response_model=list[AdminSiteRow])
async def list_all_sites_admin(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AdminSiteRow]:
    """List all active sites across all users — admin only."""
    rows = await db.execute(
        select(Site, User.email, User.plan)  # type: ignore[call-overload]
        .join(User, Site.user_id == User.id)
        .where(Site.is_deleted.is_(False))
        .order_by(Site.updated_at.desc())
    )
    result = []
    for site, email, plan in rows.all():
        result.append(
            AdminSiteRow(
                id=site.id,
                name=site.name,
                slug=site.slug,
                user_email=str(email),
                user_plan=str(plan),
                created_at=site.created_at,
                updated_at=site.updated_at,
            )
        )
    return result


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update: AdminUserUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update any user's email, password, or admin status."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update.email is not None:
        user.email = update.email  # type: ignore[assignment]
    if update.password is not None:
        user.password_hash = AuthService.get_password_hash(update.password)  # type: ignore[assignment]
    if update.is_admin is not None:
        user.is_admin = update.is_admin  # type: ignore[assignment]
    plan_changed = update.plan is not None and update.plan != user.plan
    if update.plan is not None:
        user.plan = update.plan  # type: ignore[assignment]

    db.add(user)
    await db.commit()
    await db.refresh(user)

    if plan_changed:
        asyncio.create_task(EmailService.send_plan_upgraded(str(user.email), str(user.plan)))

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a user and soft-delete all their sites."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account via admin panel")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Soft-delete all sites belonging to this user
    sites_result = await db.execute(
        select(Site).where(Site.user_id == user_id, Site.is_deleted.is_(False))
    )
    for site in sites_result.scalars().all():
        site.is_deleted = True  # type: ignore[assignment]
        site.deleted_at = datetime.now(UTC)  # type: ignore[assignment]
        db.add(site)

    await db.delete(user)
    await db.commit()


@router.post("/impersonate/{user_id}", response_model=ImpersonateResponse)
async def impersonate_user(
    user_id: UUID,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ImpersonateResponse:
    """Generate a short-lived JWT for any user (for admin debugging)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = AuthService.create_access_token(data={"sub": str(user.id)})
    return ImpersonateResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        user_email=str(user.email),
    )
