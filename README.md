# AI CMS

A multi-tenant website platform where non-technical users build and edit their sites
by talking to their own AI tools — Claude, ChatGPT, Perplexity, or any MCP-compatible assistant.

**Core idea:** You already pay for Claude or ChatGPT. Connect it once to your site, then just
talk to it to update your content. No technical knowledge needed. No extra AI costs on our end.

---

## How It Works

1. **Sign up** — create your account, get a free site at `[yourname].aicms.docmet.systems`
2. **Connect your AI** — paste the MCP config into Claude Desktop, ChatGPT, or any AI tool
3. **Talk to edit** — ask your AI "update my hero headline to say X" and it happens live

The AI talks to our MCP server, which updates your site. You preview changes in real-time
before publishing. Your site is public, SEO-optimized, and looks great out of the box.

---

## Features

### For Users
- Beautiful, responsive site templates (Framer-level quality)
- 5 themes: Modern, Startup, Warm, Minimal, Dark
- Multiple pages per site
- Draft → preview → publish workflow with rollback (last 5 versions)
- Real-time preview: see changes as your AI edits them (SSE push, no polling)
- Instant save in web admin dashboard
- SEO-optimized: meta tags, OG tags, JSON-LD structured data, semantic HTML

### AI Integration (MCP)
Connect any MCP-compatible AI tool. Full list of tools available:

**Site Management:** `list_sites`, `create_site`, `get_site_info`, `update_site`, `delete_site`, `restore_site`

**Page Management:** `list_pages`, `create_page`, `get_page_content`, `update_page`, `delete_page`, `restore_page`

**Content:** `update_page_content`, `delete_section`, `restore_section`, `reorder_sections`, `set_section_order`

**Themes:** `list_themes`, `apply_theme`

**AI-Friendly Tools:** `describe_site` (full narrative in 1 call), `generate_section` (scaffold JSON for AI to fill), `smart_find` (find by name, not UUID), `publish_page`, `get_versions`, `revert_to_version`

### Admin (Platform Owner)
- User management: list, suspend, tier management
- Impersonation: see exactly what any user sees for support
- Platform stats dashboard
- Audit log for all admin actions

---

## Content Section Types

Each page is built from sections. Sections store structured JSON content:

| Type | Fields |
|------|--------|
| `hero` | headline, subheadline, badge, cta_primary, cta_secondary |
| `features` | headline, subheadline, items (icon, title, description) |
| `testimonials` | headline, items (quote, name, role, company) |
| `about` | headline, body, stats (number, label) |
| `contact` | headline, email, phone, address, hours |
| `cta` | headline, subheadline, button_label, button_href |
| `pricing` | headline, plans (name, price, features, cta) |
| `custom` | title, content — fallback for any type AI invents |

See [docs/content-schema.md](docs/content-schema.md) for complete JSON schemas.

---

## Tech Stack

### Frontend
- **Next.js 15+** with App Router (SSR for public sites)
- **TypeScript** strict mode
- **TailwindCSS** + CSS variables for theming
- **shadcn/ui** components
- **pnpm** package manager

### Backend
- **Python 3.13+** with FastAPI
- **SQLAlchemy** async ORM
- **PostgreSQL 16**
- **Alembic** migrations
- **uv** package manager

### MCP Server
- FastAPI-based MCP server
- HTTP + SSE transport
- Token-based auth (one token per connected AI tool)

### Infrastructure
- Docker Compose (dev + production)
- Nginx reverse proxy
- GitHub Actions CI/CD
- Coolify on Hetzner for deployment
- `./cli.sh` — unified development CLI

---

## Getting Started

### Prerequisites

```bash
# Docker
brew install docker

# Node.js 22+
brew install node@22
npm install -g pnpm

# Python 3.13+
brew install python@3.13
curl -LsSf https://astral.sh/uv/install.sh | sh

# GitHub CLI (optional)
brew install gh
```

### Quick Start

```bash
git clone git@github.com:docmet/aicms.git
cd aicms
./cli.sh init    # sets up .env, git hooks, deps, DB
./cli.sh start   # starts all 5 services
```

Access:
- **Frontend:** http://localhost:3000
- **Admin:** http://localhost:3000/dashboard
- **Backend API:** http://localhost:8000/docs
- **MCP Server:** http://localhost:8001

### Test Credentials

| User | Email | Password | Role |
|------|-------|----------|------|
| Admin | norbi@docmet.com | password123 | Admin + client |
| Client | client@docmet.com | password123 | Regular user |

### Mobile Testing via ngrok

To test from a mobile device (including Claude mobile app):

```bash
# In a separate terminal, after ./cli.sh start
ngrok http 80
# Use the https://xxxx.ngrok.io URL in Claude mobile app MCP config
```

