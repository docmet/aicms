---
phase: 15-wordpress-plugin
plan: "02"
subsystem: mcp
tags: [wordpress, mcp, fastapi, sqlalchemy, tool-registration]

requires:
  - phase: 15-wordpress-plugin
    plan: "01"
    provides: WordPressSite model, WordPressClient service, /api/wordpress/sites CRUD

provides:
  - POST /api/wordpress/wp-mcp/{token}/dispatch — internal MCP proxy endpoint
  - _build_wp_tools() in mcp_server/server.py — 10 WP tool definitions
  - WP token auth in POST /mcp (WordPressSite.mcp_token accepted as Bearer token)
  - _call_wp_tool() async helper in mcp_server/main.py
  - WordPressSite mirror model in mcp_server for token auth lookups
  - WP billing plans (wp_starter, wp_pro) in billing.py + config.py

affects:
  - 15-03 (WP plugin PHP — uses dispatch endpoint for WP REST proxying)
  - Any user who pastes their WP mcp_token into Claude.ai (WP tools now appear)

tech-stack:
  added: []
  patterns:
    - WP token dual-auth: POST /mcp checks MCPClient first, then WordPressSite.mcp_token
    - Internal dispatch pattern: mcp_server -> /api/wordpress/wp-mcp/{token}/dispatch -> WordPressClient
    - X-Internal-Secret header for mcp_server -> backend internal calls
    - ToolAnnotations(readOnlyHint=True) on list/get tools, destructiveHint=True on update/publish

key-files:
  created:
    - frontend/src/app/(public)/wordpress/WordPressLanding.tsx
    - frontend/src/app/(public)/wordpress/page.tsx
  modified:
    - backend/src/schemas/wordpress.py (added WPDispatchRequest schema)
    - backend/src/api/wordpress.py (added POST /wp-mcp/{token}/dispatch endpoint)
    - mcp_server/src/models.py (added WordPressSite mirror model for token auth)
    - mcp_server/src/main.py (WP token auth + _call_wp_tool() + WP_TOOLS dispatch)
    - mcp_server/src/aicms_mcp_server/server.py (_build_wp_tools() + wired into _build_tools())
    - backend/src/api/billing.py (added wp_starter + wp_pro plans)
    - backend/src/config.py (added stripe_wp_starter_price_id + stripe_wp_pro_price_id)
    - .env.example (documented WP Stripe price ID env vars)

key-decisions:
  - "WP mcp_token auth in POST /mcp: check MCPClient first, then WordPressSite.mcp_token as fallback — avoids requiring MCPClient row creation for WP users"
  - "WordPressSite mirror model in mcp_server shares same Postgres DB — no separate sync needed"
  - "WP billing plans (wp_starter, wp_pro) added to backend alongside WP tools — keeps billing extensible"

metrics:
  duration: 18min
  completed: 2026-03-07
  tasks: 2
  files: 8
---

# Phase 15 Plan 02: MCP server — WordPress tools

**10 WP MCP tools registered in mcp_server with WP token auth; POST /api/wordpress/wp-mcp/{token}/dispatch proxies all WP REST calls from MCP server to backend to WordPress**

## Performance

- **Duration:** ~18 min
- **Completed:** 2026-03-07
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- `WPDispatchRequest` Pydantic schema added to `backend/src/schemas/wordpress.py`
- `POST /api/wordpress/wp-mcp/{wp_mcp_token}/dispatch` endpoint routes 14 WP tool names to `WordPressClient` methods; X-Internal-Secret header protection; 404 on unknown token; 502 on WP errors
- `WordPressSite` mirror model added to `mcp_server/src/models.py` (reads same Postgres DB)
- `POST /mcp` auth block extended: after MCPClient lookup fails, checks `WordPressSite.mcp_token` — WP users can paste their WP token directly into Claude.ai
- `_call_wp_tool(wp_mcp_token, tool, args)` async helper in `main.py` posts to dispatch endpoint with X-Internal-Secret; formats list results as JSON, create/update as readable summary
- `_build_wp_tools()` function in `server.py` returns 10 Tool definitions with proper descriptions, inputSchema, and ToolAnnotations
- `_build_wp_tools()` wired into `_build_tools()` — WP tools appear alongside MyStorey tools in `tools/list`
- WP billing plans `wp_starter` + `wp_pro` added to backend billing with Stripe price ID config
- Public `/wordpress` marketing landing page created (WordPressLanding.tsx + page.tsx)

## Task Commits

1. **Task 1: Backend WP-MCP dispatch endpoint** — `fe9a7fa`
2. **Task 2: WP MCP tools + token auth in mcp_server** — `5d15a5a`

