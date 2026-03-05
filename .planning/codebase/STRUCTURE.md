# Directory Structure

## Root Layout
```
mcp_cms/
├── cli.sh                       # Dev CLI — single source of truth for all commands
├── docker-compose.dev.yml       # Dev Docker Compose (5 services, hot-reload)
├── docker-compose.prod.yml      # Production Docker Compose
├── .env / .env.example          # Environment variables
├── lefthook.yml                 # Git hooks: lint → typecheck → test
├── README.md
├── ROADMAP.md                   # Phase-based feature roadmap
├── PLAN.md                      # High-level product plan
├── frontend/                    # Next.js 15 app
├── backend/                     # FastAPI backend
├── mcp_server/                  # MCP tool server
├── nginx/                       # nginx.conf + nginx.prod.conf
├── docs/                        # Project docs (content-schema.md, etc.)
├── .github/                     # GitHub Actions CI/CD
└── .planning/                   # Planning & analysis docs (this dir)
```

## Frontend Structure
```
frontend/
├── package.json                 # pnpm deps
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── prettier.config.json
├── Dockerfile                   # Multi-stage: dev & prod
└── src/
    ├── app/                     # Next.js App Router
    │   ├── layout.tsx           # Root layout, fonts, auth provider
    │   ├── globals.css          # Theme CSS variables, animations, scroll
    │   │
    │   ├── (public)/            # Auth pages (no sidebar)
    │   │   ├── login/page.tsx
    │   │   └── register/page.tsx
    │   │
    │   ├── dashboard/           # Protected dashboard
    │   │   ├── layout.tsx       # Sidebar + auth guard
    │   │   ├── page.tsx         # Sites list, welcome
    │   │   ├── sites/
    │   │   │   ├── new/page.tsx             # Onboarding wizard (3 steps)
    │   │   │   └── [site_id]/page.tsx       # Site editor
    │   │   ├── admin/page.tsx   # User management, stats, impersonate
    │   │   ├── mcp/page.tsx     # AI tool connection (Claude setup)
    │   │   ├── settings/page.tsx # Plan, billing, upgrade CTA
    │   │   └── help/page.tsx
    │   │
    │   ├── [site_slug]/         # Public site rendering (SSR, no auth)
    │   │   ├── layout.tsx
    │   │   ├── page.tsx         # Homepage
    │   │   ├── SiteRenderer.tsx # Shared renderer + nav
    │   │   ├── [page_slug]/page.tsx
    │   │   ├── sitemap.xml/route.ts
    │   │   └── robots.txt/route.ts
    │   │
    │   ├── preview/             # Draft preview (auth required)
    │   └── connect/             # OAuth callback
    │
    ├── components/
    │   ├── sections/            # 8 section renderers + SiteNavBar
    │   │   ├── HeroSection.tsx
    │   │   ├── FeaturesSection.tsx
    │   │   ├── TestimonialsSection.tsx
    │   │   ├── AboutSection.tsx
    │   │   ├── ContactSection.tsx
    │   │   ├── CtaSection.tsx
    │   │   ├── PricingSection.tsx
    │   │   ├── CustomSection.tsx
    │   │   ├── SiteNavBar.tsx   # Multi-page nav, mobile hamburger
    │   │   └── index.ts         # Component registry
    │   │
    │   ├── admin/
    │   │   ├── sidebar.tsx
    │   │   └── section-editors/ # One editor per section type + index.ts
    │   │
    │   ├── ui/                  # shadcn/ui components
    │   ├── auth-provider-wrapper.tsx
    │   ├── claude-connect.tsx
    │   └── ai-tools-connect.tsx
    │
    ├── hooks/
    │   ├── use-toast.ts         # Import from @/hooks/use-toast (not ui/)
    │   └── use-auth.ts
    │
    ├── lib/
    │   └── api.ts               # axios HTTP client with auth headers
    │
    └── test/                    # Vitest test files
```

