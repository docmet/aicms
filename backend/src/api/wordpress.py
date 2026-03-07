"""WordPress site registration and management API."""

import io
import os
import secrets
import zipfile
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
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

# PHP plugin template — {{MYSTOREY_URL}} is replaced at download time with the
# actual server origin so a zip from staging points to staging, local to
# localhost, and production to mystorey.io.
_PLUGIN_PHP_TEMPLATE = r"""<?php
/**
 * Plugin Name: MyStorey – AI Content Control
 * Plugin URI: {{MYSTOREY_URL}}/wordpress
 * Description: Connect your WordPress site to MyStorey so you can control your content via Claude, ChatGPT, or any AI assistant. No coding required.
 * Version: 1.0.0
 * Author: MyStorey
 * Author URI: {{MYSTOREY_URL}}
 * License: GPL v2 or later
 * Text Domain: mystorey-connector
 * Update URI: {{MYSTOREY_URL}}/api/wordpress/plugin/update-check
 */

if ( ! defined( 'ABSPATH' ) ) exit;

define( 'MYSTOREY_PLUGIN_VERSION', '1.0.0' );
define( 'MYSTOREY_URL', '{{MYSTOREY_URL}}' );
define( 'MYSTOREY_MCP_URL', '{{MYSTOREY_URL}}/mcp' );
define( 'MYSTOREY_DASHBOARD_URL', '{{MYSTOREY_URL}}/dashboard/wordpress' );
define( 'MYSTOREY_SETTINGS_PAGE', 'mystorey-connector' );

add_action( 'admin_menu', function() {
    add_options_page(
        'MyStorey AI Connector',
        'MyStorey AI',
        'manage_options',
        MYSTOREY_SETTINGS_PAGE,
        'mystorey_settings_page'
    );
});

add_filter( 'plugin_action_links_mystorey-connector/mystorey-connector.php', function( $links ) {
    $url = esc_url( admin_url( 'options-general.php?page=' . MYSTOREY_SETTINGS_PAGE ) );
    $links['settings'] = '<a href="' . $url . '">Settings</a>';
    return $links;
});

add_action( 'admin_enqueue_scripts', function( $hook ) {
    if ( $hook !== 'settings_page_mystorey-connector' ) return;

    wp_add_inline_style( 'wp-admin', '
        .ms-wrap { max-width: 780px; margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .ms-header { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); border-radius: 12px; padding: 32px 36px; margin-bottom: 28px; color: #fff; }
        .ms-header-logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; margin: 0 0 6px; }
        .ms-header-logo span { color: #c4b5fd; }
        .ms-header p { margin: 0; opacity: 0.85; font-size: 14px; line-height: 1.5; }
        .ms-steps { display: flex; flex-direction: column; gap: 20px; }
        .ms-step { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 24px 28px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
        .ms-step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
        .ms-step-num { width: 32px; height: 32px; border-radius: 50%; background: #7c3aed; color: #fff; font-size: 14px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .ms-step-title { font-size: 15px; font-weight: 700; color: #111827; margin: 0; }
        .ms-step p { margin: 0 0 14px; color: #4b5563; font-size: 14px; line-height: 1.6; }
        .ms-step ol { margin: 0 0 14px 20px; color: #4b5563; font-size: 14px; line-height: 1.8; padding: 0; }
        .ms-field-label { font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
        .ms-copy-row { display: flex; align-items: center; gap: 8px; }
        .ms-code { background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px; padding: 8px 12px; font-family: ui-monospace, "Cascadia Code", monospace; font-size: 13px; color: #1f2937; flex: 1; word-break: break-all; }
        .ms-btn-copy { background: #7c3aed; color: #fff; border: none; border-radius: 6px; padding: 7px 14px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background .15s; }
        .ms-btn-copy:hover { background: #6d28d9; }
        .ms-btn-copy.copied { background: #059669; }
        .ms-btn-primary { display: inline-flex; align-items: center; gap: 6px; background: #7c3aed; color: #fff !important; border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; text-decoration: none !important; transition: background .15s; margin-top: 4px; }
        .ms-btn-primary:hover { background: #6d28d9 !important; }
        .ms-btn-secondary { display: inline-flex; align-items: center; gap: 6px; background: #f3f4f6; color: #374151 !important; border: 1px solid #d1d5db; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; text-decoration: none !important; transition: background .15s; }
        .ms-btn-secondary:hover { background: #e5e7eb !important; }
        .ms-token-note { background: #ede9fe; border: 1px solid #c4b5fd; border-radius: 8px; padding: 14px 16px; font-size: 13px; color: #5b21b6; line-height: 1.6; }
        .ms-token-note a { color: #7c3aed; font-weight: 600; }
        .ms-footer { margin-top: 20px; padding: 16px 20px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #6b7280; }
        .ms-footer a { color: #7c3aed; font-weight: 600; text-decoration: none; }
    ' );

    wp_add_inline_script( 'jquery-core', '
        function msCopy(text, btn) {
            navigator.clipboard.writeText(text).then(function() {
                btn.textContent = "Copied!";
                btn.classList.add("copied");
                setTimeout(function() {
                    btn.textContent = "Copy";
                    btn.classList.remove("copied");
                }, 2000);
            });
        }
    ' );
});

function mystorey_settings_page() {
    $site_url = get_site_url();
    $mcp_url  = MYSTOREY_MCP_URL;
    $dash_url = MYSTOREY_DASHBOARD_URL;
    $profile_url = admin_url( 'profile.php' ) . '#application-passwords-section';
    ?>
    <div class="ms-wrap">

        <!-- Header -->
        <div class="ms-header">
            <p class="ms-header-logo">My<span>Storey</span></p>
            <p>Connect this WordPress site to MyStorey so your AI assistant can write and publish content directly&nbsp;&mdash; no coding required.</p>
        </div>

        <div class="ms-steps">

            <!-- Step 1 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">1</div>
                    <h2 class="ms-step-title">Create an Application Password</h2>
                </div>
                <p>Application Passwords let MyStorey connect to WordPress securely without using your admin password. They are built into WordPress &mdash; no extra plugin needed.</p>
                <ol>
                    <li>Go to <strong>Users &rarr; Profile</strong> in your WordPress admin</li>
                    <li>Scroll to <strong>Application Passwords</strong></li>
                    <li>Enter a name like <code>MyStorey</code> and click <strong>Add New Application Password</strong></li>
                    <li>Copy the generated password &mdash; <strong>you will only see it once</strong></li>
                </ol>
                <a href="<?php echo esc_url( $profile_url ); ?>" class="ms-btn-secondary">
                    Open My Profile &rarr;
                </a>
            </div>

            <!-- Step 2 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">2</div>
                    <h2 class="ms-step-title">Register this site on MyStorey</h2>
                </div>
                <p>Open your MyStorey dashboard and add this site. Copy your WordPress URL below and paste it along with the Application Password you just created.</p>

                <div class="ms-field-label">Your WordPress URL</div>
                <div class="ms-copy-row" style="margin-bottom:20px;">
                    <div class="ms-code"><?php echo esc_html( $site_url ); ?></div>
                    <button class="ms-btn-copy" onclick="msCopy('<?php echo esc_js( $site_url ); ?>', this)">Copy</button>
                </div>

                <a href="<?php echo esc_url( $dash_url ); ?>" class="ms-btn-primary" target="_blank" rel="noopener">
                    Open MyStorey Dashboard &rarr;
                </a>
            </div>

            <!-- Step 3 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">3</div>
                    <h2 class="ms-step-title">Connect your AI assistant</h2>
                </div>
                <p>After registering your site you will get an <strong>MCP Token</strong> in your MyStorey dashboard. Paste the URL and token below into Claude.ai, ChatGPT, or any MCP-compatible AI:</p>

                <div class="ms-field-label">MCP Server URL</div>
                <div class="ms-copy-row" style="margin-bottom:20px;">
                    <div class="ms-code"><?php echo esc_html( $mcp_url ); ?></div>
                    <button class="ms-btn-copy" onclick="msCopy('<?php echo esc_js( $mcp_url ); ?>', this)">Copy</button>
                </div>

                <div class="ms-token-note">
                    Your <strong>MCP Token</strong> (used as the API key / Bearer token) is shown in your
                    <a href="<?php echo esc_url( $dash_url ); ?>" target="_blank" rel="noopener">MyStorey dashboard</a>
                    after you register this site.
                </div>
            </div>

        </div><!-- .ms-steps -->

        <div class="ms-footer">
            <strong>Need help?</strong> Visit
            <a href="<?php echo esc_url( MYSTOREY_URL . '/wordpress' ); ?>" target="_blank" rel="noopener">
                <?php echo esc_html( MYSTOREY_URL ); ?>/wordpress
            </a> for the full setup guide.
        </div>

    </div><!-- .ms-wrap -->
    <?php
}
"""

