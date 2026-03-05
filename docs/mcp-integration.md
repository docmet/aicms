# MCP Integration Guide

The AI CMS exposes a Model Context Protocol (MCP) server that allows any MCP-compatible
AI tool to manage your website content. Connect Claude, ChatGPT, Perplexity, or any
MCP-capable assistant and talk to it to edit your site.

---

## Architecture

```
AI Tool (Claude / ChatGPT / etc.)
         ↓  MCP protocol (HTTP + SSE)
    Nginx Reverse Proxy (:80)
         ↓
    MCP Server (FastAPI, :8001)
         ↓  HTTP + Bearer token
    Backend API (FastAPI, :8000)
         ↓  SQLAlchemy async
    PostgreSQL (:5432)
```

The MCP server is a thin adapter — it translates MCP tool calls into backend API requests
and returns human-readable responses the AI can understand and act on.

---

## Authentication

Each AI tool connection gets a unique token:

1. Log in to the admin dashboard
2. Go to **AI Tools** (`/dashboard/mcp`)
3. Click **Register new AI tool**
4. Choose your AI platform
5. Copy the generated token and server URL

Tokens are scoped to your user account. Register multiple tokens (one per AI app).
Deleting a client immediately revokes its token.

---

## Quick Setup: Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Restart Claude Desktop. See [docs/ai-platforms.md](ai-platforms.md) for all platforms.

---

## All MCP Tools

### Site Management

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `list_sites` | List all your sites | — |
| `create_site` | Create a new site | `name`, `slug`, `theme_slug` |
| `get_site_info` | Get site details + pages | `site_id` |
| `update_site` | Update name/slug/theme | `site_id`, `name?`, `slug?`, `theme_slug?` |
| `delete_site` | Soft delete a site | `site_id` |
| `restore_site` | Restore a deleted site | `site_id` |

### Page Management

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `list_pages` | List pages for a site | `site_id` |
| `create_page` | Create a new page | `site_id`, `title`, `slug`, `is_published?` |
| `get_page_content` | Get content sections | `site_id`, `page_id` |
| `update_page` | Update page metadata | `page_id`, `title?`, `slug?`, `is_published?` |
| `delete_page` | Soft delete a page | `page_id` |
| `restore_page` | Restore a deleted page | `page_id` |

### Content Editing

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `update_page_content` | Create/update a section | `site_id`, `page_id`, `section_type`, `content` (JSON) |
| `delete_section` | Soft delete a section | `site_id`, `page_id`, `section_type` |
| `restore_section` | Restore a deleted section | `site_id`, `page_id`, `section_type` |
| `reorder_sections` | Swap two sections | `site_id`, `page_id`, `section_id_1`, `section_id_2` |
| `set_section_order` | Set absolute section order | `site_id`, `page_id`, `section_order` (array of types) |

### Publishing & Versions

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `publish_page` | Publish draft → live | `site_id`, `page_id` |
| `get_versions` | List saved versions | `site_id`, `page_id` |
| `revert_to_version` | Revert draft to version | `site_id`, `page_id`, `version_id` |

### Themes

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `list_themes` | List available themes | — |
| `apply_theme` | Change site theme | `site_id`, `theme_slug` |

### AI Helper Tools

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `describe_site` | Full narrative of site content | `site_id` |
| `generate_section` | Pre-filled template for a section | `site_id`, `page_id`, `section_type`, `description` |
| `smart_find` | Find site/page by name, not UUID | `query`, `type?` |

---

## Content Format

`update_page_content` expects structured JSON matching the section type schema.

**All edits go to `content_draft`.** Call `publish_page` to push to live.

### `hero`
```json
{
  "headline": "Welcome to Bloom Florist",
  "subheadline": "Fresh flowers for every occasion, delivered same-day.",
  "badge": "Now open on Sundays",
  "cta_primary": {"label": "Order now", "href": "#contact"},
  "cta_secondary": {"label": "See our work", "href": "#gallery"}
}
```