## Backend Structure
```
backend/
├── pyproject.toml               # uv / hatchling config
├── Dockerfile
├── start.sh                     # alembic upgrade head → uvicorn
├── Makefile
│
├── alembic/                     # DB migrations
│   └── versions/
│       └── YYYYMMDD_HHMM_slug.py
│
├── seeds/
│   ├── seed.py
│   └── demo_data.py
│
└── src/
    ├── main.py                  # FastAPI app, CORS, router registration
    ├── config.py                # Pydantic settings (env vars)
    ├── database.py              # AsyncEngine, AsyncSessionLocal
    │
    ├── models/
    │   ├── user.py              # User, UserPlan, PLAN_SITE_LIMITS
    │   ├── site.py
    │   ├── page.py
    │   ├── content.py           # ContentSection (draft/published JSON)
    │   ├── page_version.py
    │   ├── mcp_client.py
    │   └── theme.py
    │
    ├── schemas/
    │   ├── content.py           # Section type schemas (HeroSection, etc.)
    │   ├── site.py
    │   ├── page.py
    │   ├── user.py
    │   ├── theme.py
    │   └── mcp.py
    │
    ├── api/
    │   ├── auth.py              # POST /api/auth/login (form data)
    │   ├── sites.py             # CRUD + plan limit enforcement
    │   ├── pages.py
    │   ├── content.py           # PUT by-type, POST publish
    │   ├── public.py            # GET /api/public/sites/{slug} (no auth)
    │   ├── themes.py
    │   ├── mcp.py               # MCP client registration + OAuth
    │   ├── oauth.py             # /authorize, /token endpoints
    │   ├── preview.py           # SSE for live preview
    │   └── admin.py             # Admin-only (users, stats, impersonate)
    │
    ├── services/
    │   ├── auth.py
    │   └── preview.py
    │
    └── tests/
        ├── unit/
        └── integration/
```

## MCP Server Structure
```
mcp_server/
├── pyproject.toml
├── Dockerfile
├── start.sh
└── src/
    └── aicms_mcp_server/
        ├── main.py              # FastAPI app
        ├── server.py            # MCPServer — all 17 tool implementations
        └── schemas/
```

## Key File Locations
| Purpose | Path |
|---------|------|
| Theme CSS variables | `frontend/src/app/globals.css` |
| Public site renderer | `frontend/src/app/[site_slug]/page.tsx` |
| Admin site editor | `frontend/src/app/dashboard/sites/[site_id]/page.tsx` |
| Onboarding wizard | `frontend/src/app/dashboard/sites/new/page.tsx` |
| Section component registry | `frontend/src/components/sections/index.ts` |
| Admin panel | `frontend/src/app/dashboard/admin/page.tsx` |
| Content schemas | `backend/src/schemas/content.py` |
| User model + plans | `backend/src/models/user.py` |
| Public API | `backend/src/api/public.py` |
| Sites API | `backend/src/api/sites.py` |
| MCP tools | `mcp_server/src/aicms_mcp_server/server.py` |
| DB migrations | `backend/alembic/versions/` |
| Dev CLI | `./cli.sh` |
| Nginx (dev) | `nginx/nginx.conf` |
| Nginx (prod) | `nginx/nginx.prod.conf` |

## Naming Conventions

### Frontend
- Components: `PascalCase.tsx`
- Hooks: `use-kebab-case.ts` (import from `@/hooks/`)
- Routes: file-based, dynamic via `[param]` brackets
- Import alias: `@/` maps to `src/`

### Backend
- Models: `PascalCase` class, `snake_case` table names (plural)
- Routers: `snake_case` file, `snake_case` endpoints
- Schemas: `PascalCase` (e.g., `SiteCreate`, `SiteResponse`)
- Enums: `snake_case` values (`UserPlan.free`, `UserPlan.pro`)
- Migrations: `YYYYMMDD_HHMM_description.py`
- Functions: `snake_case` throughout

### MCP
- Tools: `snake_case` (e.g., `update_section`, `publish_page`)

### General
- Env vars: `SCREAMING_SNAKE_CASE`
- Git: conventional commits (`feat(scope):`, `fix(scope):`, `docs(scope):`)
- No feature branches — commit directly to `main`