_PLUGIN_README = """=== MyStorey – AI Content Control ===
Contributors: mystorey
Tags: ai, mcp, claude, chatgpt, content
Requires at least: 5.6
Tested up to: 6.7
Stable tag: 1.0.0
License: GPLv2 or later

Control your WordPress content via Claude.ai, ChatGPT, or any MCP-compatible AI assistant.

== Description ==
MyStorey acts as a bridge between your AI assistant and WordPress. Install this plugin, create
an Application Password, register on MyStorey, and start telling your AI what to write.

== Installation ==
1. Upload the plugin zip via Plugins → Add New → Upload Plugin
2. Activate the plugin
3. Go to Settings → MyStorey AI and follow the 3-step setup

== Changelog ==
= 1.0.0 =
* Initial release
"""


@router.get("/plugin/download")
async def download_plugin(request: Request) -> Response:
    """Generate and serve the WordPress plugin zip with the server URL baked in."""
    server_url = str(request.base_url).rstrip("/")
    php_content = _PLUGIN_PHP_TEMPLATE.replace("{{MYSTOREY_URL}}", server_url)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mystorey-connector/mystorey-connector.php", php_content)
        zf.writestr("mystorey-connector/readme.txt", _PLUGIN_README)
    buf.seek(0)

    return Response(
        content=buf.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=mystorey-connector.zip"},
    )


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


@router.post("/sites/{site_id}/test")
async def test_wordpress_site(
    site_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Test the live connection to a registered WordPress site."""
    result = await db.execute(
        select(WordPressSite).where(WordPressSite.id == site_id)
    )
    db_site = result.scalar_one_or_none()
    if not db_site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress site not found")
    if db_site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    client = WordPressClient(
        site_url=str(db_site.site_url),
        username=str(db_site.app_username),
        password=str(db_site.app_password_encrypted),
    )
    try:
        user_info = await client.verify_credentials()
        roles: list[str] = user_info.get("roles", [])
        can_write = any(r in roles for r in ("administrator", "editor", "author"))
        name = user_info.get("name") or user_info.get("slug") or str(db_site.app_username)
        if not can_write:
            return {
                "ok": False,
                "error": (
                    f"Connected as '{name}' (role: {', '.join(roles) or 'unknown'}) — "
                    "this user cannot create or edit posts. "
                    "Use an Administrator or Editor account."
                ),
            }
        return {"ok": True, "site_name": str(db_site.site_name), "site_url": str(db_site.site_url), "wp_user": name, "roles": roles}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


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