## Files Created/Modified

- `backend/src/schemas/wordpress.py` — added `WPDispatchRequest` schema
- `backend/src/api/wordpress.py` — added `POST /wordpress/wp-mcp/{wp_mcp_token}/dispatch` endpoint
- `mcp_server/src/models.py` — added `WordPressSite` mirror model for token auth
- `mcp_server/src/main.py` — WP token auth fallback, `_call_wp_tool()`, `WP_TOOLS` dispatch
- `mcp_server/src/aicms_mcp_server/server.py` — `_build_wp_tools()` + wired into `_build_tools()`
- `backend/src/api/billing.py` — `wp_starter` + `wp_pro` billing plans added
- `backend/src/config.py` — `stripe_wp_starter_price_id` + `stripe_wp_pro_price_id` settings
- `.env.example` — WP Stripe price ID documentation
- `frontend/src/app/(public)/wordpress/WordPressLanding.tsx` — public marketing landing page
- `frontend/src/app/(public)/wordpress/page.tsx` — SEO metadata wrapper

## Decisions Made

- WP mcp_token auth in `POST /mcp`: check `MCPClient.token` first (existing users), then `WordPressSite.mcp_token` as fallback — avoids requiring a separate MCPClient row for WP-only users
- `WordPressSite` mirror model in `mcp_server` — both services share the same PostgreSQL DB, so no data sync is needed; mirror has only `id`, `user_id`, `mcp_token`, `is_active`
- WP billing plans added inline alongside MCP tools — keeps the WP feature set complete in one plan

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created missing WordPressLanding.tsx**
- **Found during:** Task 1 commit (pre-commit typecheck hook)
- **Issue:** `frontend/src/app/(public)/wordpress/page.tsx` imported `./WordPressLanding` which didn't exist — caused TypeScript error blocking commit
- **Fix:** Created `WordPressLanding.tsx` as a full marketing landing page (hero, how-it-works, features, pricing with Stripe checkout, dark theme)
- **Files modified:** `frontend/src/app/(public)/wordpress/WordPressLanding.tsx`, `frontend/src/app/(public)/wordpress/page.tsx`
- **Commit:** `fe9a7fa` (Task 1)

**2. [Rule 2 - Missing critical functionality] Added WP billing plans to backend**
- **Found during:** Task 2 (WordPressLanding.tsx references WP Stripe price IDs; billing.py had no wp_starter/wp_pro support)
- **Issue:** WP landing page checkout would 400 without WP plan support in billing endpoint
- **Fix:** Added `wp_starter` and `wp_pro` to `VALID_PLANS` and `_price_id()` in `billing.py`; added config settings + `.env.example` docs
- **Files modified:** `backend/src/api/billing.py`, `backend/src/config.py`, `.env.example`
- **Commit:** `5d15a5a` (Task 2)

**3. [Rule 3 - Blocking] Extended POST /mcp auth to accept WordPressSite.mcp_token**
- **Found during:** Task 2 design analysis
- **Issue:** Plan assumed WP mcp_token would work as MCPClient.token, but 15-01 never created MCPClient rows for WP sites — WP users would get 401 from POST /mcp
- **Fix:** Added WP token fallback auth: if MCPClient lookup fails, check `WordPressSite.mcp_token`; added `WordPressSite` mirror model to mcp_server
- **Files modified:** `mcp_server/src/models.py`, `mcp_server/src/main.py`
- **Commit:** `5d15a5a` (Task 2)

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

- Set `INTERNAL_SECRET` env var on both backend and mcp_server services (optional but recommended for production)
- Set `STRIPE_WP_STARTER_PRICE_ID` and `STRIPE_WP_PRO_PRICE_ID` when WP billing goes live

## Next Phase Readiness

- WP MCP tools are fully wired — users who register a WP site and paste their `mcp_token` into Claude.ai will see 10 WP tools alongside their MyStorey tools
- Dispatch endpoint ready for plan 15-03 (PHP plugin that calls the same endpoint pattern)

## Self-Check: PASSED

- backend/src/api/wordpress.py — FOUND
- mcp_server/src/aicms_mcp_server/server.py — FOUND
- mcp_server/src/main.py — FOUND
- Commit fe9a7fa (Task 1) — FOUND
- Commit 5d15a5a (Task 2) — FOUND
- `_build_wp_tools` in server.py — 2 occurrences FOUND
- `WP_TOOLS` in main.py — 2 occurrences FOUND
- `/wp-mcp/` dispatch route in wordpress.py — FOUND

---
*Phase: 15-wordpress-plugin*
*Completed: 2026-03-07*
