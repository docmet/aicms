# Development Guide

This guide covers the development setup, workflows, and best practices for AI CMS.

---

## Development Environment Setup

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

### Initial Setup

```bash
git clone git@github.com:docmet/aicms.git
cd aicms
./cli.sh init
```

`./cli.sh init` does:
1. Creates `.env` from `env.example`
2. Configures git hooks (lefthook)
3. Installs frontend dependencies (pnpm)
4. Installs backend dependencies (uv)
5. Starts Docker services
6. Runs database migrations
7. Seeds the database with test data

```bash
./cli.sh start   # Start all services
```

Access:
- Frontend: http://localhost:3000
- Admin dashboard: http://localhost:3000/dashboard
- Backend API docs: http://localhost:8000/docs
- MCP server: http://localhost:8001

### Test Credentials

| User | Email | Password | Role |
|------|-------|----------|------|
| Admin | norbi@docmet.com | password123 | Admin + regular user |
| Client | client@docmet.com | password123 | Regular user |

---

## Mobile Testing via ngrok

To test from a mobile device (including Claude mobile app via MCP):

```bash
# In a separate terminal (after ./cli.sh start)
ngrok http 80
```

Use the generated `https://xxxx.ngrok.io` URL as the MCP server URL in mobile apps.
See [docs/ai-platforms.md](ai-platforms.md) for platform-specific setup.

---

## CLI Reference

```bash
# Services
./cli.sh start              # Start all 5 services (nginx, frontend, backend, mcp_server, postgres)
./cli.sh stop               # Stop all services
./cli.sh restart            # Restart all services
./cli.sh restart-frontend   # Restart frontend only
./cli.sh restart-backend    # Restart backend only
./cli.sh logs               # View all service logs
./cli.sh logs:frontend      # Frontend logs only
./cli.sh logs:backend       # Backend logs only

# Code quality
./cli.sh lint               # Run all linters (frontend ESLint + backend ruff)
./cli.sh lint:frontend      # Frontend only
./cli.sh lint:backend       # Backend only
./cli.sh format             # Format all code (Prettier + black + isort)
./cli.sh typecheck          # Run all type checks (tsc + mypy)
./cli.sh test               # Run all tests
./cli.sh test:frontend      # Frontend tests (Vitest)
./cli.sh test:backend       # Backend tests (pytest)
./cli.sh test:integration   # Backend integration tests

# Database
./cli.sh db:migrate         # Run Alembic migrations
./cli.sh db:seed            # Seed database
./cli.sh db:reset           # Wipe + migrate + seed (caution: destroys data)

# MCP
./cli.sh mcp:install        # Install MCP server dependencies
./cli.sh mcp:run            # Run MCP server manually (requires api_url + token params)

# Utilities
./cli.sh verify             # Check all required tools are installed
./cli.sh build              # Build production Docker images
./cli.sh clean              # Remove all containers and volumes (caution)
./cli.sh help               # Full command reference
```

---

## Claude Code Skills (Slash Commands)

Project-specific slash commands are in `.claude/commands/`. Use them in Claude Code:

| Command | Description |
|---------|-------------|
| `/check-stack` | Verify all services are healthy |
| `/db-reset` | Reset and reseed the database |
| `/test-mcp` | Test all MCP tools with seed credentials |
| `/new-section-type` | Guide to add a new section type end-to-end |
| `/deploy-check` | Check CI status and staging health |
| `/seed-demo` | Reseed with rich demo content |

---

## Git Workflow

We work directly on `main`. No feature branches required for this project stage.

Commits are enforced via lefthook (runs in parallel before commit):
- `lint` — `./cli.sh lint`
- `typecheck` — `./cli.sh typecheck`
- `test` — `./cli.sh test`

The pre-commit hook also runs `format` and re-stages changed files automatically.

### Commit Convention

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

**Scopes:** `frontend`, `backend`, `mcp`, `infra`, `docs`, `deploy`, `claude`

Examples:
```
feat(frontend): add hero section component with gradient background
fix(backend): enforce site ownership check on content update
docs(mcp): update tool descriptions with JSON schema examples
feat(mcp): add describe_site and generate_section tools
chore(infra): add security headers to nginx config
```

---

## Frontend Development

