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


class Site(BaseModel):
    id: str
    name: str
    slug: str
    theme_slug: str


class ContentSection(BaseModel):
    id: str
    section_type: str
    content: str


class Page(BaseModel):
    id: str
    title: str
    slug: str
    sections: List[ContentSection]


class MCPServer:
    def __init__(self, api_url: str, api_token: str):
        self.server = Server("aicms-mcp")
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}
        
        # Register handlers
        self.server.list_tools = self.handle_list_tools
        self.server.call_tool = self.handle_call_tool
        self.server.list_resources = self.handle_list_resources
        self.server.list_prompts = self.handle_list_prompts

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to AI CMS API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available MCP tools"""
        tools = [
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
                        "name": {"type": "string", "description": "Display name for the site"},
                        "slug": {"type": "string", "description": "Unique URL slug for the site"},
                        "theme_slug": {"type": "string", "description": "Theme to use (default: 'default')"},
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
                name="update_site",
                description="Update site name, slug, or theme",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site to update"},
                        "name": {"type": "string", "description": "New display name"},
                        "slug": {"type": "string", "description": "New URL slug"},
                        "theme_slug": {"type": "string", "description": "Theme slug to apply"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="delete_site",
                description="Delete a site and all its pages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site to delete"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="list_pages",
                description="List all pages for a site",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="create_page",
                description="Create a new page on a site",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site"},
                        "title": {"type": "string", "description": "Page title"},
                        "slug": {"type": "string", "description": "URL slug for the page"},
                        "is_published": {"type": "boolean", "description": "Whether page is published"},
                    },
                    "required": ["site_id", "title", "slug"],
                },
            ),
            Tool(
                name="get_page_content",
                description="Get content sections for a page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site (optional)"},
                        "page_id": {"type": "string", "description": "UUID of the page"},
                    },
                    "required": ["page_id"],
                },
            ),
            Tool(
                name="update_page_content",
                description="Update content for a page section (creates if doesn't exist)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site (optional)"},
                        "page_id": {"type": "string", "description": "UUID of the page"},
                        "section_type": {"type": "string", "description": "Type: hero, about, services, contact, etc."},
                        "content": {"type": "string", "description": "HTML or text content"},
                        "order": {"type": "integer", "description": "Display order"},
                    },
                    "required": ["page_id", "section_type", "content"],
                },
            ),
            Tool(
                name="update_page",
                description="Update page title, slug, or publish status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site (optional)"},
                        "page_id": {"type": "string", "description": "UUID of the page"},
                        "title": {"type": "string", "description": "New title"},
                        "slug": {"type": "string", "description": "New slug"},
                        "is_published": {"type": "boolean", "description": "Publish status"},
                    },
                    "required": ["page_id"],
                },
            ),
            Tool(
                name="delete_page",
                description="Delete a page and its content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "UUID of the site (optional)"},
                        "page_id": {"type": "string", "description": "UUID of the page"},
                    },
                    "required": ["page_id"],
                },
            ),
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
                        "site_id": {"type": "string", "description": "UUID of the site"},
                        "theme_slug": {"type": "string", "description": "Slug of the theme to apply"},
                    },
                    "required": ["site_id", "theme_slug"],
                },
            ),
        ]
        return ListToolsResult(tools=tools)

    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        tool_name = request.params.name
        args = request.params.arguments or {}

        try:
            if tool_name == "list_sites":
                data = await self._make_request("GET", "/sites")
                sites = [Site(**site) for site in data]
                content = "\n".join(
                    f"- {site.name} (slug: {site.slug}, theme: {site.theme_slug})"
                    for site in sites
                )
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Your sites:\n{content}")]
                )

            elif tool_name == "get_site_info":
                site_id = args["site_id"]
                data = await self._make_request("GET", f"/sites/{site_id}")
                site = Site(**data)
                
                # Get pages for the site
                pages_data = await self._make_request("GET", f"/sites/{site_id}/pages")
                pages_text = "\n".join(
                    f"  - {p['title']} (slug: {p['slug']}, published: {p['is_published']})"
                    for p in pages_data
                ) if pages_data else "  No pages yet"
                
                content = f"""Site: {site.name}
Slug: {site.slug}
Theme: {site.theme_slug}
ID: {site.id}

