"""Contact form submission API.

Public submit endpoint (no auth):
  POST /api/public/sites/{site_slug}/contact

Owner read endpoints (auth required):
  GET    /api/sites/{site_id}/submissions
  PATCH  /api/sites/{site_id}/submissions/{sub_id}/read
  DELETE /api/sites/{site_id}/submissions/{sub_id}
"""

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.site import Site
from src.models.submission import FormSubmission
from src.models.user import User

public_router = APIRouter()
private_router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class SubmitContactForm(BaseModel):
    name: str
    email: str
    subject: str | None = None
    message: str


class SubmissionResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    email: str
    subject: str | None
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Public: submit form (no auth) ─────────────────────────────────────────────

@public_router.post("/{site_slug}/contact", status_code=201)
async def submit_contact_form(
    site_slug: str,
    body: SubmitContactForm,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit a contact form for a site. No auth required."""
    # Validate site exists
    result = await db.execute(
        select(Site).where(Site.slug == site_slug, Site.is_deleted.is_(False))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    submission = FormSubmission(
        id=uuid4(),
        site_id=site.id,
        name=body.name,
        email=body.email,
        subject=body.subject,
        message=body.message,
    )
    db.add(submission)
    await db.commit()

    # Fire-and-forget email notification to site owner
    asyncio.create_task(_notify_owner(site, submission))

    return {"ok": True, "message": "Message sent. We'll be in touch soon!"}


async def _notify_owner(site: Site, sub: FormSubmission) -> None:
    """Send email notification to site owner (non-fatal)."""
    from sqlalchemy import select as sa_select

    from src.database import AsyncSessionLocal
    from src.models.user import User
    from src.services.email import EmailService

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(sa_select(User).where(User.id == site.user_id))
            owner = result.scalar_one_or_none()
            if owner and owner.email:
                await EmailService.send_contact_notification(
                    to=str(owner.email),
                    site_name=str(site.name),
                    visitor_name=str(sub.name),
                    visitor_email=str(sub.email),
                    subject=str(sub.subject) if sub.subject else None,
                    message=str(sub.message),
                )
    except Exception:
        pass  # Non-fatal


# ── Private: read submissions (auth required) ─────────────────────────────────

async def _get_site_or_404(site_id: UUID, current_user: User, db: AsyncSession) -> Site:
    result = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id, ~Site.is_deleted)
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@private_router.get("/{site_id}/submissions", response_model=list[SubmissionResponse])
async def list_submissions(
    site_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FormSubmission]:
    """List all form submissions for a site (newest first)."""
    await _get_site_or_404(site_id, current_user, db)

    result = await db.execute(
        select(FormSubmission)
        .where(FormSubmission.site_id == site_id)
        .order_by(FormSubmission.created_at.desc())
    )
    return list(result.scalars().all())


@private_router.patch("/{site_id}/submissions/{sub_id}/read", response_model=SubmissionResponse)
async def mark_read(
    site_id: UUID,
    sub_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FormSubmission:
    """Mark a submission as read."""
    await _get_site_or_404(site_id, current_user, db)

    result = await db.execute(
        select(FormSubmission).where(FormSubmission.id == sub_id, FormSubmission.site_id == site_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    if not sub.read_at:
        sub.read_at = datetime.now(UTC)  # type: ignore[assignment]
        await db.commit()
        await db.refresh(sub)
    return sub


@private_router.delete("/{site_id}/submissions/{sub_id}", status_code=204)
async def delete_submission(
    site_id: UUID,
    sub_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a form submission."""
    await _get_site_or_404(site_id, current_user, db)

    result = await db.execute(
        select(FormSubmission).where(FormSubmission.id == sub_id, FormSubmission.site_id == site_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    await db.delete(sub)
    await db.commit()
