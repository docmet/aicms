import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# ── Default JSON structures per section type ────────────────────────────────
SECTION_DEFAULTS: Dict[str, Any] = {
    "hero": {
        "headline": "Welcome",
        "subheadline": "",
        "badge": "",
        "cta_primary": {"label": "Get Started", "href": "#"},
        "cta_secondary": {"label": "Learn More", "href": "#"},
    },
    "features": {
        "headline": "Features",
        "subheadline": "",
        "items": [
            {"icon": "⚡", "title": "Fast", "description": "Blazing fast performance"},
            {"icon": "🔒", "title": "Secure", "description": "Enterprise-grade security"},
            {"icon": "📱", "title": "Responsive", "description": "Works on every device"},
        ],
    },
    "testimonials": {
        "headline": "What our customers say",
        "items": [
            {"quote": "This is amazing!", "name": "Jane Doe", "role": "CEO", "company": "Acme Inc"},
        ],
    },
    "about": {
        "headline": "About Us",
        "body": "We are a company dedicated to excellence.",
        "stats": [
            {"number": "500+", "label": "Customers"},
            {"number": "99%", "label": "Satisfaction"},
        ],
    },
    "contact": {
        "headline": "Get in Touch",
        "email": "hello@example.com",
        "phone": "",
        "address": "",
        "hours": "",
    },
    "cta": {
        "headline": "Ready to get started?",
        "subheadline": "Join thousands of happy customers.",
        "button_label": "Start Free Trial",
        "button_href": "#",
    },
    "pricing": {
        "headline": "Simple Pricing",
        "subheadline": "No hidden fees.",
        "plans": [
            {"name": "Starter", "price": "Free", "features": ["5 sites", "Basic support"], "cta_label": "Get started", "highlighted": False},
            {"name": "Pro", "price": "$29", "period": "/month", "features": ["Unlimited sites", "Priority support", "Analytics"], "cta_label": "Start free trial", "highlighted": True},
        ],
    },
    "custom": {"title": "Custom Section", "content": ""},
}

VALID_SECTION_TYPES = list(SECTION_DEFAULTS.keys())

THEME_DESCRIPTIONS = {
    "modern": "clean blue tones, great for tech and SaaS",
    "warm": "orange and earthy palette, inviting feel — good for services or local businesses",
    "startup": "emerald greens, energetic and growth-focused",
    "minimal": "neutral zinc, lets the content breathe — ideal for portfolios",
    "dark": "deep violet, bold and premium — great for agencies or creative studios",
    "default": "balanced neutral default",
    "nature": "organic greens, alias for startup",
}


