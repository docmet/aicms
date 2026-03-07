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

add_action( 'admin_enqueue_scripts', function( $hook ) {
    if ( $hook !== 'settings_page_mystorey-connector' ) return;
    wp_add_inline_script( 'jquery-core', '
        function mystoreyCopy(text, btn) {
            navigator.clipboard.writeText(text).then(function() {
                var orig = btn.textContent;
                btn.textContent = "Copied!";
                btn.style.background = "#00a32a";
                setTimeout(function() {
                    btn.textContent = orig;
                    btn.style.background = "";
                }, 2000);
            });
        }
    ' );
});

function mystorey_copy_button( $text, $label = 'Copy' ) {
    $esc = esc_attr( $text );
    return '<button type="button" class="button button-small"
        style="margin-left:8px;vertical-align:middle;"
        onclick="mystoreyCopy(\'' . $esc . '\', this)">' . esc_html( $label ) . '</button>';
}

function mystorey_settings_page() {
    $site_url = get_site_url();
    ?>
    <div class="wrap">
        <h1>MyStorey &#8211; AI Content Control</h1>
        <p>Connect this WordPress site to MyStorey so your AI assistant can write and publish content directly.</p>

        <hr/>

        <h2>Step 1 &#8212; Create an Application Password</h2>
        <p>Application Passwords let MyStorey connect to WordPress securely, without using your admin password.</p>
        <ol>
            <li>Go to <strong>Users &#8594; Profile</strong> in your WordPress admin</li>
            <li>Scroll to <strong>Application Passwords</strong></li>
            <li>Enter a name like <code>MyStorey</code> and click <strong>Add New Application Password</strong></li>
            <li>Copy the generated password &#8212; <strong>you will only see it once</strong></li>
        </ol>
        <p>
            <a href="<?php echo esc_url( admin_url( 'profile.php' ) ); ?>#application-passwords-section"
               class="button button-secondary">Open My Profile &#8594;</a>
        </p>

        <hr/>

        <h2>Step 2 &#8212; Register on MyStorey</h2>
        <p>Open the MyStorey dashboard and register this site. Use the values below:</p>

        <table class="form-table" role="presentation">
            <tr>
                <th scope="row">Your WordPress URL</th>
                <td>
                    <code style="font-size:13px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( $site_url ); ?>
                    </code>
                    <?php echo mystorey_copy_button( $site_url, 'Copy URL' ); ?>
                </td>
            </tr>
        </table>

        <p style="margin-top:16px;">
            <a href="<?php echo esc_url( MYSTOREY_DASHBOARD_URL ); ?>"
               class="button button-primary" target="_blank" rel="noopener">
                Open MyStorey Dashboard &#8594;
            </a>
        </p>

        <hr/>

        <h2>Step 3 &#8212; Connect Your AI</h2>
        <p>After registering your site on MyStorey you will receive an <strong>MCP Token</strong>.
           Paste the values below into Claude.ai, ChatGPT (Developer mode), or any MCP-compatible AI:</p>

        <table class="form-table" role="presentation">
            <tr>
                <th scope="row">MCP URL</th>
                <td>
                    <code style="font-size:13px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( MYSTOREY_MCP_URL ); ?>
                    </code>
                    <?php echo mystorey_copy_button( MYSTOREY_MCP_URL, 'Copy URL' ); ?>
                    <p class="description">Paste this as the MCP server URL in your AI client.</p>
                </td>
            </tr>
            <tr>
                <th scope="row">MCP Token</th>
                <td>
                    <em>Available in your
                        <a href="<?php echo esc_url( MYSTOREY_DASHBOARD_URL ); ?>" target="_blank" rel="noopener">
                            MyStorey dashboard
                        </a>
                        after registering this site.
                    </em>
                    <p class="description">Use this as the Bearer token / API key in your AI client.</p>
                </td>
            </tr>
        </table>

        <hr/>

        <p>
            <strong>Need help?</strong>
            Visit <a href="<?php echo esc_url( MYSTOREY_URL ); ?>/wordpress" target="_blank" rel="noopener">
                <?php echo esc_html( MYSTOREY_URL ); ?>/wordpress
            </a> for the full setup guide.
        </p>
    </div>
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
