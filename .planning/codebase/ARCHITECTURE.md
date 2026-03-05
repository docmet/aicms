# Architecture

## Pattern
**Monolith with Service Separation**: Three distinct services (Frontend, Backend, MCP Server) communicate via HTTP APIs through an Nginx reverse proxy. Each service handles a specific concern while sharing a single PostgreSQL database (accessed only by the backend; MCP server uses the backend API).

## Layers

### Frontend (Next.js 15 App Router)
- **Public sites**: SSR pages at `/{site_slug}/[page_slug]` — serves published content only
- **Dashboard**: Auth-gated admin UI for site management
- **Section components**: 8 section types rendered from JSON content
- **Themes**: CSS variables via `data-theme` attribute (7 themes)

### Backend (FastAPI)
- **API routers**: REST endpoints for sites, pages, content, themes, auth, admin, MCP management
- **ORM models**: SQLAlchemy async models (User, Site, Page, ContentSection, PageVersion, MCPClient, Theme)
- **Pydantic schemas**: Request validation + typed response models
- **Services**: Auth helpers, preview SSE service

### MCP Server (FastAPI)
- **Tool handlers**: 17 MCP tool implementations
- **Backend client**: Makes authenticated HTTP requests to backend API
- **OAuth endpoints**: Authorization Code flow with DCR support

### Infrastructure
- **Nginx**: Reverse proxy routing, security headers, gzip, rate limiting
- **PostgreSQL 16**: Multi-tenant data; cascading soft deletes
- **Docker Compose**: Orchestrates 5 services

## Data Flow

### User Authentication
1. `POST /api/auth/login` (form data) → JWT token
2. Token stored client-side (localStorage), sent as `Authorization: Bearer` header
3. Backend validates JWT on every protected request

### Site & Page Management
1. User creates site → Frontend calls `POST /api/sites`
2. Backend enforces `PLAN_SITE_LIMITS` before creating Site record
3. New site gets default homepage Page automatically

### Content Editing (Draft → Publish)
1. **Draft**: MCP or admin writes to `content_draft` via `PUT /api/sites/{id}/pages/{id}/content/by-type/{type}`
2. **Preview**: Dashboard polls draft; public site ignores drafts
3. **Publish**: `POST /api/sites/{id}/pages/{id}/publish` copies `content_draft` → `content_published` for all sections
4. **Rollback**: Last 5 versions in `PageVersion` table

### Public Site Rendering
1. Visitor hits `/{site_slug}` → Frontend requests `GET /api/public/sites/{site_slug}`
2. Backend returns site metadata + nav pages + published sections only
3. Frontend renders with theme CSS variables + section component registry
4. Free tier: `show_badge: true` injects "Made with MyStorey" badge

### MCP Request Lifecycle
1. AI tool sends `POST /mcp` with `Authorization: Bearer {token}`
2. MCP server validates token against `MCPClient` table
3. Tool handler makes authenticated backend API call
4. Backend updates `content_draft` (never `content_published` directly)
5. Dashboard SSE connection (`/api/preview/…`) streams live draft updates
6. User manually publishes when satisfied

## Key Abstractions

### Core Models
| Model | Purpose |
|-------|---------|
| `User` | Authentication, plan/tier enforcement, multi-tenancy root |
| `Site` | User's website (slug, name, theme, soft-delete) |
| `Page` | A page within a site (slug, order, published flag) |
| `ContentSection` | Section content (type + draft JSON + published JSON) |
| `PageVersion` | Historical snapshots for rollback (last 5 kept) |
| `MCPClient` | AI tool registration (platform, bearer token) |
| `Theme` | Available themes |

### Content Schema
- 8 section types: `hero`, `features`, `testimonials`, `about`, `contact`, `cta`, `pricing`, `custom`
- Each stored as JSON in `content_draft` / `content_published`
- Pydantic schemas in `backend/src/schemas/content.py`

### Themes
- 7 themes: modern, warm, startup, minimal, dark, nature, default
- Applied via CSS custom properties on `<div data-theme="name">`
- `--font-inter` (body) and `--font-sora` (headings) via next/font
- Scroll animations: `.animate-on-scroll` + IntersectionObserver

### Pricing Tiers
- `UserPlan` enum: `free`, `pro`, `agency`
- Limits enforced in `backend/src/api/sites.py` at create time
- Error format: `plan_limit_reached:{plan}:{limit}` (HTTP 403)

## Entry Points

### Frontend
- `frontend/src/app/layout.tsx` — root layout, fonts, auth provider
- `frontend/src/app/[site_slug]/page.tsx` — public site renderer
- `frontend/src/app/dashboard/page.tsx` — admin dashboard
- `frontend/src/app/dashboard/sites/[site_id]/page.tsx` — site editor
- `frontend/src/app/dashboard/sites/new/page.tsx` — 3-step onboarding wizard

### Backend
- `backend/src/main.py` — FastAPI app setup, router registration
- `backend/src/api/auth.py` — login, JWT generation
- `backend/src/api/sites.py` — site CRUD with plan enforcement
- `backend/src/api/content.py` — section upsert, publish
- `backend/src/api/public.py` — public API (no auth, drafts hidden)
- `backend/src/api/admin.py` — admin endpoints (users, stats, impersonate)

### MCP Server
- `mcp_server/src/aicms_mcp_server/server.py` — all 17 tool implementations
- `mcp_server/src/main.py` — FastAPI app serving MCP protocol