Pages:
{pages_text}"""
                return CallToolResult(
                    content=[TextContent(type="text", text=content)]
                )

            elif tool_name == "create_site":
                name = args["name"]
                slug = args["slug"]
                theme_slug = args.get("theme_slug", "default")
                
                data = await self._make_request(
                    "POST",
                    "/sites",
                    json={"name": name, "slug": slug, "theme_slug": theme_slug}
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Site '{name}' created successfully with slug '{slug}' and theme '{theme_slug}'"
                        )
                    ]
                )

            elif tool_name == "update_site":
                site_id = args["site_id"]
                update_data = {}
                if "name" in args:
                    update_data["name"] = args["name"]
                if "slug" in args:
                    update_data["slug"] = args["slug"]
                if "theme_slug" in args:
                    update_data["theme_slug"] = args["theme_slug"]
                
                await self._make_request(
                    "PATCH",
                    f"/sites/{site_id}",
                    json=update_data
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Site {site_id} updated successfully"
                        )
                    ]
                )

            elif tool_name == "delete_site":
                site_id = args["site_id"]
                await self._make_request("DELETE", f"/sites/{site_id}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Site {site_id} deleted successfully"
                        )
                    ]
                )

            elif tool_name == "list_pages":
                site_id = args["site_id"]
                pages_data = await self._make_request("GET", f"/sites/{site_id}/pages")
                
                if not pages_data:
                    return CallToolResult(
                        content=[TextContent(type="text", text="No pages found for this site")]
                    )
                
                content = "Pages:\n" + "\n".join(
                    f"- {p['title']} (ID: {p['id']}, slug: {p['slug']}, published: {p['is_published']})"
                    for p in pages_data
                )
                return CallToolResult(
                    content=[TextContent(type="text", text=content)]
                )

            elif tool_name == "create_page":
                site_id = args["site_id"]
                title = args["title"]
                slug = args["slug"]
                is_published = args.get("is_published", False)
                
                data = await self._make_request(
                    "POST",
                    f"/sites/{site_id}/pages",
                    json={"title": title, "slug": slug, "is_published": is_published}
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Page '{title}' created successfully with slug '{slug}'"
                        )
                    ]
                )

            elif tool_name == "update_page":
                site_id = args.get("site_id")
                page_id = args["page_id"]
                update_data = {}
                if "title" in args:
                    update_data["title"] = args["title"]
                if "slug" in args:
                    update_data["slug"] = args["slug"]
                if "is_published" in args:
                    update_data["is_published"] = args["is_published"]
                
                await self._make_request(
                    "PATCH",
                    f"/sites/{site_id}/pages/{page_id}" if site_id else f"/pages/{page_id}",
                    json=update_data
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Page {page_id} updated successfully"
                        )
                    ]
                )

            elif tool_name == "delete_page":
                site_id = args.get("site_id")
                page_id = args["page_id"]
                
                await self._make_request(
                    "DELETE",
                    f"/sites/{site_id}/pages/{page_id}" if site_id else f"/pages/{page_id}"
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Page {page_id} deleted successfully"
                        )
                    ]
                )

            elif tool_name == "get_page_content":
                site_id = args.get("site_id")
                page_id = args["page_id"]
                
                # Get page details first
                page_data = await self._make_request(
                    "GET",
                    f"/sites/{site_id}/pages/{page_id}" if site_id else f"/pages/{page_id}"
                )
                
                # Get content sections
                content_data = await self._make_request(
                    "GET",
                    f"/sites/{site_id}/pages/{page_id}/content" if site_id else f"/pages/{page_id}/content"
                )
                
                sections_text = "\n\n".join(
                    f"## {s['section_type']} (Order: {s.get('order', 0)})\n{s['content']}"
                    for s in content_data
                ) if content_data else "No content sections yet"
                
                content_text = f"Page: {page_data['title']}\nSlug: {page_data['slug']}\nPublished: {page_data['is_published']}\n\n{sections_text}"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=content_text)]
                )

            elif tool_name == "update_page_content":
                site_id = args.get("site_id")
                page_id = args["page_id"]
                section_type = args["section_type"]
                content = args["content"]
                order = args.get("order", 0)
                
                # First, try to find existing section
                content_data = await self._make_request(
                    "GET",
                    f"/sites/{site_id}/pages/{page_id}/content" if site_id else f"/pages/{page_id}/content"
                )
                
                existing = next((s for s in content_data if s["section_type"] == section_type), None)
                
                if existing:
                    # Update existing
                    await self._make_request(
                        "PATCH",
                        f"/sites/{site_id}/pages/{page_id}/content/{existing['id']}" if site_id else f"/pages/{page_id}/content/{existing['id']}",
                        json={"content": content, "order": order}
                    )
                else:
                    # Create new section
                    await self._make_request(
                        "POST",
                        f"/sites/{site_id}/pages/{page_id}/content" if site_id else f"/pages/{page_id}/content",
                        json={"section_type": section_type, "content": content, "order": order}
                    )
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Content updated for section '{section_type}' on page {page_id}"
                        )
                    ]
                )

            elif tool_name == "apply_theme":
                site_id = args["site_id"]
                theme_slug = args["theme_slug"]
                
                await self._make_request(
                    "PATCH",
                    f"/sites/{site_id}",
                    json={"theme_slug": theme_slug}
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Theme '{theme_slug}' applied to site {site_id}"
                        )
                    ]
                )

            elif tool_name == "list_themes":
                data = await self._make_request("GET", "/themes")
                themes = "\n".join(
                    f"- {theme['slug']}: {theme.get('description', 'No description')}"
                    for theme in data
                )
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=f"Available themes:\n{themes}")
                    ]
                )

            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {tool_name}",
                        )
                    ],
                    isError=True,
                )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ],
                isError=True,
            )

    async def handle_list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """List available resources"""
        return ListResourcesResult(resources=[])

    async def handle_list_prompts(self, request: ListPromptsRequest) -> ListPromptsResult:
        """List available prompts"""
        return ListPromptsResult(prompts=[])


def create_server(api_url: str, api_token: str) -> MCPServer:
    """Create MCP server instance"""
    return MCPServer(api_url, api_token)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI CMS MCP Server")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="AI CMS API URL",
    )
    parser.add_argument(
        "--api-token",
        default=os.getenv("AICMS_API_TOKEN"),
        help="AI CMS API token",
    )
    
    args = parser.parse_args()
    
    if not args.api_token:
        print("Error: API token required. Set AICMS_API_TOKEN or use --api-token")
        return
    
    server = create_server(args.api_url, args.api_token)
    
    # Run stdio server
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
