# MCP Integration Guide

AI CMS supports the Model Context Protocol (MCP) for integration with AI assistants like Claude, ChatGPT, and Cursor.

## Overview

The MCP server provides a standardized way for AI tools to interact with your CMS. It uses HTTP+SSE transport and implements OAuth 2.0 authentication.

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Claude    │──────▶│   MCP Proxy │──────▶│   MCP Server│
│   Desktop   │  OAuth│   (Nginx)   │  HTTP │   (FastAPI) │
└─────────────┘      └─────────────┘      └──────┬──────┘
                                                   │
                                                   │ HTTP
                                                   ▼
                                            ┌─────────────┐
                                            │   Backend   │
                                            │   (FastAPI) │
                                            └──────┬──────┘
                                                   │
                                                   │ SQL
                                                   ▼
                                            ┌─────────────┐
                                            │  PostgreSQL │
                                            └─────────────┘
```

## Available MCP Tools

### Site Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_sites` | List all sites with UUIDs | None |
| `create_site` | Create a new site | `name`, `slug`, `theme_slug` (optional) |
| `get_site_info` | Get site details and pages | `site_id` (UUID or slug) |
| `update_site` | Update site properties | `site_id`, `name` (optional), `slug` (optional), `theme_slug` (optional) |
| `delete_site` | Delete a site | `site_id` (UUID or slug) |

### Page Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_pages` | List pages for a site | `site_id` (UUID) |
| `create_page` | Create a new page | `site_id`, `title`, `slug`, `is_published` (optional) |
| `get_page_content` | Get content sections | `page_id` (UUID or slug) |
| `update_page` | Update page metadata | `page_id`, `title` (optional), `slug` (optional), `is_published` (optional) |
| `delete_page` | Delete a page | `page_id` (UUID or slug) |

### Content & Themes

| Tool | Description | Parameters |
|------|-------------|------------|
| `update_page_content` | Add/update content section | `page_id`, `section_type`, `content` |
| `list_themes` | List available themes | None |
| `apply_theme` | Change site theme | `site_id`, `theme_slug` |

## Section Types

When using `update_page_content`, you can use these section types:

- `hero` - Header/hero section with title and subtitle
- `body` - Main content body text
- `features` - Features list with bullet points
- `cta` - Call-to-action section
- `footer` - Footer content

## Authentication

### OAuth 2.0 Flow

1. User initiates connection from Claude Desktop
2. MCP server redirects to authorization endpoint
3. User authenticates with AI CMS credentials
4. MCP server issues access token
5. Claude Desktop uses token for API calls

### Configuration

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "aicms": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-proxy"],
      "env": {
        "SERVER_URL": "https://your-domain.com/sse/YOUR-CLIENT-ID",
        "CLIENT_ID": "aicms-client",
        "AUTHORIZATION_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Usage Examples

### Creating a Site

```
You: Create a new site called "My Blog" with slug "my-blog" and theme "nature"

Claude: I'll create that site for you.

Create site
Name: My Blog
Slug: my-blog
Theme: nature

Result: Site 'My Blog' created successfully with slug 'my-blog' (ID: a5fb23e6-bfba-4d53-8945-428c50e7be7e)
```

### Adding Content

```
You: Add a hero section to the home page saying "Welcome to My Blog"

Claude: I'll update the home page content.

Update page content
Page: home
Section: hero
Content: Welcome to My Blog

Result: Created hero section with content
```

### Listing Sites

```
You: Show me all my sites

Claude: Here are your sites:

- My Blog (slug: my-blog, theme: nature, ID: a5fb23e6-bfba-4d53-8945-428c50e7be7e)
- Demo Site (slug: demo-site, theme: warm, ID: 3644ac4e-7baa-454b-8350-6dfb558e24ec)
```

## Development

### Testing MCP Locally

1. Start the development stack:
   ```bash
   ./cli.sh start
   ```

2. Register an MCP client:
   ```bash
   curl -X POST http://localhost/api/mcp/register \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Claude Test", "tool_type": "claude"}'
   ```

3. Test tools via curl:
   ```bash
   curl -X POST http://localhost/sse/YOUR-CLIENT-ID \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR-TOKEN" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

### MCP Server Logs

```bash
./cli.sh logs:mcp-server
```

## Troubleshooting

### Connection Issues

- Verify ngrok is running and the URL is correct
- Check nginx configuration forwards headers properly
- Ensure MCP server container is healthy

### Authentication Errors

- Verify the MCP client token is valid
- Check token hasn't expired
- Ensure user exists in database

### Tool Execution Failures

- Check backend logs for API errors
- Verify site/page UUIDs are correct
- Ensure user has permission to modify resources

## Security

- All MCP connections use HTTPS in production
- OAuth 2.0 tokens expire after 24 hours
- MCP clients are tied to specific users
- All API calls validate user permissions
