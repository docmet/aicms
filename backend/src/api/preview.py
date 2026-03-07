"""SSE endpoint for real-time page preview.

GET /api/preview/pages/{page_id}/stream
  Server-Sent Events stream. Auth required (JWT).
  Streams JSON payloads whenever draft content for the page changes.

Event payload format:
  data: {"type": "sections_updated", "page_id": "...", "sections": [...]}

The admin editor connects to this stream on page load and passes events to the
preview iframe, which re-renders sections sub-second without polling.
"""

import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.database import get_db
from src.models.content import ContentSection
from src.models.page import Page
from src.models.share_preview import SharePreview
from src.models.site import Site
from src.models.user import User
from src.services.preview import preview_manager

router = APIRouter()


@router.get("/pages/{page_id}/stream")
async def preview_stream(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreamingResponse:
    """SSE stream for live preview of draft content changes.

    Connect from the admin editor. Each event is a JSON payload describing
    the current state of all sections for the page.
    """
    # Verify ownership via site join
    result = await db.execute(
        select(Page)
        .join(Site)
        .where(
            Page.id == page_id,
            Site.user_id == current_user.id,
            Page.is_deleted.is_(False),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    queue = preview_manager.subscribe(page_id)

    async def event_generator() -> AsyncGenerator[str]:
        # Send connected acknowledgement immediately
        yield 'data: {"type": "connected"}\n\n'
        async for message in preview_manager.stream(page_id, queue):
            yield message

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx response buffering
        },
    )


@router.get("/share/{token}")
async def share_preview_stream(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreamingResponse:
    """Public SSE stream for share-link previews. No auth required — validated by share token."""
    result = await db.execute(select(SharePreview).where(SharePreview.token == token))
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Preview link not found")

    expires = sp.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if datetime.now(UTC) > expires:
        raise HTTPException(status_code=410, detail="Preview link has expired")

    # Resolve page_id (fall back to first page of site if not set)
    resolved_page_id: UUID
    if sp.page_id:
        resolved_page_id = UUID(str(sp.page_id))
    else:
        pg_result = await db.execute(
            select(Page)
            .where(Page.site_id == sp.site_id, Page.is_deleted.is_(False))
            .order_by(Page.order)
            .limit(1)
        )
        page = pg_result.scalar_one_or_none()
        if not page:
            raise HTTPException(status_code=404, detail="No page found")
        resolved_page_id = UUID(str(page.id))

    queue = preview_manager.subscribe(resolved_page_id)

    async def event_generator() -> AsyncGenerator[str]:
        # Send initial sections snapshot so the client can sync immediately on connect
        sections_result = await db.execute(
            select(ContentSection)
            .where(ContentSection.page_id == resolved_page_id, ContentSection.is_deleted.is_(False))
            .order_by(ContentSection.order)
        )
        sections = sections_result.scalars().all()
        snapshot = [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "content_draft": s.content_draft,
                "order": s.order,
                "has_unpublished_changes": False,
            }
            for s in sections
            if s.content_draft
        ]
        yield f"data: {json.dumps({'type': 'sections_updated', 'sections': snapshot})}\n\n"

        async for message in preview_manager.stream(resolved_page_id, queue):
            yield message

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
