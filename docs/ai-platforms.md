# AI Platform Setup Guides

Connect any MCP-compatible AI assistant to your AI CMS site.
Get your MCP token from the **AI Tools** section of the dashboard (`/dashboard/mcp`).

---

## Prerequisites

- Stack running: `./cli.sh start`
- MCP token from `/dashboard/mcp`
- MCP Server URL: `http://localhost:8001` (dev) or `https://aicms.docmet.systems/mcp` (prod)

---

## Claude Desktop

**Best experience — native MCP support.**

### Setup

1. Open (or create): `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aicms": {
      "url": "http://localhost:8001/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

2. Restart Claude Desktop
3. Look for the tools icon — AI CMS tools should appear
4. Test: "List my sites"

### Production / Staging

```json
{
  "mcpServers": {
    "aicms": {
      "url": "https://aicms.docmet.systems/mcp/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

---

## Claude Mobile App (iOS / Android)

Connect via MCP when your server is publicly accessible (ngrok for dev, staging/prod URL otherwise).

### Local development with ngrok

```bash
# In a separate terminal after ./cli.sh start
ngrok http 80
# Note the https://xxxx.ngrok.io URL
```

### Add in Claude Mobile app settings

- **Name:** AI CMS
- **URL:** `https://xxxx.ngrok.io/mcp/sse` (ngrok) or `https://aicms.docmet.systems/mcp/sse` (prod)
- **Authorization:** `Bearer YOUR_MCP_TOKEN`

---

## ChatGPT (Custom GPT Actions)

ChatGPT supports tools via Custom GPTs and the Actions API.
Requires a publicly accessible HTTPS endpoint (staging or production).

### Setup

1. Go to https://chat.openai.com/gpts/create
2. In **Actions**, add a new action
3. Set server URL: `https://aicms.docmet.systems/mcp`
4. Authentication: Bearer token → your MCP token
5. Import the OpenAPI schema from `/mcp/openapi.json`

---

## Cursor IDE

Cursor has built-in MCP support.

### Setup (`.cursor/mcp.json` or global settings)

```json
{
  "mcpServers": {
    "aicms": {
      "url": "http://localhost:8001/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

---

## Perplexity

Perplexity Pro supports MCP tools.

### Setup

In Perplexity → Settings → Tools → Add MCP:
- **URL:** `https://aicms.docmet.systems/mcp/sse`
- **Token:** `Bearer YOUR_MCP_TOKEN`

---

## rube.app

### Setup

In rube.app → Settings → Connections → Add MCP:
- **Server URL:** `https://aicms.docmet.systems/mcp/sse`
- **Auth:** `Bearer YOUR_MCP_TOKEN`

---

## Any MCP-Compatible Tool

**Connection details:**
- **SSE endpoint:** `{BASE_URL}/sse`
- **Auth header:** `Authorization: Bearer YOUR_MCP_TOKEN`
- **Protocol:** MCP 1.0 (HTTP + Server-Sent Events)

---

## Multiple AI Tools

Register multiple tokens (one per AI app) in `/dashboard/mcp`.
All tokens are scoped to your user — each AI can only edit YOUR sites.
You can revoke individual tokens without affecting others.

---

## Troubleshooting

### "No tools available" or tools don't appear

```bash
# Verify MCP server is running
./cli.sh logs  # check mcp_server service

# Test manually
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/sse
```

### "Authentication failed"

- Token may be expired or deleted
- Regenerate at `/dashboard/mcp`
- Must use `Bearer ` (with space) before the token

### ngrok issues

- Free ngrok tunnels expire periodically, restart if needed
- Always use the HTTPS URL (not HTTP)

### "Site not found" from tools

- Use `list_sites` to see available sites for your account
- Use `describe_site` to get full context
- Verify you're using the token for the right account