### Connect Claude Desktop

1. Go to http://localhost:3000/dashboard/mcp
2. Register a new AI tool (Claude Desktop)
3. Copy the generated config
4. Paste into `~/Library/Application Support/Claude/claude_desktop_config.json`
5. Restart Claude Desktop

See [docs/ai-platforms.md](docs/ai-platforms.md) for all platform setup guides.

---

## Development Commands

```bash
./cli.sh start            # Start all services
./cli.sh stop             # Stop all services
./cli.sh restart          # Restart all services
./cli.sh lint             # Run all linters
./cli.sh format           # Format all code
./cli.sh test             # Run all tests
./cli.sh typecheck        # Type check
./cli.sh db:migrate       # Run migrations
./cli.sh db:seed          # Seed database
./cli.sh db:reset         # Wipe + migrate + seed
./cli.sh logs             # View all service logs
./cli.sh mcp:run          # Run MCP server manually
./cli.sh verify           # Check all tools installed
./cli.sh help             # Full command reference
```

### Claude Code Skills (slash commands)

```
/check-stack      Check Docker services health
/db-reset         Reset and reseed the database
/test-mcp         Test all MCP tools via curl
/new-section-type Guide to add a new section type end-to-end
/deploy-check     Check CI status and staging health
/seed-demo        Reseed with rich structured demo content
```

---

## Project Structure

```
mcp_cms/
├── cli.sh                    # Development CLI (30+ commands)
├── docker-compose.yml        # Production Docker Compose
├── docker-compose.dev.yml    # Dev (5 services: nginx, frontend, backend, mcp_server, postgres)
├── env.example              # Environment template
├── lefthook.yml             # Git hooks config (lint+typecheck+test on commit)
├── frontend/                # Next.js 15+ application
│   └── src/
│       ├── app/
│       │   ├── (public)/    # Landing page, login, register
│       │   ├── (dashboard)/ # Admin dashboard (auth required)
│       │   └── [site_slug]/ # Public site renderer (SSR, no auth)
│       ├── components/
│       │   ├── sections/    # Public site section components (Hero, Features, etc.)
│       │   ├── admin/       # Dashboard components
│       │   └── ui/          # shadcn/ui primitives
│       └── styles/          # Themes (CSS variables)
├── backend/                 # Python FastAPI
│   └── src/
│       ├── models/          # User, Site, Page, ContentSection, PageVersion, MCPClient
│       ├── schemas/         # Pydantic schemas + content section schemas
│       ├── api/             # Routes: auth, sites, pages, content, themes, mcp, admin
│       └── tests/           # Unit + integration tests
├── mcp_server/              # MCP server (FastAPI + SSE)
│   └── src/
│       └── aicms_mcp_server/server.py  # All MCP tool implementations
├── nginx/                   # Reverse proxy config + security headers
├── docs/                    # Documentation
│   ├── development.md       # Dev setup and workflows
│   ├── deployment.md        # Staging + production deployment
│   ├── mcp-integration.md   # MCP tools reference
│   ├── content-schema.md    # Content JSON schemas reference
│   ├── versioning.md        # Draft/preview/publish/rollback system
│   ├── admin.md             # Admin features and impersonation
│   ├── security.md          # Security principles and implementation
│   └── ai-platforms.md      # Platform-specific setup guides
└── .github/
    └── workflows/
        └── deploy.yml       # CI (lint+typecheck+test) + deploy to staging
```

---

## Deployment

### Staging
- Domain: `aicms.docmet.systems`
- User sites: `[site-slug].aicms.docmet.systems`
- Platform: Coolify on Hetzner
- Auto-deploys on push to `main` after CI passes

### Production (future)
- Custom domains per user site
- CDN integration
- See [docs/deployment.md](docs/deployment.md)

---

## Pricing (Freemium)

| Plan | Sites | Domain | Pages | Versions |
|------|-------|--------|-------|---------|
| Free | 1 | subdomain only | 5/site | 1 (previous) |
| Pro | Unlimited | Custom domain | Unlimited | Last 5 |

---

## Documentation

- [Development Guide](docs/development.md) — setup, workflows, conventions
- [Content Schema](docs/content-schema.md) — all section type JSON schemas
- [Versioning](docs/versioning.md) — draft/preview/publish/rollback
- [MCP Integration](docs/mcp-integration.md) — all MCP tools reference
- [AI Platforms](docs/ai-platforms.md) — Claude, ChatGPT, Perplexity setup
- [Admin Guide](docs/admin.md) — admin features, impersonation
- [Security](docs/security.md) — security model and practices
- [Deployment](docs/deployment.md) — staging and production

---

## License

MIT — see [LICENSE](LICENSE)
