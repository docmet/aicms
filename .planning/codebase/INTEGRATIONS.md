# Integrations

## Databases
- **Primary**: PostgreSQL 16 (Alpine in Docker)
- **Driver**: asyncpg 0.30+ (async Python driver)
- **ORM**: SQLAlchemy 2.0+ with `AsyncSession` / `async_sessionmaker`
- **Migrations**: Alembic — auto-run on startup via `backend/start.sh`
- **URL format**: `postgresql+asyncpg://user:password@host:port/dbname`
- **Connection**: `create_async_engine` (default pool settings)
- **Health checks**: `pg_isready` in Docker Compose
- **Volume**: `postgres_data` (persistent in both dev and prod)

## Authentication
- **JWT**:
  - Algorithm: HS256 (configurable via `JWT_ALGORITHM`)
  - Expiration: 30–60 min (`JWT_EXPIRATION_MINUTES`)
  - Secret: `JWT_SECRET` env var (default is an insecure placeholder)
  - Library: python-jose with cryptography
  - Token endpoint: `POST /api/auth/login` (form data, not JSON)
- **Password hashing**: bcrypt via passlib
- **MCP OAuth2**:
  - Authorization Code flow with PKCE support
  - Endpoints: `GET /authorize`, `POST /token`
  - Auth codes: 5-minute TTL, single-use, stored in-memory dict
  - Dynamic Client Registration (DCR) at `/mcp`
  - DCR response echoes `redirect_uris` back (required by Claude)
- **MCP client tokens**: Plain bearer token stored in `MCPClient.token` (not hashed)

## MCP / AI Integration
- **Protocol**: MCP 1.0+ (Model Context Protocol)
- **Transport**: HTTP + SSE
- **Auth**: Bearer token header only; generic `POST /mcp` endpoint (no client_id in URL)
- **17 MCP tools**:
  - Sites: `list_sites`, `create_site`, `get_site_info`, `describe_site`, `update_site`, `delete_site`
  - Pages: `list_pages`, `create_page`, `update_page`, `delete_page`, `publish_page`
  - Content: `get_page_content`, `update_section`, `generate_section`, `delete_section`
  - Themes: `list_themes`, `apply_theme`
- **MCP URL shown to users**: `{origin}/mcp` (generic)
- **Old endpoint**: `/mcp/{client_id}` kept for backward compat

## Infrastructure

### Reverse Proxy (Nginx)
- **Images**: `nginx:alpine`
- **Port**: 80 (SSL terminated upstream by Coolify/Traefik)
- **Routes**:
  - `/api/*` → `backend:8000`
  - `/mcp`, `/mcp/` → `mcp_server:8000`
  - `/oauth/*` → `backend:8000`
  - `/*` → `frontend:3000`
- **Configs**: `nginx/nginx.conf` (dev), `nginx/nginx.prod.conf` (prod)
- **Production features**: gzip compression, security headers, rate limiting

### Docker Services (5 total)
| Service | Image | Port |
|---------|-------|------|
| nginx | nginx:alpine | 80 |
| frontend | node:22-alpine (prod) | 3000 |
| backend | python:3.13-slim | 8000 |
| mcp_server | python:3.13-slim | 8000 |
| postgres | postgres:16-alpine | 5432 |

### Backend API Routes
- `/api/auth/*` — login, register, token
- `/api/admin/*` — admin-only (is_admin check)
- `/api/sites/*` — site CRUD + page management
- `/api/public/sites/*` — public content (published only, no auth)
- `/api/themes/*` — listing and application
- `/api/mcp/*` — MCP OAuth and client management
- `/oauth/*` — OAuth authorize/token endpoints
- `/api/preview/*` — SSE draft preview

## External Services
- **No external LLM API calls** currently — `generate_section` is a placeholder
- **No email provider** — no email verification or password reset
- **No payment provider** — pricing tiers exist in DB but no billing integration yet
- **No CDN** — static assets served by Next.js / nginx directly
- **No object storage** — no file/image upload functionality yet
- **Deployment**: Coolify-compatible (Traefik handles SSL, DNS)