### `features`
```json
{
  "headline": "Why choose us",
  "items": [
    {"icon": "🌸", "title": "Daily fresh", "description": "Sourced from local growers every morning."},
    {"icon": "🚚", "title": "Same-day delivery", "description": "Order by 2pm for same-day delivery."},
    {"icon": "💝", "title": "Custom arrangements", "description": "Tell us your vision."}
  ]
}
```

### `testimonials`
```json
{
  "headline": "What our customers say",
  "items": [
    {"quote": "Best flower shop in the city!", "name": "Sarah M.", "role": "Regular customer"}
  ]
}
```

### `about`
```json
{
  "headline": "Our story",
  "body": "We've been bringing beauty into homes since 2010...",
  "stats": [
    {"number": "10+", "label": "Years open"},
    {"number": "500+", "label": "Happy customers"}
  ]
}
```

### `contact`
```json
{
  "headline": "Visit us",
  "email": "hello@bloom.hu",
  "phone": "+36 1 234 5678",
  "address": "Váci utca 15, Budapest",
  "hours": "Mon-Sat: 8am-7pm"
}
```

### `cta`
```json
{
  "headline": "Ready to order?",
  "subheadline": "Free delivery on orders over 5000 HUF.",
  "button_label": "Order now",
  "button_href": "#contact"
}
```

### `custom` (fallback for any unknown type)
```json
{
  "title": "Awards",
  "content": "Winner of Budapest Best Florist 2024..."
}
```

See [docs/content-schema.md](content-schema.md) for the complete schema reference.

---

## Typical AI Workflow

### Build a new site from scratch

```
1. smart_find("bloom florist") → check if exists
2. create_site("Bloom Florist", "bloom-florist", "warm")
3. create_page(site_id, "Home", "home")
4. generate_section(site_id, page_id, "hero", "flower shop in Budapest")
5. update_page_content(site_id, page_id, "hero", {...tailored content...})
6. update_page_content(site_id, page_id, "features", {...})
7. update_page_content(site_id, page_id, "contact", {...})
8. publish_page(site_id, page_id)
```

### Update existing content

```
1. describe_site(site_id)      ← understand what currently exists
2. update_page_content(...)    ← update drafts
3. publish_page(site_id, page_id)
```

### Rollback after a mistake

```
1. get_versions(site_id, page_id)
2. revert_to_version(site_id, page_id, version_id)
3. describe_site(site_id)      ← confirm it looks right
4. publish_page(site_id, page_id)
```

---

## Real-Time Preview

When the admin editor is open in the browser, it connects to an SSE stream.
Any `update_page_content` call instantly pushes the draft change to the preview pane.
The user can watch changes happen in real-time as the AI edits.

The preview always shows `content_draft`. The public site always shows `content_published`.

---

## Soft Delete

All delete operations use soft delete — items are marked deleted but recoverable.

```
delete_site / restore_site
delete_page / restore_page
delete_section / restore_section
```

---

## Error Reference

| Error message | Meaning / Fix |
|--------------|---------------|
| `Site not found` | Wrong site_id or not owned by your account |
| `Page not found` | Wrong page_id, or wrong site_id provided |
| `Invalid JSON for section type 'hero'` | Schema validation failed, check required fields |
| `Section 'hero' already exists` | Use `update_page_content` — it creates or updates |
| `Authentication failed` | Token expired or revoked, get a new one |

---

## Development & Testing

```bash
# Start all services
./cli.sh start

# Quick test via Claude Code skill
/test-mcp

# Manual curl test
TOKEN=$(curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client@docmet.com&password=password123" | jq -r .access_token)

MCP_TOKEN=$(curl -s -X POST http://localhost/api/mcp/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","tool_type":"custom"}' | jq -r .token)

# List sites
curl -X POST http://localhost:8001/tools/call \
  -H "Authorization: Bearer $MCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"list_sites","arguments":{}}'
```
