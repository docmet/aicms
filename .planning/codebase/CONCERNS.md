# Concerns & Technical Debt

## Security Concerns

### Critical
- **Insecure JWT default**: `config.py` defaults `jwt_secret = "your-secret-key-change-in-production"` — must be overridden in `.env`, but a footgun if not set
- **Tokens in localStorage**: Auth JWT and `admin_token_backup` stored in `localStorage` — vulnerable to XSS. Should migrate to HttpOnly cookies
- **MCP client tokens not hashed**: `MCPClient.token` stored as plaintext in DB — should be hashed like passwords
- **OAuth codes in-memory**: `_oauth_codes` dict in `backend/src/api/mcp.py` is lost on restart; not suitable for multi-instance deployments

### Medium
- **Admin impersonation — no audit log**: `POST /api/admin/impersonate/{user_id}` generates tokens for any user with no audit trail
- **Placeholder OAuth endpoints**: `/authorize` and `/token` in `oauth.py` auto-approve with no consent screen and return `"mock-access-token"` — not production-grade OAuth
- **No CSRF protection**: No CSRF tokens or SameSite cookie configuration visible
- **No rate limiting on auth/exchange endpoints**: `/api/auth/login` and `/exchange-code` could be brute-forced; nginx prod has generic rate limiting but not fine-grained

## Known Issues / Bugs

- **`generate_section` is a placeholder**: MCP tool exists but has no real AI generation logic — returns placeholder content
- **No email verification**: Users registered immediately without email confirmation (`backend/src/api/auth.py`)
- **No password reset**: No password reset / recovery flow exists
- **Slug collision race condition**: Between checking slug uniqueness and creating the record, another request could claim the same slug (no DB-level unique constraint race protection)
- **Soft deletes accumulate**: No cleanup mechanism for old soft-deleted records (sites, pages, sections)

## Technical Debt

### Backend
- **14+ `# type: ignore[assignment]`** annotations in `admin.py` — type casting issues not properly resolved
- **Bare `except Exception:`** in `database.py` without logging — loses error context
- **No validation that theme slug exists**: `SiteCreate`/`SiteUpdate` accepts any theme string without checking themes table
- **No content schema version migration**: If section defaults change, existing stored JSON with old schema could break rendering
- **Broad exception handlers**: Several API endpoints swallow errors without logging the failing operation

### Frontend
- **Few tests**: Vitest configured but test files largely absent
- **No E2E tests**: No Playwright/Cypress setup
- **Admin page uses `# type: ignore` equivalent patterns**: Some `any` typing in admin dashboard

## Performance Concerns

- **N+1 query for badge**: `_site_shows_badge()` in `backend/src/api/public.py` queries `User` separately per site — should use eager join
- **Unindexed slug lookups**: `Site.slug` and `Page.slug` filtered without explicit DB indexes (relied on by public API on every request)
- **Broadcast all sections on any change**: `_broadcast_sections` in `backend/src/api/content.py` fetches and serializes all sections even for single-field updates
- **Default connection pool**: `create_async_engine` uses defaults — may need `pool_size`/`max_overflow` tuning under load
- **No caching**: No Redis or in-memory cache for public site data (every request hits the DB)

## Fragile Areas

- **Content JSON validation**: Section JSON is parsed and loosely validated — malformed content could cause rendering errors on the frontend
- **MCP server single point of failure**: Backend OAuth and client registration endpoints depend on MCP server availability — no retry or circuit breaker
- **SSE preview connection**: Long-lived SSE connections in `preview.py` — no reconnection logic or heartbeat visible
- **In-memory OAuth codes**: Lost on restart, one server only — will break in horizontal scaling
- **bcrypt version pin**: `bcrypt<4.1.0` in `pyproject.toml` — unusual version cap, may cause issues as bcrypt releases updates

## Missing Features (Production Gaps)

- **Email verification** — no flow exists (planned Phase 14)
- **Password reset** — no flow exists (planned Phase 14)
- **AI automations** — Agency plan feature; `generate_section` is a placeholder (planned Phase 14)
- **API rate limiting** (fine-grained) — nginx has generic limits but no per-user or per-endpoint limits
- **Structured logging / observability** — no structured logs, no tracing, no error monitoring (Sentry planned Phase 14)
- **Backup / restore** — no export/import for site content
- **Graceful MCP server degradation** — site creation fails hard if MCP server is down
- **Static HTML snapshot generation** — Phase 12 partial; Cloudflare R2/Pages serving not yet implemented

### Resolved (no longer gaps)
- ~~Billing integration~~ — Stripe Checkout + webhook + Customer Portal done (Phase 8)
- ~~Custom domains~~ — `domain` field on Site + Settings UI + MCP tool done (Phase 12)
- ~~File/image uploads~~ — Cloudflare R2 + local volume storage done (Phase 9)

## Dependency Concerns

- **`mcp>=1.0.0`** — relatively new library, may have breaking changes in minor versions
- **`requires-python = ">=3.13"`** — stricter than most production environments
- **`>=` version ranges** (not pinned) — `fastapi>=0.115.0` etc. could introduce breaking changes on fresh installs; `uv.lock` provides actual pinning
- **`bcrypt<4.1.0`** — unclear why 4.1+ excluded; may need investigation before bcrypt releases 4.1

## Architecture Concerns

- **No refresh tokens**: JWTs expire; users get logged out abruptly with no token refresh mechanism
- **No multi-tenancy audit**: User isolation relies on foreign keys + manual `user_id` filters in queries — no systematic audit that all queries properly scope to authenticated user
- **Draft/published complexity**: Two JSON columns per section creates state complexity and could diverge unexpectedly
- **No transaction isolation tuning**: Default async session isolation may allow dirty reads during concurrent section updates
- **Admin impersonation session tracking**: No way for a user to know if their active session is admin-impersonated
