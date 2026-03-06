# MyStorey

Build and manage websites by talking to your AI assistant. Connect Claude or ChatGPT once — then just describe what you want and it happens live.

**Product:** mystorey.io · **Staging:** mystorey-staging (Coolify, Hetzner)

---

## How It Works

1. **Sign up** — get a free site at `[yourname].mystorey.io`
2. **Connect your AI** — paste your MCP URL into Claude.ai or ChatGPT (one-time setup)
3. **Talk to edit** — "update my hero headline", "switch to the dark theme", "add a pricing section" — it happens live with real-time preview

---

## Features

### For Users
- 8 section types: Hero, Features, Testimonials, About, Contact, CTA, Pricing, Custom
- 7 themes: Modern, Startup, Warm, Minimal, Dark + default/nature aliases
- Multi-page sites with automatic site navigation
- Draft → preview → publish workflow
- Last 5 versions per page with AI-triggered rollback
- Real-time preview via SSE (see changes as AI types them)
- Free plan: 1 site, mystorey.io subdomain, "Made with MyStorey" badge
- Pro ($9.99/mo): 3 sites, custom domains, no badge
- Agency ($99/mo): 15 sites, custom domains, AI automations (coming)
- SEO: meta tags, OG, JSON-LD, sitemap.xml, robots.txt per site

### AI Integration (MCP) — 19 tools
| Group | Tools |
|-------|-------|
| Sites | `list_sites` `create_site` `get_site_info` `describe_site` `update_site` `delete_site` |
| Pages | `list_pages` `create_page` `update_page` `delete_page` `publish_page` |
| Content | `get_page_content` `update_section` `generate_section` `delete_section` |
| Themes | `list_themes` `apply_theme` |
| Versions | `list_versions` `revert_to_version` |

Works with: Claude.ai ✅ · ChatGPT (Apps/developer mode) ✅ · Claude Desktop ✅ · Any MCP-compatible tool ✅

### Admin (Platform Owner)
- Platform stats: users, sites, pages, sections
- User management: list, delete, toggle admin, set plan manually
- Impersonate any user for support (restore button included)

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, shadcn/ui, pnpm |
| Backend | Python 3.13+, FastAPI, SQLAlchemy async, PostgreSQL 16, Alembic, uv |
| MCP Server | FastAPI, HTTP+SSE, OAuth 2.0 |
| Infra | Docker Compose, Nginx, GitHub Actions CI/CD, Coolify on Hetzner |

5 Docker services: `nginx` · `frontend` · `backend` · `mcp_server` · `postgres`

---

## Getting Started

### Prerequisites

```bash
brew install docker node@22
npm install -g pnpm
brew install python@3.13
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Start

```bash
git clone git@github.com:docmet/aicms.git mystorey
cd mystorey
./cli.sh init     # sets up .env, git hooks, deps, DB
./cli.sh start    # starts all services
```

| Service | URL |
|---------|-----|
| App | http://localhost:3000 |
| Dashboard | http://localhost:3000/dashboard |
| API docs | http://localhost:8000/docs |
| MCP server | http://localhost:8001 |
| Mail (dev) | http://localhost:8025 (Mailpit) |

### Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | norbi@docmet.com | password123 |
| User | client@docmet.com | password123 |

### ngrok (mobile / AI tool testing)

```bash
ngrok http 80
# Use the https://xxxx.ngrok-free.app URL in Claude.ai or ChatGPT
```

---

## Development Commands

```bash
./cli.sh start            # Start all services
./cli.sh stop             # Stop
./cli.sh restart          # Restart
./cli.sh lint             # Run all linters
./cli.sh format           # Format all code
./cli.sh test             # Run all tests
./cli.sh typecheck        # Type check (frontend + backend)
./cli.sh db:migrate       # Run Alembic migrations
./cli.sh db:seed          # Seed database
./cli.sh db:reset         # Wipe + migrate + seed
./cli.sh logs             # View all service logs
./cli.sh deploy:prod      # Deploy to production
./cli.sh help             # Full command list
```

### Claude Code Skills

```
/check-stack        Check all Docker services are healthy
/db-reset           Reset and reseed the database
/test-mcp           Test MCP tools via curl
/new-section-type   Guide to add a new section type end-to-end
/deploy-check       Check CI status and staging health
/seed-demo          Reseed with rich demo content
```

---

## Project Structure

```
mystorey/
├── cli.sh                      # Dev CLI (30+ commands)
├── docker-compose.dev.yml      # Dev stack (with hot-reload)
├── docker-compose.prod.yml     # Production stack
├── nginx/                      # Reverse proxy configs
├── .env.example                # Environment template
├── frontend/                   # Next.js 15
│   └── src/
│       ├── app/
│       │   ├── (public)/       # Landing, login, register
│       │   ├── dashboard/      # Admin dashboard (auth required)
│       │   └── [site_slug]/    # Public site renderer (SSR)
│       ├── components/
│       │   ├── sections/       # Hero, Features, Testimonials, etc.
│       │   ├── admin/          # Dashboard + section editors
│       │   └── ui/             # shadcn/ui primitives
│       └── public/icons/       # Brand icons (Claude, OpenAI, Perplexity)
├── backend/                    # FastAPI
│   └── src/
│       ├── models/             # User, Site, Page, ContentSection, PageVersion, MCPClient
│       ├── schemas/            # Pydantic schemas
│       ├── api/                # auth, sites, pages, content, themes, mcp, admin, billing
│       └── tests/              # Unit + integration tests
├── mcp_server/                 # MCP server (FastAPI + SSE)
├── docs/                       # Extended documentation
└── .planning/research/         # Research documents (payment, WP plugin, etc.)
```

---

## Deployment

### Staging
- Deployed via Coolify on Hetzner (auto-deploy on `main` after CI passes)
- GitHub Actions: lint → typecheck → test → Coolify webhook

### Production
- Same stack, production Docker targets
- `backend/start.sh` runs `alembic upgrade head` then uvicorn on every deploy
- Env vars: see `.env.example`

### Key env vars
```bash
JWT_SECRET=                     # openssl rand -hex 32
STRIPE_SECRET_KEY=              # sk_live_... (or sk_test_... for staging)
STRIPE_WEBHOOK_SECRET=          # whsec_...
STRIPE_PRO_PRICE_ID=            # price_...
STRIPE_AGENCY_PRICE_ID=         # price_...
REVOLUT_MERCHANT_API_KEY=       # (currently unused, Stripe preferred)
SMTP_HOST=                      # mail-in-a-box or mailpit for dev
SMTP_USER=
SMTP_PASSWORD=
```

---

## Documentation

- [Development Guide](docs/development.md)
- [Content Schema](docs/content-schema.md)
- [MCP Integration](docs/mcp-integration.md)
- [AI Platforms Setup](docs/ai-platforms.md)
- [Versioning](docs/versioning.md)
- [Admin Guide](docs/admin.md)
- [Deployment](docs/deployment.md)
- [Security](docs/security.md)
- [Payment & Tax Research](.planning/research/payment-tax-research.md)
- [WordPress Plugin Plan](.planning/research/wordpress-mcp-plugin-opportunity.md)
