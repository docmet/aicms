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
                description="List all sites you have access to",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_site",
                description="Get site details including current theme",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "Site ID or slug"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="update_theme",
                description="Change the theme for a site",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "Site ID or slug"},
                        "theme_slug": {
                            "type": "string",
                            "description": "Theme slug (default, warm, nature, dark, minimal)",
                            "enum": ["default", "warm", "nature", "dark", "minimal"],
                        },
                    },
                    "required": ["site_id", "theme_slug"],
                },
            ),
            Tool(
                name="get_content",
                description="Get content for a specific page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "Site ID or slug"},
                        "page_slug": {"type": "string", "description": "Page slug (default: 'home')"},
                    },
                    "required": ["site_id"],
                },
            ),
            Tool(
                name="update_content",
                description="Update content for a specific section",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string", "description": "Site ID or slug"},
                        "page_id": {"type": "string", "description": "Page ID"},
                        "section_id": {"type": "string", "description": "Section ID"},
                        "content": {"type": "string", "description": "New content"},
                    },
                    "required": ["site_id", "page_id", "section_id", "content"],
                },
            ),
            Tool(
                name="list_themes",
                description="List all available themes",
                inputSchema={
                    "type": "object",
                    "properties": {},
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

            elif tool_name == "get_site":
                site_id = args["site_id"]
                data = await self._make_request("GET", f"/sites/{site_id}")
                site = Site(**data)
                content = f"""Site: {site.name}
Slug: {site.slug}
Theme: {site.theme_slug}
ID: {site.id}"""
                return CallToolResult(
                    content=[TextContent(type="text", text=content)]
                )

            elif tool_name == "update_theme":
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
                            text=f"Theme updated to {theme_slug} for site {site_id}"
                        )
                    ]
                )

            elif tool_name == "get_content":
                site_id = args["site_id"]
                page_slug = args.get("page_slug", "home")
                
                # Get pages
                pages_data = await self._make_request("GET", f"/sites/{site_id}/pages")
                if not pages_data:
                    return CallToolResult(
                        content=[TextContent(type="text", text="No pages found")]
                    )
                
                # Find page
                page = next((p for p in pages_data if p["slug"] == page_slug), pages_data[0])
                
                # Get content
                content_data = await self._make_request(
                    "GET",
                    f"/sites/{site_id}/pages/{page['id']}/content"
                )
                
                sections = [ContentSection(**section) for section in content_data]
                content_text = f"Page: {page['title']}\n\n"
                for section in sections:
                    content_text += f"## {section.section_type}\n{section.content}\n\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=content_text)]
                )

            elif tool_name == "update_content":
                site_id = args["site_id"]
                page_id = args["page_id"]
                section_id = args["section_id"]
                content = args["content"]
                
                await self._make_request(
                    "PATCH",
                    f"/sites/{site_id}/pages/{page_id}/content/{section_id}",
                    json={"content": content}
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Content updated for section {section_id}"
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
