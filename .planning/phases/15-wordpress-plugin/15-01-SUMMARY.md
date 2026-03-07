---
phase: 15-wordpress-plugin
plan: "01"
subsystem: api
tags: [wordpress, fastapi, sqlalchemy, httpx, alembic, application-password]

requires:
  - phase: 14-polish-stability
    provides: stable backend with user model, async SQLAlchemy patterns, test infra

provides:
  - wordpress_sites table with mcp_token and credential storage
  - CRUD API at /api/wordpress/sites (POST, GET, PATCH, DELETE)
  - WordPressClient service for WP REST API proxying (12 methods)
  - Application Password authentication for WP REST API
  - mcp_token generation (secrets.token_urlsafe) for WP plugin auth

affects:
  - 15-02 (WP MCP tools depend on WordPressClient and WordPressSite model)
  - 15-03 (WP plugin PHP will use mcp_token from this API)

tech-stack:
  added: [httpx (for WP REST API client)]
  patterns:
    - WordPressClient class with async httpx, BasicAuth, 15s timeout
    - Site probe-before-save pattern (validate credentials at registration time)
    - soft-delete via is_active=False (no hard deletes)
    - mcp_token rotation on credential change (PATCH re-probes + new token)

key-files:
  created:
    - backend/src/models/wordpress_site.py
    - backend/src/schemas/wordpress.py
    - backend/src/services/wordpress_client.py
    - backend/src/api/wordpress.py
    - backend/alembic/versions/20260307_0800_add_wordpress_sites.py
    - backend/src/tests/test_wordpress_api.py
  modified:
    - backend/src/models/__init__.py
    - backend/src/models/user.py
    - backend/src/main.py

key-decisions:
  - "Store app_password as plaintext for now (app_password_encrypted column name reserved for future encryption layer)"
  - "mcp_token rotated automatically when site_url or app_password changes in PATCH"
  - "DELETE is soft-delete (is_active=False) — token remains in DB for audit trail"
  - "WordPressClient uses Any return types to avoid httpx generic type complexity with mypy"
  - "API catches broad Exception (not just HTTPException) from get_site_info to handle mock side_effects in tests"

requirements-completed: ["WP-03", "WP-08"]

duration: 12min
completed: 2026-03-07
---

# Phase 15 Plan 01: Backend — WordPressSite model, WP REST client, and CRUD API

**SQLAlchemy WordPressSite model with mcp_token, httpx-based WP REST API client (12 methods), and FastAPI CRUD router at /api/wordpress/sites with Application Password validation on registration**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-07T17:06:00Z
- **Completed:** 2026-03-07T17:11:10Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- WordPressSite SQLAlchemy model with `mcp_token` (unique), `app_password_encrypted`, `site_url`, `is_active` columns and cascade relationship to User
- Alembic migration `20260307_0800_add_wordpress_sites` with correct `down_revision = "20260307_0700"`
- WordPressClient service covering all 12 required WP REST API methods using httpx BasicAuth
- FastAPI router at `/api/wordpress/sites` with ownership checks, probe-before-save, and mcp_token generation
- 4 passing tests: register, bad credentials (400), list, soft-delete

## Task Commits

1. **Task 1: WordPressSite model, Pydantic schemas, and Alembic migration** - `6f386ef` (feat)
2. **Task 2: WP REST API client service, WordPress API router, and tests** - `ddf1e89` (feat)

## Files Created/Modified

- `backend/src/models/wordpress_site.py` — WordPressSite SQLAlchemy model
- `backend/src/schemas/wordpress.py` — WordPressSiteCreate/Response/Update Pydantic schemas
- `backend/src/services/wordpress_client.py` — WordPressClient with 12 async WP REST methods
- `backend/src/api/wordpress.py` — CRUD router at /api/wordpress/sites
- `backend/alembic/versions/20260307_0800_add_wordpress_sites.py` — DB migration
- `backend/src/tests/test_wordpress_api.py` — 4 integration tests with mocked WP client
- `backend/src/models/__init__.py` — added WordPressSite export
- `backend/src/models/user.py` — added wordpress_sites relationship
- `backend/src/main.py` — registered wordpress_router at /api prefix

## Decisions Made

- `app_password_encrypted` column name reserved for future encryption; stores plaintext for now to keep implementation simple
- `mcp_token` rotated automatically whenever `site_url` or `app_password` changes in PATCH (security hygiene)
- DELETE uses soft-delete (`is_active=False`) not hard delete — token remains for audit trail
- `WordPressClient` methods return `Any` to avoid complex httpx generic type constraints with mypy strict mode
- Exception handler in POST/PATCH registration catches broad `Exception` (not just `HTTPException`) so tests using `side_effect=Exception(...)` behave correctly

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused `datetime` import from wordpress_site.py**
- **Found during:** Task 1 (lint pre-commit hook)
- **Issue:** `from datetime import datetime` was imported but SQLAlchemy `func.now()` is used for timestamps, making the import unused
- **Fix:** Removed the import
- **Files modified:** backend/src/models/wordpress_site.py
- **Verification:** ruff lint passes
- **Committed in:** 6f386ef (Task 1 commit)

**2. [Rule 1 - Bug] Fixed broad Exception catch for WP probe in POST endpoint**
- **Found during:** Task 2 (test_register_wordpress_site_bad_credentials test failure)
- **Issue:** Router caught `HTTPException` only, but `WordPressClient.get_site_info` can raise any exception; test mock used `side_effect=Exception(...)` which leaked as 500
- **Fix:** Changed `except HTTPException` to `except Exception` in the registration endpoint probe block
- **Files modified:** backend/src/api/wordpress.py
- **Verification:** test_register_wordpress_site_bad_credentials passes with 400 response
- **Committed in:** ddf1e89 (Task 2 commit)

**3. [Rule 1 - Bug] Fixed isort import ordering for wordpress_router in main.py**
- **Found during:** Task 2 (lint pre-commit hook)
- **Issue:** `from src.api.wordpress import router as wordpress_router` placed at wrong alphabetical position (after billing instead of after themes)
- **Fix:** Moved import to correct alphabetical position between themes and config
- **Files modified:** backend/src/main.py
- **Verification:** ruff/isort passes
- **Committed in:** ddf1e89 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 bugs caught by lint/tests)
**Impact on plan:** All fixes necessary for lint/test correctness. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None — no external service configuration required. WP credentials are provided per-site by users at registration time.

## Next Phase Readiness

- WordPressSite model and WordPressClient ready for plan 15-02 (WP MCP tools)
- `/api/wordpress/sites` CRUD available for plan 15-03 (PHP plugin + frontend)
- `mcp_token` generation complete — plugin will use this token to authenticate MCP calls

---
*Phase: 15-wordpress-plugin*
*Completed: 2026-03-07*
