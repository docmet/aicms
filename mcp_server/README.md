# AI CMS MCP Server

A hosted MCP (Model Context Protocol) server for managing AI CMS content and themes through AI tools like ChatGPT, Claude, and Cursor.

## 🚀 Quick Start

The MCP server runs automatically in Docker - no installation needed!

### 1. Start the stack

```bash
./cli.sh start
```

The MCP server will be available at http://localhost:8001

### 2. Register an AI Tool

1. Go to http://localhost:3000/dashboard/mcp
2. Click "Add Client"
3. Select your AI tool (Claude, ChatGPT, or Cursor)
4. Copy the generated configuration

### 3. Configure Your AI Tool

Follow the tool-specific instructions provided in the dashboard.

## 🔧 Architecture

- **Hosted Server**: Runs in Docker alongside the main application
- **Client Authentication**: Each AI tool gets a unique token
- **Multi-tenant**: Isolates data per user
- **No Local Setup**: Everything runs in the cloud/Docker

## 🛠️ Available Tools

- `list_sites` - List all sites you have access to
- `get_site` - Get site details including theme
- `update_theme` - Change site theme
- `get_content` - Get page content
- `update_content` - Update page content
- `list_themes` - List available themes

## 📝 Usage Examples

### Claude Desktop

```
User: Change my demo-site theme to warm
Claude: I'll change the theme for you.
[Uses update_theme tool]
Done! The theme has been changed to warm.
```

### ChatGPT

```
User: Show me all my sites
ChatGPT: [Uses list_sites tool]
You have 1 site:
- demo-site (Theme: default)
```

## � Security

- Each user gets isolated access to their own sites
- Tokens expire after 1 year
- Can revoke access anytime from the dashboard

## 📚 More Info

- AI CMS Documentation: https://github.com/docmet/aicms
- Help Page: http://localhost:3000/dashboard/help
- MCP Specification: https://modelcontextprotocol.io
