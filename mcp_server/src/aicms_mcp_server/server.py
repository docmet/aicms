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


class MCPServer:
    def __init__(self, api_url: str, api_token: str, app_url: str = ""):
        self.server = Server("aicms-mcp")
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.app_url = app_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def _preview_url(self, site_id: str, page_id: str) -> str | None:
        """Return the draft preview URL, or None if app_url is not configured."""
        if not self.app_url:
            return None
        return f"{self.app_url}/preview/{site_id}/{page_id}"

        # Register handlers
        self.server.list_tools = self.handle_list_tools
        self.server.call_tool = self.handle_call_tool
        self.server.list_resources = self.handle_list_resources
        self.server.list_prompts = self.handle_list_prompts

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make authenticated request to AI CMS API."""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

    # ── Tool definitions ───────────────────────────────────────────────────

    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        tools = [
            # ── Sites ──────────────────────────────────────────────────────
            Tool(
                name="list_sites",
                description="List all sites for the authenticated user",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="create_site",
                description="Create a new site with name and slug",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Display name"},
                        "slug": {"type": "string", "description": "Unique URL slug"},
                        "theme_slug": {"type": "string", "description": "Theme (default: 'default')"},
                    },
                    "required": ["name", "slug"],
                },
            ),
            Tool(
                name="get_site_info",
                description="Get detailed information about a site including pages and theme",
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
                    "Get a full structured description of a site: theme, all pages, "
                    "section types and their draft content. Use this to understand what "
                    "already exists before making changes."
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
                name="update_site",
                description="Update site name, slug, or theme",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                        "theme_slug": {"type": "string"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="delete_site",
                description="Delete a site and all its pages",
                inputSchema={
                    "type": "object",
                    "properties": {"site_id": {"type": "string"}},
                    "required": ["site_id"],
                },
            ),
            # ── Pages ──────────────────────────────────────────────────────
            Tool(
                name="list_pages",
                description="List all pages for a site",
                inputSchema={
                    "type": "object",
                    "properties": {"site_id": {"type": "string"}},
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="create_page",
                description="Create a new page on a site",
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
                description="Update page title, slug, or publish status",
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
                description="Delete a page and its content",
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
                    "Publish a page: copies all draft content to published, makes it live. "
                    "Always call this after updating content sections to make changes visible."
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
                description="Get draft content sections for a page",
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
                    "Create or update a content section on a page using structured JSON. "
                    "The content_json must match the schema for the section_type. "
                    f"Valid section types: {', '.join(VALID_SECTION_TYPES)}. "
                    "After calling this, call publish_page to make the change live."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "section_type": {
                            "type": "string",
                            "enum": VALID_SECTION_TYPES,
                            "description": "Type of section to create/update",
                        },
                        "content_json": {
                            "type": "object",
                            "description": "Content data object matching the section type schema",
                        },
                        "order": {
                            "type": "integer",
                            "description": "Display order (0-based). Defaults to 0.",
                        },
                    },
                    "required": ["site_id", "page_id", "section_type", "content_json"],
                },
            ),
            Tool(
                name="generate_section",
                description=(
                    "Generate a content section with sensible defaults for a given type. "
                    "Returns the default JSON structure you can inspect and then pass to update_section. "
                    f"Valid types: {', '.join(VALID_SECTION_TYPES)}."
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
                description="Delete a content section by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "section_id": {"type": "string", "description": "UUID of the section"},
                    },
                    "required": ["site_id", "page_id", "section_id"],
                },
            ),
            # ── Themes ─────────────────────────────────────────────────────
            Tool(
                name="list_themes",
                description="List available themes",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="apply_theme",
                description="Apply a theme to a site",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "theme_slug": {"type": "string"},
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
            return CallToolResult(
                content=[TextContent(type="text", text=f"API error {e.response.status_code}: {e.response.text}")],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    async def _dispatch(self, tool_name: str, args: Dict[str, Any]) -> CallToolResult:

        # ── list_sites ────────────────────────────────────────────────────
        if tool_name == "list_sites":
            data = await self._make_request("GET", "/sites")
            if not data:
                return self._text("You have no sites yet.")
            lines = [f"- {s['name']} (slug: {s['slug']}, theme: {s['theme_slug']}, id: {s['id']})" for s in data]
            return self._text("Your sites:\n" + "\n".join(lines))

        # ── create_site ───────────────────────────────────────────────────
        elif tool_name == "create_site":
            data = await self._make_request(
                "POST",
                "/sites",
                json={
                    "name": args["name"],
                    "slug": args["slug"],
                    "theme_slug": args.get("theme_slug", "default"),
                },
            )
            return self._text(
                f"Site '{data['name']}' created. ID: {data['id']}, URL slug: {data['slug']}, theme: {data['theme_slug']}"
            )

        # ── get_site_info ─────────────────────────────────────────────────
        elif tool_name == "get_site_info":
            site_id = args["site_id"]
            site = await self._make_request("GET", f"/sites/{site_id}")
            pages = await self._make_request("GET", f"/sites/{site_id}/pages")
            pages_text = "\n".join(
                f"  - {p['title']} (slug: /{p['slug']}, published: {p['is_published']}, id: {p['id']})"
                for p in pages
            ) if pages else "  No pages yet"
            return self._text(
                f"Site: {site['name']}\nSlug: {site['slug']}\nTheme: {site['theme_slug']}\nID: {site['id']}\n\nPages:\n{pages_text}"
            )

        # ── describe_site ─────────────────────────────────────────────────
        elif tool_name == "describe_site":
            site_id = args["site_id"]
            site = await self._make_request("GET", f"/sites/{site_id}")
            pages = await self._make_request("GET", f"/sites/{site_id}/pages")

            lines = [
                f"# {site['name']}",
                f"Slug: {site['slug']} | Theme: {site['theme_slug']} | ID: {site['id']}",
                "",
            ]

            for page in pages:
                pid = page["id"]
                pub_str = "published" if page["is_published"] else "draft"
                preview_url = self._preview_url(site_id, pid)
                page_header = f"## Page: {page['title']} (/{page['slug']}) [{pub_str}] id={pid}"
                if preview_url:
                    page_header += f" | preview: {preview_url}"
                lines.append(page_header)
                try:
                    sections = await self._make_request("GET", f"/sites/{site_id}/pages/{pid}/content")
                except Exception:
                    sections = []

                if not sections:
                    lines.append("  (no sections)")
                else:
                    for s in sections:
                        unpub = " [unpublished changes]" if s.get("has_unpublished_changes") else ""
                        draft = s.get("content_draft") or ""
                        # Pretty-print if valid JSON
                        try:
                            content_preview = json.dumps(json.loads(draft), indent=2)
                        except Exception:
                            content_preview = draft[:200]
                        lines.append(f"  ### {s['section_type']} (order={s.get('order', 0)}, id={s['id']}){unpub}")
                        lines.append(f"  ```json\n  {content_preview}\n  ```")
                lines.append("")

            return self._text("\n".join(lines))

        # ── update_site ───────────────────────────────────────────────────
        elif tool_name == "update_site":
            site_id = args["site_id"]
            patch = {k: args[k] for k in ("name", "slug", "theme_slug") if k in args}
            await self._make_request("PATCH", f"/sites/{site_id}", json=patch)
            return self._text(f"Site {site_id} updated: {patch}")

        # ── delete_site ───────────────────────────────────────────────────
        elif tool_name == "delete_site":
            await self._make_request("DELETE", f"/sites/{args['site_id']}")
            return self._text(f"Site {args['site_id']} deleted.")

        # ── list_pages ────────────────────────────────────────────────────
        elif tool_name == "list_pages":
            site_id = args["site_id"]
            pages = await self._make_request("GET", f"/sites/{site_id}/pages")
            if not pages:
                return self._text("No pages found for this site.")
            lines = [
                f"- {p['title']} (/{p['slug']}, published: {p['is_published']}, id: {p['id']})"
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
            return self._text(f"Page '{data['title']}' created. ID: {data['id']}, slug: /{data['slug']}")

        # ── update_page ───────────────────────────────────────────────────
        elif tool_name == "update_page":
            site_id = args["site_id"]
            page_id = args["page_id"]
            patch = {k: args[k] for k in ("title", "slug", "is_published") if k in args}
            await self._make_request("PATCH", f"/sites/{site_id}/pages/{page_id}", json=patch)
            return self._text(f"Page {page_id} updated: {patch}")

        # ── delete_page ───────────────────────────────────────────────────
        elif tool_name == "delete_page":
            await self._make_request("DELETE", f"/sites/{args['site_id']}/pages/{args['page_id']}")
            return self._text(f"Page {args['page_id']} deleted.")

        # ── publish_page ──────────────────────────────────────────────────
        elif tool_name == "publish_page":
            site_id = args["site_id"]
            page_id = args["page_id"]
            data = await self._make_request("POST", f"/sites/{site_id}/pages/{page_id}/publish")
            section_count = len(data.get("sections", []))
            return self._text(
                f"Page published successfully. {section_count} section(s) are now live."
            )

        # ── get_page_content ──────────────────────────────────────────────
        elif tool_name == "get_page_content":
            site_id = args["site_id"]
            page_id = args["page_id"]
            page = await self._make_request("GET", f"/sites/{site_id}/pages/{page_id}")
            sections = await self._make_request("GET", f"/sites/{site_id}/pages/{page_id}/content")

            preview_url = self._preview_url(site_id, page_id)
            lines = [
                f"Page: {page['title']} (/{page['slug']}, published: {page['is_published']})",
                *([ f"Preview draft: {preview_url}" ] if preview_url else []),
                "",
            ]

            if not sections:
                lines.append("No content sections yet.")
            else:
                for s in sections:
                    unpub = " [has unpublished changes]" if s.get("has_unpublished_changes") else ""
                    lines.append(f"## {s['section_type']} (order={s.get('order', 0)}, id={s['id']}){unpub}")
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
            content_json = args["content_json"]
            order = args.get("order", 0)

            # Use the upsert-by-type endpoint — idempotent, MCP-friendly
            await self._make_request(
                "PUT",
                f"/sites/{site_id}/pages/{page_id}/content/by-type/{section_type}",
                json={"content_draft": json.dumps(content_json), "order": order},
            )
            preview_url = self._preview_url(site_id, page_id)
            preview_hint = f"\nPreview draft: {preview_url}" if preview_url else ""
            return self._text(
                f"Section '{section_type}' updated on page {page_id}. "
                f"Call publish_page to make this change live.{preview_hint}"
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
                f"Default content structure for '{section_type}':\n\n"
                f"```json\n{json.dumps(default, indent=2)}\n```\n\n"
                f"Pass this (modified as needed) as content_json to update_section."
            )

        # ── delete_section ────────────────────────────────────────────────
        elif tool_name == "delete_section":
            site_id = args["site_id"]
            page_id = args["page_id"]
            section_id = args["section_id"]
            await self._make_request("DELETE", f"/sites/{site_id}/pages/{page_id}/content/{section_id}")
            return self._text(f"Section {section_id} deleted.")

        # ── list_themes ───────────────────────────────────────────────────
        elif tool_name == "list_themes":
            data = await self._make_request("GET", "/themes")
            lines = [f"- {t['slug']}: {t.get('description', 'No description')}" for t in data]
            return self._text("Available themes:\n" + "\n".join(lines))

        # ── apply_theme ───────────────────────────────────────────────────
        elif tool_name == "apply_theme":
            site_id = args["site_id"]
            theme_slug = args["theme_slug"]
            await self._make_request("PATCH", f"/sites/{site_id}", json={"theme_slug_draft": theme_slug})
            return self._text(
                f"Theme '{theme_slug}' staged as draft on site {site_id}. "
                "Call publish_page to make the theme change live on the public site."
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
        return ListPromptsResult(prompts=[])


def create_server(api_url: str, api_token: str, app_url: str = "") -> MCPServer:
    return MCPServer(api_url, api_token, app_url)


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI CMS MCP Server")
    parser.add_argument(
        "--api-url",
        default=os.getenv("AICMS_API_URL", "http://localhost:8000/api"),
        help="AI CMS API base URL (default: http://localhost:8000/api)",
    )
    parser.add_argument(
        "--api-token",
        default=os.getenv("AICMS_API_TOKEN"),
        help="AI CMS API bearer token",
    )
    parser.add_argument(
        "--app-url",
        default=os.getenv("APP_URL", ""),
        help="Public frontend URL for preview links (e.g. https://mystorey.io)",
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
