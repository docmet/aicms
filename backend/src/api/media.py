"""Media file upload and management API.

Routes mounted at /api/sites/{site_id}/media.

  POST   /{site_id}/media/upload        — upload a file (multipart/form-data)
  GET    /{site_id}/media               — list media files for a site
  PATCH  /{site_id}/media/{media_id}    — update alt_text
  DELETE /{site_id}/media/{media_id}    — delete file from storage + DB
  POST   /{site_id}/media/import-url    — import an image from a public URL
"""

import io
from typing import Annotated
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.api.pages import get_site_owned_by_user
from src.config import get_settings
from src.database import get_db
from src.models.media import MediaFile
from src.models.user import User
from src.schemas.media import MediaFileResponse
from src.services.storage import (
    ALLOWED_TYPES,
    PLAN_FILE_LIMITS,
    PLAN_STORAGE_LIMITS,
    get_storage,
    make_storage_key,
)

router = APIRouter()

settings = get_settings()


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _check_plan_limits(site_id: UUID, user: User, db: AsyncSession) -> None:
    """Raise 403 if the user has exceeded their plan's storage or file count."""
    plan = str(user.plan) if user.plan else "free"

    # File count limit (0 = unlimited)
    file_limit = PLAN_FILE_LIMITS.get(plan, 20)
    if file_limit > 0:
        count_result = await db.execute(
            select(func.count()).select_from(MediaFile).where(MediaFile.site_id == site_id)
        )
        current_count = count_result.scalar_one()
        if current_count >= file_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"plan_file_limit_reached:{plan}:{file_limit}",
            )

    # Storage size limit
    storage_limit = PLAN_STORAGE_LIMITS.get(plan, 50 * 1024 * 1024)
    size_result = await db.execute(
        select(func.sum(MediaFile.size_bytes)).where(MediaFile.site_id == site_id)
    )
    current_bytes: int = size_result.scalar_one() or 0
    if current_bytes >= storage_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"plan_storage_limit_reached:{plan}:{storage_limit}",
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/{site_id}/media/upload",
    response_model=MediaFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> MediaFile:
    """Upload a file (image or document) for a site."""
    await get_site_owned_by_user(site_id, current_user, db)

    # Validate MIME type
    mime_type = file.content_type or ""
    file_type = ALLOWED_TYPES.get(mime_type)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {mime_type}",
        )

    # Read file data
    data = await file.read()
    size_bytes = len(data)

    # Enforce max upload size per file
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB.",
        )

    # Enforce plan limits
    await _check_plan_limits(site_id, current_user, db)

    # Upload to storage
    storage_key = make_storage_key(str(site_id), file.filename or "upload")
    storage = get_storage()
    url = await storage.upload(storage_key, data, mime_type)

    # Detect image dimensions if it's an image
    width: int | None = None
    height: int | None = None
    if file_type == "image" and mime_type != "image/svg+xml":
        try:
            from PIL import Image as PILImage  # type: ignore[import-not-found]

            img = PILImage.open(io.BytesIO(data))
            width, height = img.size
        except Exception:
            pass  # Non-critical, skip if Pillow not installed or fails

    # Save record
    media_file = MediaFile(
        id=uuid4(),
        site_id=site_id,
        user_id=current_user.id,
        original_filename=file.filename or "upload",
        storage_key=storage_key,
        url=url,
        mime_type=mime_type,
        file_type=file_type,
        size_bytes=size_bytes,
        width=width,
        height=height,
    )
    db.add(media_file)
    await db.commit()
    await db.refresh(media_file)
    return media_file


@router.get("/{site_id}/media", response_model=list[MediaFileResponse])
async def list_media(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MediaFile]:
    """List all media files for a site, newest first."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(MediaFile)
        .where(MediaFile.site_id == site_id)
        .order_by(MediaFile.created_at.desc())
    )
    return list(result.scalars().all())


class MediaUpdate(BaseModel):
    alt_text: str | None = None


@router.patch("/{site_id}/media/{media_id}", response_model=MediaFileResponse)
async def update_media(
    site_id: UUID,
    media_id: UUID,
    update: MediaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MediaFile:
    """Update alt_text on a media file."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(MediaFile).where(MediaFile.id == media_id, MediaFile.site_id == site_id)
    )
    media_file = result.scalar_one_or_none()
    if not media_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    media_file.alt_text = update.alt_text  # type: ignore[assignment]
    db.add(media_file)
    await db.commit()
    await db.refresh(media_file)
    return media_file


@router.delete("/{site_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    site_id: UUID,
    media_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a media file from storage and the database."""
    await get_site_owned_by_user(site_id, current_user, db)
    result = await db.execute(
        select(MediaFile).where(MediaFile.id == media_id, MediaFile.site_id == site_id)
    )
    media_file = result.scalar_one_or_none()
    if not media_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    # Delete from storage backend
    storage = get_storage()
    await storage.delete(str(media_file.storage_key))

    await db.delete(media_file)
    await db.commit()


class ImportUrlRequest(BaseModel):
    url: str
    alt_text: str | None = None


@router.post(
    "/{site_id}/media/import-url",
    response_model=MediaFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_media_from_url(
    site_id: UUID,
    body: ImportUrlRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MediaFile:
    """Download an image from a public URL and store it as a site media file."""
    await get_site_owned_by_user(site_id, current_user, db)
    await _check_plan_limits(site_id, current_user, db)

    # Download image
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(body.url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch URL: {exc}",
        ) from exc

    mime_type = resp.headers.get("content-type", "").split(";")[0].strip()
    file_type = ALLOWED_TYPES.get(mime_type)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"URL returned unsupported type: {mime_type}",
        )

    data = resp.content
    size_bytes = len(data)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Remote file too large. Maximum size is {settings.max_upload_size_mb}MB.",
        )

    # Derive filename from URL path
    original_filename = body.url.rstrip("/").split("/")[-1] or "imported"

    # Detect image dimensions
    width: int | None = None
    height: int | None = None
    if file_type == "image" and mime_type != "image/svg+xml":
        try:
            from PIL import Image as PILImage  # type: ignore[import-not-found]

            img = PILImage.open(io.BytesIO(data))
            width, height = img.size
        except Exception:
            pass

    storage_key = make_storage_key(str(site_id), original_filename)
    storage = get_storage()
    url = await storage.upload(storage_key, data, mime_type)

    media_file = MediaFile(
        id=uuid4(),
        site_id=site_id,
        user_id=current_user.id,
        original_filename=original_filename,
        storage_key=storage_key,
        url=url,
        mime_type=mime_type,
        file_type=file_type,
        size_bytes=size_bytes,
        alt_text=body.alt_text,
        width=width,
        height=height,
    )
    db.add(media_file)
    await db.commit()
    await db.refresh(media_file)
    return media_file
