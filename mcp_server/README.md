# AI CMS MCP Server

An MCP (Model Context Protocol) server for managing AI CMS content and themes through AI tools like ChatGPT, Claude, and Cursor.

## 🚀 Quick Start

### 1. Install the MCP server

```bash
cd mcp_server
pip install -e .
```

### 2. Configure for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aicms": {
      "command": "aicms-mcp",
      "args": ["--api-url", "http://localhost:8000/api/v1"],
      "env": {
        "AICMS_API_TOKEN": "your-jwt-token-here"
      }
    }
  }
}
```

### 3. Configure for ChatGPT

Add to ChatGPT custom instructions:

```
You have access to the AI CMS MCP server for managing website content. The server is running locally at http://localhost:8001.
```

## 🔧 Configuration

The MCP server needs to connect to your AI CMS backend:

- `--api-url`: Backend API URL (default: http://localhost:8000/api/v1)
- `--api-token`: JWT token for authentication (or set AICMS_API_TOKEN env var)

## 🛠️ Available Tools

- `list_sites`: List all sites you have access to
- `get_site`: Get site details including theme
- `update_theme`: Change site theme
- `get_content`: Get page content
- `update_content`: Update page content
- `list_themes`: List available themes

## 📝 Usage Examples

### Claude Desktop

```
User: Change my demo-site theme to warm
Assistant: I'll change the theme for you.
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

## 🐛 Troubleshooting

1. **Connection refused**: Make sure your AI CMS backend is running
2. **Authentication error**: Check your JWT token is valid
3. **Permission denied**: Ensure you have access to the site

## 📚 More Info

- AI CMS Documentation: https://github.com/docmet/aicms
- MCP Specification: https://modelcontextprotocol.io