class MCPServer:
    def __init__(self, api_url: str, api_token: str, app_url: str = ""):
        self.server = Server("aicms-mcp")
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.app_url = app_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def _preview_url(self, site_id: str, page_id: str) -> str | None:
        if not self.app_url:
            return None
        return f"{self.app_url}/preview/{site_id}/{page_id}"

        # Register handlers
        self.server.list_tools = self.handle_list_tools
        self.server.call_tool = self.handle_call_tool
        self.server.list_resources = self.handle_list_resources
        self.server.list_prompts = self.handle_list_prompts

    async def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                **kwargs,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()

    # ── Tool definitions ───────────────────────────────────────────────────

    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        tools = [
            # ── Sites ──────────────────────────────────────────────────────
            Tool(
                name="list_sites",
                description=(
                    "List all the user's sites. Use this at the start of a conversation to "
                    "understand what they've already built. If they have sites, ask which one "
                    "they want to work on, or offer a quick overview. If no sites exist, "
                    "suggest creating one and ask about their business."
                ),
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="create_site",
                description=(
                    "Create a new site. Before calling, ask: what is the site for, "
                    "what industry/vibe, what URL slug? Good slugs are short, lowercase, no spaces "
                    "(e.g. 'acme-coffee'). After creation, offer to build out the homepage."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Display name, e.g. 'Acme Coffee'"},
                        "slug": {"type": "string", "description": "URL slug, e.g. 'acme-coffee'"},
                        "theme_slug": {
                            "type": "string",
                            "description": (
                                "Initial theme. Options: modern (blue, tech/SaaS), warm (orange, services/local), "
                                "startup (emerald, growth), minimal (neutral, portfolio), dark (violet, agency). "
                                "Pick based on the user's industry rather than defaulting to 'default'."
                            ),
                        },
                    },
                    "required": ["name", "slug"],
                },
            ),
            Tool(
                name="get_site_info",
                description=(
                    "Get basic info about a site (name, slug, theme, pages). "
                    "Use describe_site when you need to actually read section content."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="describe_site",
                description=(
                    "Get a full snapshot of a site: theme (published + draft), all pages, "
                    "and the draft content of every section. Always call this before suggesting "
                    "improvements or making edits — you need to see what's already there. "
                    "After reading, offer specific observations: what looks strong, what's missing, "
                    "what copy could be stronger."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="update_site",
                description=(
                    "Update the site's display name or URL slug. "
                    "To change the theme, use apply_theme instead — it goes through the draft workflow. "
                    "Confirm slug changes with the user since they change the public URL."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "name": {"type": "string", "description": "New display name"},
                        "slug": {"type": "string", "description": "New URL slug — confirm with user first, changes public URL"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="delete_site",
                description=(
                    "Permanently delete a site and all its pages. "
                    "Always confirm with the user before calling — this cannot be undone."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {"site_id": {"type": "string"}},
                    "required": ["site_id"],
                },
            ),
            # ── Pages ──────────────────────────────────────────────────────
            Tool(
                name="list_pages",
                description=(
                    "List all pages on a site. Good for understanding structure. "
                    "Common pages to suggest if missing: Home, About, Services/Pricing, Contact. "
                    "Offer to help add any that are missing."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {"site_id": {"type": "string"}},
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="create_page",
                description=(
                    "Create a new page. After creating, offer to add sections right away. "
                    "Suggest relevant section types based on the page purpose "
                    "(About → about + contact; Pricing → pricing + cta; Home → hero + features + cta)."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "title": {"type": "string"},
                        "slug": {"type": "string"},
                        "is_published": {"type": "boolean", "description": "Default false"},
                    },
                    "required": ["site_id", "title", "slug"],
                },
            ),
            Tool(
                name="update_page",
                description="Update page title, slug, or publish status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "title": {"type": "string"},
                        "slug": {"type": "string"},
                        "is_published": {"type": "boolean"},
                    },
                    "required": ["site_id", "page_id"],
                },
            ),
            Tool(
                name="delete_page",
                description="Delete a page. Confirm with the user if the page has content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                    },
                    "required": ["site_id", "page_id"],
                },
            ),
            Tool(
                name="publish_page",
                description=(
                    "Make all draft changes live — sections and any staged theme. "
                    "Always call this after updating content, unless the user wants to keep it as a draft. "
                    "After publishing, share the live URL and ask if anything needs tweaking."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                    },
                    "required": ["site_id", "page_id"],
                },
            ),
            # ── Content sections ───────────────────────────────────────────
            Tool(
                name="get_page_content",
                description=(
                    "Get draft content for all sections on a page. "
                    "Always call this before editing so you make targeted changes "
                    "instead of accidentally overwriting fields the user hasn't asked to change."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                    },
                    "required": ["site_id", "page_id"],
                },
            ),
            Tool(
                name="update_section",
                description=(
                    "Create or update a content section (upsert by type — safe to call multiple times). "
                    f"Valid section types: {', '.join(VALID_SECTION_TYPES)}. "
                    "Read current content first (get_page_content) to preserve fields not being changed. "
                    "Write copy that is specific, human, and relevant to the user's actual business — "
                    "no generic filler. After updating, ask if the tone and wording feel right."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "section_type": {
                            "type": "string",
                            "enum": VALID_SECTION_TYPES,
                        },
                        "content_json": {
                            "type": "object",
                            "description": "Full content object for this section type",
                        },
                        "order": {
                            "type": "integer",
                            "description": "Display order (0 = top). Typical: hero(0), features(1), testimonials(2), about(3), cta(4).",
                        },
                    },
                    "required": ["site_id", "page_id", "section_type", "content_json"],
                },
            ),
            Tool(
                name="generate_section",
                description=(
                    "Get the default content structure for a section type — useful for "
                    "understanding available fields before writing real content."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "section_type": {
                            "type": "string",
                            "enum": VALID_SECTION_TYPES,
                        },
                    },
                    "required": ["section_type"],
                },
            ),
            Tool(
                name="delete_section",
                description=(
                    "Delete a section by its ID. Get the ID from get_page_content. "
                    "Confirm before deleting sections that contain real content."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "section_id": {"type": "string", "description": "UUID from get_page_content"},
                    },
                    "required": ["site_id", "page_id", "section_id"],
                },
            ),
            # ── Versions ───────────────────────────────────────────────────
            Tool(
                name="list_versions",
                description=(
                    "List the published version history for a page (newest first, up to 5). "
                    "Call this before reverting so you can show the user their options "
                    "and let them choose which version to restore."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                    },
                    "required": ["site_id", "page_id"],
                },
            ),
            Tool(
                name="revert_to_version",
                description=(
                    "Revert all draft content (sections + theme) back to a previously published version. "
                    "Always call list_versions first to show the user their options and confirm which version. "
                    "This updates the draft — call publish_page after to make the reverted content live."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "version_id": {"type": "string", "description": "Version UUID from list_versions"},
                    },
                    "required": ["site_id", "page_id", "version_id"],
                },
            ),
            # ── Themes ─────────────────────────────────────────────────────
            Tool(
                name="list_themes",
                description=(
                    "List available themes with their visual personality. "
                    "Use when the user wants to change the look, or proactively suggest a theme "
                    "that fits their industry (e.g. warm for a coffee shop, startup for SaaS, dark for an agency)."
                ),
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="apply_theme",
                description=(
                    "Stage a theme as a draft — immediately visible in preview, not live until publish_page. "
                    "Suggest a theme based on the user's industry/vibe if they haven't specified one. "
                    "Available: modern (blue, tech), warm (orange, services), startup (emerald, growth), "
                    "minimal (neutral, portfolio), dark (violet, agency)."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "theme_slug": {
                            "type": "string",
                            "enum": ["modern", "warm", "startup", "minimal", "dark", "default"],
                        },
                    },
                    "required": ["site_id", "theme_slug"],
                },
            ),
        ]
        return ListToolsResult(tools=tools)

    # ── Tool implementations ───────────────────────────────────────────────

    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        tool_name = request.params.name
        args = request.params.arguments or {}

        try:
            return await self._dispatch(tool_name, args)
        except httpx.HTTPStatusError as e:
            body = e.response.text
            if "plan_limit_reached" in body:
                parts = body.split(":")
                plan = parts[1] if len(parts) > 1 else "current"
                limit = parts[2].strip('"}') if len(parts) > 2 else "?"
                return CallToolResult(
                    content=[TextContent(type="text", text=(
                        f"The {plan} plan allows a maximum of {limit} site(s). "
                        "The user would need to upgrade to create more sites."
                    ))],
                    isError=True,
                )
            return CallToolResult(
                content=[TextContent(type="text", text=f"API error {e.response.status_code}: {body}")],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    async def _dispatch(self, tool_name: str, args: Dict[str, Any]) -> CallToolResult:  # noqa: C901

        # ── list_sites ────────────────────────────────────────────────────
        if tool_name == "list_sites":
            data = await self._make_request("GET", "/sites")
            if not data:
                return self._text(
                    "No sites yet — blank slate! "
                    "Tell me what the site is for and I can get it up in minutes."
                )
            lines = []
            for s in data:
                theme_info = s["theme_slug"]
                if s.get("theme_slug_draft") and s["theme_slug_draft"] != s["theme_slug"]:
                    theme_info += f" (draft: {s['theme_slug_draft']})"
                lines.append(f"- **{s['name']}** — slug: `{s['slug']}`, theme: {theme_info}, id: `{s['id']}`")
            return self._text("Here are your sites:\n\n" + "\n".join(lines))

        # ── create_site ───────────────────────────────────────────────────
        elif tool_name == "create_site":
            data = await self._make_request(
                "POST",
                "/sites",
                json={
                    "name": args["name"],
                    "slug": args["slug"],
                    "theme_slug": args.get("theme_slug", "modern"),
                },
            )
            theme = data["theme_slug"]
            desc = THEME_DESCRIPTIONS.get(theme, "")
            return self._text(
                f"**{data['name']}** created! (id: `{data['id']}`)\n"
                f"Slug: `{data['slug']}` | Theme: {theme}{f' — {desc}' if desc else ''}\n\n"
                f"The site is empty right now. Want me to build out the homepage? "
                f"Tell me a bit about the business — what it does, who it's for — "
                f"and I'll write the copy for hero, features, and a CTA."
            )

        # ── get_site_info ─────────────────────────────────────────────────
        elif tool_name == "get_site_info":
            site_id = args["site_id"]
            site, pages = await asyncio.gather(
                self._make_request("GET", f"/sites/{site_id}"),
                self._make_request("GET", f"/sites/{site_id}/pages"),
            )
            theme_line = f"Theme: {site['theme_slug']}"
            if site.get("theme_slug_draft") and site["theme_slug_draft"] != site["theme_slug"]:
                theme_line += f" | Draft theme staged: **{site['theme_slug_draft']}** (not published yet)"

            pages_text = "\n".join(
                f"  - **{p['title']}** (`/{p['slug']}`) {'✅ published' if p['is_published'] else '📝 draft'} — id: `{p['id']}`"
                for p in pages
            ) if pages else "  No pages yet."

            return self._text(
                f"**{site['name']}**\n"
                f"Slug: `{site['slug']}` | {theme_line}\n"
                f"ID: `{site['id']}`\n\n"
                f"Pages:\n{pages_text}"
            )

        # ── describe_site ─────────────────────────────────────────────────
        elif tool_name == "describe_site":
            site_id = args["site_id"]
            site, pages = await asyncio.gather(
                self._make_request("GET", f"/sites/{site_id}"),
                self._make_request("GET", f"/sites/{site_id}/pages"),
            )

            theme_line = f"Theme: **{site['theme_slug']}**"
            if site.get("theme_slug_draft") and site["theme_slug_draft"] != site["theme_slug"]:
                theme_line += f" | Staged draft: **{site['theme_slug_draft']}** (not published)"

            lines = [
                f"# {site['name']}",
                f"Slug: `{site['slug']}` | {theme_line} | ID: `{site['id']}`",
                "",
            ]

            for page in pages:
                pid = page["id"]
                pub_str = "✅ published" if page["is_published"] else "📝 draft"
                preview_url = self._preview_url(site_id, pid)
                header = f"## {page['title']} (`/{page['slug']}`) [{pub_str}] id=`{pid}`"
                if preview_url:
                    header += f"\nPreview: {preview_url}"
                lines.append(header)

                try:
                    sections = await self._make_request("GET", f"/sites/{site_id}/pages/{pid}/content")
                except Exception:
                    sections = []

                if not sections:
                    lines.append("  *(no sections yet)*")
                else:
                    for s in sections:
                        unpub = " ⚠️ unpublished changes" if s.get("has_unpublished_changes") else ""
                        draft = s.get("content_draft") or ""
                        try:
                            content_preview = json.dumps(json.loads(draft), indent=2)
                        except Exception:
                            content_preview = draft[:300]
                        lines.append(
                            f"\n### {s['section_type']} (order={s.get('order', 0)}, id=`{s['id']}`){unpub}\n"
                            f"```json\n{content_preview}\n```"
                        )
                lines.append("")

            return self._text("\n".join(lines))

        # ── update_site ───────────────────────────────────────────────────
        elif tool_name == "update_site":
            site_id = args["site_id"]
            patch = {k: args[k] for k in ("name", "slug") if k in args}
            if not patch:
                return self._text("Nothing to update — provide name or slug. To change the theme, use apply_theme.")
            await self._make_request("PATCH", f"/sites/{site_id}", json=patch)
            changes = ", ".join(f"{k} → `{v}`" for k, v in patch.items())
            return self._text(f"Updated: {changes}.")

        # ── delete_site ───────────────────────────────────────────────────
        elif tool_name == "delete_site":
            await self._make_request("DELETE", f"/sites/{args['site_id']}")
            return self._text("Site deleted.")

        # ── list_pages ────────────────────────────────────────────────────
        elif tool_name == "list_pages":
            site_id = args["site_id"]
            pages = await self._make_request("GET", f"/sites/{site_id}/pages")
            if not pages:
                return self._text(
                    "No pages yet. A typical site has: Home, About, Services/Pricing, Contact. "
                    "Want me to create any of these?"
                )
            lines = [
                f"- **{p['title']}** (`/{p['slug']}`) {'✅' if p['is_published'] else '📝 draft'} — id: `{p['id']}`"
                for p in pages
            ]
            return self._text("Pages:\n" + "\n".join(lines))

        # ── create_page ───────────────────────────────────────────────────
        elif tool_name == "create_page":
            data = await self._make_request(
                "POST",
                f"/sites/{args['site_id']}/pages",
                json={
                    "title": args["title"],
                    "slug": args["slug"],
                    "is_published": args.get("is_published", False),
                },
            )
            return self._text(
                f"Page **{data['title']}** created (slug: `/{data['slug']}`, id: `{data['id']}`). "
                f"It's empty — want me to add sections now?"
            )

        # ── update_page ───────────────────────────────────────────────────
        elif tool_name == "update_page":
            site_id = args["site_id"]
            page_id = args["page_id"]
            patch = {k: args[k] for k in ("title", "slug", "is_published") if k in args}
            await self._make_request("PATCH", f"/sites/{site_id}/pages/{page_id}", json=patch)
            changes = ", ".join(f"{k} → `{v}`" for k, v in patch.items())
            return self._text(f"Page updated: {changes}.")

        # ── delete_page ───────────────────────────────────────────────────
        elif tool_name == "delete_page":
            await self._make_request("DELETE", f"/sites/{args['site_id']}/pages/{args['page_id']}")
            return self._text("Page deleted.")

        # ── publish_page ──────────────────────────────────────────────────
        elif tool_name == "publish_page":
            site_id = args["site_id"]
            page_id = args["page_id"]
            page = await self._make_request("POST", f"/sites/{site_id}/pages/{page_id}/publish")

            try:
                sections = await self._make_request("GET", f"/sites/{site_id}/pages/{page_id}/content")
                section_summary = f"{len(sections)} section(s)" if sections else "changes"
            except Exception:
                section_summary = "changes"

            preview_url = self._preview_url(site_id, page_id)
            live_hint = f"\n\nLive at: {preview_url}" if preview_url else ""
            return self._text(
                f"**{page['title']}** published! {section_summary} are now live.{live_hint}\n\n"
                f"Want to make any other tweaks?"
            )

        # ── get_page_content ──────────────────────────────────────────────
        elif tool_name == "get_page_content":
            site_id = args["site_id"]
            page_id = args["page_id"]
            page, sections = await asyncio.gather(
                self._make_request("GET", f"/sites/{site_id}/pages/{page_id}"),
                self._make_request("GET", f"/sites/{site_id}/pages/{page_id}/content"),
            )

            preview_url = self._preview_url(site_id, page_id)
            lines = [
                f"**{page['title']}** (`/{page['slug']}`) {'✅ published' if page['is_published'] else '📝 draft'}",
                *([ f"Preview: {preview_url}" ] if preview_url else []),
                "",
            ]

            if not sections:
                lines.append("No sections yet.")
            else:
                unpublished = [s for s in sections if s.get("has_unpublished_changes")]
                if unpublished:
                    lines.append(f"⚠️  {len(unpublished)} section(s) have unpublished changes.\n")
                for s in sections:
                    flag = " ⚠️ draft" if s.get("has_unpublished_changes") else ""
                    lines.append(f"### {s['section_type']} (order={s.get('order', 0)}, id=`{s['id']}`){flag}")
                    draft = s.get("content_draft") or ""
                    try:
                        lines.append(json.dumps(json.loads(draft), indent=2))
                    except Exception:
                        lines.append(draft)
                    lines.append("")

            return self._text("\n".join(lines))

        # ── update_section ────────────────────────────────────────────────
        elif tool_name == "update_section":
            site_id = args["site_id"]
            page_id = args["page_id"]
            section_type = args["section_type"]
            content_json = args.get("content_json") or args.get("content")
            order = args.get("order")

            payload: Dict[str, Any] = {"content_draft": json.dumps(content_json)}
            if order is not None:
                payload["order"] = order

            await self._make_request(
                "PUT",
                f"/sites/{site_id}/pages/{page_id}/content/by-type/{section_type}",
                json=payload,
            )
            preview_url = self._preview_url(site_id, page_id)
            preview_hint = f" Preview: {preview_url}" if preview_url else ""
            return self._text(
                f"**{section_type}** section updated.{preview_hint}\n\n"
                f"Does the copy feel right, or would you like to adjust the tone, phrasing, or any specific field?"
            )

        # ── generate_section ──────────────────────────────────────────────
        elif tool_name == "generate_section":
            section_type = args["section_type"]
            default = SECTION_DEFAULTS.get(section_type)
            if not default:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown section type: {section_type}")],
                    isError=True,
                )
            return self._text(
                f"Default structure for **{section_type}**:\n\n"
                f"```json\n{json.dumps(default, indent=2)}\n```\n\n"
                f"Pass a filled-in version as `content_json` to `update_section`."
            )

        # ── delete_section ────────────────────────────────────────────────
        elif tool_name == "delete_section":
            site_id = args["site_id"]
            page_id = args["page_id"]
            section_id = args["section_id"]
            await self._make_request("DELETE", f"/sites/{site_id}/pages/{page_id}/content/{section_id}")
            return self._text("Section deleted. Call publish_page if you want this removal to go live.")

        # ── list_versions ─────────────────────────────────────────────────
        elif tool_name == "list_versions":
            site_id = args["site_id"]
            page_id = args["page_id"]
            versions = await self._make_request("GET", f"/sites/{site_id}/pages/{page_id}/versions")
            if not versions:
                return self._text(
                    "No published versions yet — versions are created each time you publish (up to 5 kept)."
                )
            lines = []
            for v in versions:
                date = (v.get("published_at") or "")[:10]
                label = f" — {v['label']}" if v.get("label") else ""
                lines.append(f"- **v{v['version_number']}** ({date}){label} — id: `{v['id']}`")
            return self._text(
                "Published versions (newest first):\n\n" + "\n".join(lines) + "\n\n"
                "Use `revert_to_version` with a version id to restore one as draft."
            )

        # ── revert_to_version ─────────────────────────────────────────────
        elif tool_name == "revert_to_version":
            site_id = args["site_id"]
            page_id = args["page_id"]
            version_id = args["version_id"]

            # Check for staged theme draft before reverting
            site = await self._make_request("GET", f"/sites/{site_id}")
            has_theme_draft = bool(
                site.get("theme_slug_draft") and site["theme_slug_draft"] != site.get("theme_slug")
            )

            # Revert sections
            await self._make_request("POST", f"/sites/{site_id}/pages/{page_id}/revert/{version_id}")

            # Also clear any staged theme draft so the full state is reverted
            if has_theme_draft:
                await self._make_request("PATCH", f"/sites/{site_id}", json={"theme_slug_draft": None})

            theme_note = " Staged theme draft also cleared." if has_theme_draft else ""
            return self._text(
                f"Reverted to the selected version.{theme_note} "
                f"The draft has been restored — call `publish_page` to make it live.\n\n"
                f"Want me to publish it now, or would you like to review the content first?"
            )

        # ── list_themes ───────────────────────────────────────────────────
        elif tool_name == "list_themes":
            data = await self._make_request("GET", "/themes")
            lines = []
            for t in data:
                desc = THEME_DESCRIPTIONS.get(t["slug"], t.get("description", ""))
                lines.append(f"- **{t['slug']}**: {desc}")
            return self._text(
                "Available themes:\n\n" + "\n".join(lines) + "\n\n"
                "Apply one with `apply_theme`, then `publish_page` to make it live."
            )

        # ── apply_theme ───────────────────────────────────────────────────
        elif tool_name == "apply_theme":
            site_id = args["site_id"]
            theme_slug = args["theme_slug"]
            await self._make_request("PATCH", f"/sites/{site_id}", json={"theme_slug_draft": theme_slug})
            desc = THEME_DESCRIPTIONS.get(theme_slug, "")
            desc_note = f" ({desc})" if desc else ""
            return self._text(
                f"Theme **{theme_slug}**{desc_note} staged. "
                f"It's visible in the preview right now. "
                f"Call `publish_page` to make it live — this publishes all other pending changes too."
            )

        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")],
                isError=True,
            )

    @staticmethod
    def _text(msg: str) -> CallToolResult:
        return CallToolResult(content=[TextContent(type="text", text=msg)])

    async def handle_list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        return ListResourcesResult(resources=[])

    async def handle_list_prompts(self, request: ListPromptsRequest) -> ListPromptsResult:
        return ListPromptsResult(prompts=[
            Prompt(
                name="review_site",
                description="Get a full review of your site with improvement suggestions",
            ),
            Prompt(
                name="build_homepage",
                description="Guide to building a complete homepage from scratch",
            ),
            Prompt(
                name="whats_next",
                description="Ask what to work on next based on current site state",
            ),
        ])

    async def handle_get_prompt(self, request: GetPromptRequest) -> GetPromptResult:
        name = request.params.name

        if name == "review_site":
            return GetPromptResult(
                description="Review site content and suggest improvements",
                messages=[PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=(
                        "Please review my site. Use list_sites to find it, then describe_site to read all the content. "
                        "Tell me: what's working well, what's missing, what copy could be stronger, "
                        "and what I should add or change. Be specific — refer to actual text in my sections."
                    )),
                )],
            )

        if name == "build_homepage":
            return GetPromptResult(
                description="Build a complete homepage",
                messages=[PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=(
                        "Help me build a complete homepage. First ask me: what does my business do, "
                        "who is my target customer, and what makes me different from competitors? "
                        "Then use those answers to write compelling copy for hero, features, testimonials, and a CTA. "
                        "Let me review each section before publishing."
                    )),
                )],
            )

        if name == "whats_next":
            return GetPromptResult(
                description="Suggest next steps for the site",
                messages=[PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=(
                        "Look at my site using describe_site and tell me the single most impactful thing to do next. "
                        "Consider: missing sections, unpublished changes, missing pages, theme fit, copy quality. "
                        "Give me one concrete recommendation and offer to do it."
                    )),
                )],
            )

        return GetPromptResult(
            description=name,
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=name))],
        )


def create_server(api_url: str, api_token: str, app_url: str = "") -> MCPServer:
    return MCPServer(api_url, api_token, app_url)


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="MyStorey MCP Server")
    parser.add_argument(
        "--api-url",
        default=os.getenv("AICMS_API_URL", "http://localhost:8000/api"),
    )
    parser.add_argument(
        "--api-token",
        default=os.getenv("AICMS_API_TOKEN"),
    )
    parser.add_argument(
        "--app-url",
        default=os.getenv("APP_URL", ""),
        help="Frontend URL for preview links",
    )

    args = parser.parse_args()

    if not args.api_token:
        print("Error: API token required. Set AICMS_API_TOKEN or use --api-token")
        return

    server = create_server(args.api_url, args.api_token, args.app_url)

    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aicms-mcp",
                server_version="0.1.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