**Stack:** Next.js 15+ App Router, TypeScript strict, TailwindCSS, shadcn/ui, pnpm

### Structure

```
frontend/src/
├── app/
│   ├── (public)/         # Landing page, login, register
│   ├── (dashboard)/      # Admin dashboard (auth required)
│   │   └── dashboard/
│   │       ├── sites/    # Site editor
│   │       ├── mcp/      # AI tools connection
│   │       ├── admin/    # Admin panel (admin users only)
│   │       └── ...
│   └── [site_slug]/      # Public site renderer (SSR, no auth)
├── components/
│   ├── sections/         # Public site section components (HeroSection, etc.)
│   ├── admin/            # Dashboard components
│   │   └── section-editor/  # Structured form fields per section type
│   ├── seo/              # SEO meta + JSON-LD components
│   └── ui/               # shadcn/ui primitives
├── hooks/                # Custom React hooks
│   └── use-preview-stream.ts  # SSE hook for live preview
├── lib/                  # API client, utilities
└── styles/               # globals.css, themes.css (CSS variables)
```

### Section Components

Public site sections are in `src/components/sections/`. Each renders structured JSON content:

| Component | Section Type | Key Props |
|-----------|-------------|-----------|
| `HeroSection` | `hero` | headline, subheadline, badge, cta_primary, cta_secondary |
| `FeaturesSection` | `features` | headline, subheadline, items[] |
| `TestimonialsSection` | `testimonials` | headline, items[] |
| `AboutSection` | `about` | headline, body, stats[] |
| `ContactSection` | `contact` | headline, email, phone, address, hours |
| `CTASection` | `cta` | headline, subheadline, button_label, button_href |
| `PricingSection` | `pricing` | headline, plans[] |
| `CustomSection` | any unknown | title, content |

### Adding a New Section Type

Use the `/new-section-type` Claude Code skill for guided steps, or manually:

1. Add JSON schema in `backend/src/schemas/content.py`
2. Create React component in `frontend/src/components/sections/NewSection.tsx`
3. Register in `frontend/src/app/[site_slug]/page.tsx` mapper
4. Add admin form fields in `frontend/src/components/admin/section-editor/`
5. Update MCP tool description in `mcp_server/src/aicms_mcp_server/server.py`
6. Add example to `docs/content-schema.md`

### Theme System

Themes use CSS variables defined in `frontend/src/styles/themes.css`.
Applied via `data-theme="<slug>"` attribute on the site wrapper element.

Available themes: `modern`, `startup`, `warm`, `minimal`, `dark`

Each theme defines:
- `--color-primary`, `--color-secondary`, `--color-accent`
- `--gradient-hero`, `--gradient-cta`
- `--font-heading`, `--font-body`
- `--color-surface`, `--color-background`, `--color-text`

---

## Backend Development

**Stack:** Python 3.13+, FastAPI, SQLAlchemy async, PostgreSQL 16, Alembic, uv, pytest

### Structure

```
backend/src/
├── main.py              # FastAPI app, route registration
├── config.py            # Settings (env vars)
├── database.py          # SQLAlchemy async session setup
├── models/              # SQLAlchemy ORM models
│   ├── user.py          # User (id, email, password_hash, is_admin, tier, is_suspended)
│   ├── site.py          # Site (user_id FK, slug, name, theme_slug, is_deleted)
│   ├── page.py          # Page (site_id FK, title, slug, is_published, last_published_at)
│   ├── content.py       # ContentSection (page_id FK, section_type, content_draft, content_published)
│   ├── page_version.py  # PageVersion (page_id FK, version_number, snapshot JSON)
│   ├── theme.py         # Theme (slug, name, config JSON)
│   └── mcp_client.py    # MCPClient (user_id FK, token, tool_type)
├── schemas/             # Pydantic request/response schemas
│   ├── content.py       # Content section schemas (hero, features, etc.)
│   └── ...
├── api/                 # FastAPI route handlers
│   ├── auth.py          # POST /auth/register, /auth/login, GET /auth/me
│   ├── sites.py         # CRUD /sites/*
│   ├── pages.py         # CRUD /sites/{id}/pages/*
│   ├── content.py       # CRUD /sites/{id}/pages/{id}/content/*
│   ├── preview.py       # SSE /pages/{id}/preview-stream, POST /pages/{id}/publish
│   ├── themes.py        # GET /themes/*
│   ├── mcp.py           # MCP client registration
│   └── admin.py         # Admin-only endpoints
├── services/            # Business logic
│   ├── auth.py          # JWT, password hashing
│   └── theme.py         # Theme management
└── tests/
    ├── unit/            # Unit tests
    └── integration/     # Integration tests (require running DB)
```

