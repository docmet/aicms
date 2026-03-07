import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.admin import router as admin_router
from src.api.analytics import private_router as analytics_router
from src.api.analytics import public_router as analytics_public_router
from src.api.auth import router as auth_router
from src.api.billing import router as billing_router
from src.api.blog import router as blog_router
from src.api.content import router as content_router
from src.api.mcp import router as mcp_router
from src.api.media import router as media_router
from src.api.oauth import router as oauth_router
from src.api.pages import router as pages_router
from src.api.preview import router as preview_router
from src.api.public import router as public_router
from src.api.share import private_router as share_router
from src.api.share import public_router as share_public_router
from src.api.sites import router as sites_router
from src.api.submissions import private_router as submissions_router
from src.api.submissions import public_router as submissions_public_router
from src.api.themes import router as themes_router
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Sentry error monitoring ────────────────────────────────────────────────────
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.0,  # Errors only — enable traces when needed
    )


async def _run_scheduled_publishes() -> None:
    """Background task: publish pages whose scheduled_at has passed."""
    import json
    from datetime import UTC, datetime
    from uuid import uuid4

    from sqlalchemy import select

    from src.api.content import _broadcast_sections, _broadcast_theme
    from src.database import AsyncSessionLocal
    from src.models.content import ContentSection
    from src.models.page import Page
    from src.models.page_version import PageVersion
    from src.models.site import Site

    while True:
        try:
            now = datetime.now(UTC)
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Page).where(
                        Page.scheduled_at.isnot(None),
                        Page.scheduled_at <= now,
                        Page.is_deleted.is_(False),
                    )
                )
                pages = result.scalars().all()
                for page in pages:
                    try:
                        site_result = await db.execute(
                            select(Site).where(Site.id == page.site_id, Site.is_deleted.is_(False))
                        )
                        site = site_result.scalar_one_or_none()
                        if not site:
                            page.scheduled_at = None  # type: ignore[assignment]
                            db.add(page)
                            continue

                        if site.theme_slug_draft is not None:
                            site.theme_slug = site.theme_slug_draft  # type: ignore[assignment]
                            site.theme_slug_draft = None  # type: ignore[assignment]
                            db.add(site)

                        sections_result = await db.execute(
                            select(ContentSection).where(
                                ContentSection.page_id == page.id,
                                ContentSection.is_deleted.is_(False),
                            )
                        )
                        sections = sections_result.scalars().all()
                        for s in sections:
                            s.content_published = s.content_draft  # type: ignore[assignment]
                            db.add(s)

                        versions_result = await db.execute(
                            select(PageVersion)
                            .where(PageVersion.page_id == page.id)
                            .order_by(PageVersion.version_number.desc())
                            .limit(1)
                        )
                        latest = versions_result.scalar_one_or_none()
                        next_num = (latest.version_number + 1) if latest else 1
                        snapshot = json.dumps({
                            "page": {"id": str(page.id), "title": page.title, "slug": page.slug},
                            "theme_slug": str(site.theme_slug) if site.theme_slug else None,
                            "sections": [{"section_type": s.section_type, "content": s.content_draft, "order": s.order} for s in sections],
                        })
                        db.add(PageVersion(id=uuid4(), page_id=page.id, version_number=next_num, snapshot=snapshot))

                        page.is_published = True  # type: ignore[assignment]
                        page.last_published_at = now  # type: ignore[assignment]
                        page.scheduled_at = None  # type: ignore[assignment]
                        db.add(page)
                        await db.commit()

                        await _broadcast_sections(page.id, db)  # type: ignore[arg-type]
                        await _broadcast_theme(page.site_id, None, str(site.theme_slug) if site.theme_slug else None, db)  # type: ignore[arg-type]
                        logger.info("Scheduled publish: page %s", page.id)
                    except Exception as e:
                        logger.warning("Scheduled publish failed for page %s: %s", page.id, e)
                        await db.rollback()
        except Exception as e:
            logger.warning("Scheduler loop error: %s", e)
        await asyncio.sleep(60)  # check every minute


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    asyncio.create_task(_run_scheduled_publishes())
    yield


# Create FastAPI app
app = FastAPI(
    title="AI CMS API",
    description="AI-powered Content Management System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "AI CMS API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(sites_router, prefix="/api/sites", tags=["sites"])
app.include_router(pages_router, prefix="/api/sites", tags=["pages"])
app.include_router(content_router, prefix="/api/sites", tags=["content"])
app.include_router(media_router, prefix="/api/sites", tags=["media"])
app.include_router(blog_router, prefix="/api/sites", tags=["blog"])
app.include_router(submissions_router, prefix="/api/sites", tags=["submissions"])
app.include_router(submissions_public_router, prefix="/api/public/sites", tags=["public"])
app.include_router(analytics_router, prefix="/api/sites", tags=["analytics"])
app.include_router(analytics_public_router, prefix="/api/public/sites", tags=["public"])
app.include_router(share_router, prefix="/api/sites", tags=["share"])
app.include_router(share_public_router, prefix="/api/share", tags=["share"])
app.include_router(themes_router, prefix="/api/themes", tags=["themes"])
app.include_router(public_router, prefix="/api/public/sites", tags=["public"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["mcp"])
app.include_router(oauth_router, tags=["oauth"])
app.include_router(preview_router, prefix="/api/preview", tags=["preview"])
app.include_router(billing_router, prefix="/api/billing", tags=["billing"])

# Serve local uploads (dev only; in production, R2 serves files directly)
if settings.storage_backend == "local":
    upload_dir = Path(settings.local_upload_path)
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    except OSError:
        pass  # Skip in test environments where the upload path may not be writable
