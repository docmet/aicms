"""WordPress site registration and management API."""

import os
import secrets
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
    WPDispatchRequest,
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


@router.post("/wp-mcp/{wp_mcp_token}/dispatch")
async def wp_mcp_dispatch(
    wp_mcp_token: str,
    request_body: WPDispatchRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Internal endpoint: MCP server proxies WP REST calls through here.

    No user auth — authenticated via X-Internal-Secret header.
    The wp_mcp_token identifies the WordPressSite.
    """
    internal_secret = os.getenv("INTERNAL_SECRET", "")
    if internal_secret:
        provided = request.headers.get("x-internal-secret", "")
        if provided != internal_secret:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal secret")

    result = await db.execute(
        select(WordPressSite).where(
            WordPressSite.mcp_token == wp_mcp_token,
            WordPressSite.is_active.is_(True),
        )
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress site not found")

    client = WordPressClient(
        site_url=str(db_site.site_url),
        username=str(db_site.app_username),
        password=str(db_site.app_password_encrypted),
    )

    tool = request_body.tool
    args = request_body.args

    try:
        if tool == "wp_list_posts":
            wp_result = await client.list_posts(
                status=args.get("status", "any"),
                per_page=args.get("per_page", 20),
            )
        elif tool == "wp_get_post":
            wp_result = await client.get_post(args["post_id"])
        elif tool == "wp_create_post":
            extra = {k: v for k, v in args.items() if k not in ("title", "content", "status")}
            wp_result = await client.create_post(args["title"], args["content"], args.get("status", "draft"), **extra)
        elif tool == "wp_update_post":
            extra = {k: v for k, v in args.items() if k != "post_id"}
            wp_result = await client.update_post(args["post_id"], **extra)
        elif tool == "wp_publish_post":
            wp_result = await client.update_post(args["post_id"], status="publish")
        elif tool == "wp_list_pages":
            wp_result = await client.list_pages(
                status=args.get("status", "any"),
                per_page=args.get("per_page", 20),
            )
        elif tool == "wp_get_page":
            wp_result = await client.get_page(args["page_id"])
        elif tool == "wp_create_page":
            extra = {k: v for k, v in args.items() if k not in ("title", "content", "status")}
            wp_result = await client.create_page(args["title"], args["content"], args.get("status", "draft"), **extra)
        elif tool == "wp_update_page":
            extra = {k: v for k, v in args.items() if k != "page_id"}
            wp_result = await client.update_page(args["page_id"], **extra)
        elif tool == "wp_publish_page":
            wp_result = await client.update_page(args["page_id"], status="publish")
        elif tool == "wp_list_categories":
            wp_result = await client.list_categories()
        elif tool == "wp_list_tags":
            wp_result = await client.list_tags()
        elif tool == "wp_get_site_info":
            wp_result = await client.get_site_info()
        elif tool == "wp_update_site_settings":
            wp_result = await client.update_site_settings(args.get("title"), args.get("description"))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown WP tool: {tool}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return {"result": wp_result}