### Database Migrations

```bash
# Create a new migration
cd backend
uv run alembic revision --autogenerate -m "description"

# Apply migrations
./cli.sh db:migrate

# Rollback one step
cd backend && uv run alembic downgrade -1
```

### Content Section Schemas

Section content is stored as JSON strings. Schemas are in `backend/src/schemas/content.py`.

See [docs/content-schema.md](content-schema.md) for the complete reference.

When a known `section_type` is submitted, the JSON is validated against its schema.
Unknown section types are stored as-is (treated as `custom`).

### Adding a New API Endpoint

1. Define Pydantic schemas in `src/schemas/`
2. Add route handler in `src/api/`
3. Register router in `src/main.py`
4. Add integration test in `src/tests/integration/`

**Security checklist for new endpoints:**
- Requires `current_user = Depends(get_current_user)`
- Verifies resource ownership (returns 404, not 403, when not found/owned)
- Input validated via Pydantic
- No secrets in response body

---

## MCP Server Development

**Location:** `mcp_server/src/aicms_mcp_server/server.py`

The MCP server proxies all tool calls to the backend API. Each tool:
1. Validates input
2. Makes HTTP call to `{BACKEND_URL}/api/v1/...` with user's auth token
3. Formats response as human-readable text for the AI

### Adding a New MCP Tool

1. Add tool definition (name, description, inputSchema) in `server.py`
2. Add handler in the `call_tool` function
3. Update tool description to include JSON schema examples
4. Test via `./cli.sh mcp:run` or `/test-mcp` skill
5. Update `docs/mcp-integration.md`

### Testing MCP Tools

```bash
# Start services
./cli.sh start

# Quick test via CLI skill
/test-mcp

# Manual curl test
TOKEN=$(curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client@docmet.com&password=password123" | jq -r .access_token)

# Register MCP client
MCP_TOKEN=$(curl -s -X POST http://localhost/api/mcp/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "tool_type": "custom"}' | jq -r .token)

# List sites via MCP
curl -X POST http://localhost:8001/tools/call \
  -H "Authorization: Bearer $MCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "list_sites", "arguments": {}}'
```

---

## Versioning System

See [docs/versioning.md](versioning.md) for the full draft/preview/publish architecture.

Quick summary:
- AI/user edits always update `content_draft`
- `content_published` only updates on explicit Publish action
- SSE stream (`/pages/{id}/preview-stream`) pushes draft updates to the admin preview pane
- `PageVersion` snapshots saved on each publish (max 5, rollback supported)

---

## Security

See [docs/security.md](security.md) for the full security guide.

Quick summary:
- All data endpoints verify ownership (user can only see/modify their own data)
- Input validated via Pydantic + sanitized (HTML stripped)
- JWT auth, bcrypt passwords, never return password hashes
- Rate limiting on auth endpoints (via Nginx in production)

---

## Troubleshooting

### Services won't start
```bash
./cli.sh verify          # Check all tools installed
./cli.sh logs            # View error logs
./cli.sh restart         # Try restarting
```

### Database issues
```bash
./cli.sh db:reset        # Wipe and start fresh
```

### Frontend build errors
```bash
# Clear cache and reinstall
cd frontend && rm -rf .next node_modules && pnpm install
```

### Backend import errors
```bash
cd backend && uv sync --dev
```

### Git hook failures
```bash
# View what failed
./cli.sh lint
./cli.sh typecheck
./cli.sh test

# Fix issues, then commit again
# (Never skip hooks with --no-verify in normal workflow)
```

### MCP connection issues
- Verify MCP server is running: `./cli.sh logs` (check mcp_server service)
- Verify token is valid: check `/dashboard/mcp` in admin
- Test manually: `/test-mcp` skill
