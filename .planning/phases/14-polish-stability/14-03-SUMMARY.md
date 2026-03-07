---
phase: 14-polish-stability
plan: "03"
subsystem: database
tags: [postgres, alembic, sqlalchemy, partial-index, uniqueness, race-condition]

# Dependency graph
requires:
  - phase: 14-00
    provides: test scaffold for slug uniqueness (test_slug_uniqueness.py stubs)
provides:
  - Partial unique index uq_pages_site_slug_active on pages(site_id, slug) WHERE is_deleted=false
  - IntegrityError → HTTP 409 handler in create_page endpoint
affects: [pages-api, mcp-tools, slug-routing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Partial unique index: enforce uniqueness only on active (non-deleted) rows via WHERE clause"
    - "TOCTOU guard: SELECT fast-path check + IntegrityError catch on commit for race condition safety"

key-files:
  created:
    - backend/alembic/versions/20260307_0600_add_pages_slug_unique.py
  modified:
    - backend/src/api/pages.py

key-decisions:
  - "Use partial index (WHERE is_deleted=false) instead of plain unique constraint to allow slug reuse after soft-delete"
  - "Keep existing SELECT check as fast-path 400; add IntegrityError catch as authoritative guard for concurrent creates"

patterns-established:
  - "Soft-delete uniqueness: use partial indexes to exclude deleted rows from uniqueness constraints"
  - "Race-condition safety: wrap db.commit() in try/except IntegrityError returning 409"

requirements-completed: [PLSH-04]

# Metrics
duration: 15min
completed: 2026-03-07
---

# Phase 14 Plan 03: Page Slug Uniqueness Summary

**Partial unique index on pages(site_id, slug) WHERE is_deleted=false eliminates TOCTOU race condition in concurrent page creates, returning HTTP 409 on slug conflict**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-07T13:50:00Z
- **Completed:** 2026-03-07T14:05:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created Alembic migration 20260307_0600 adding partial unique index `uq_pages_site_slug_active` on pages(site_id, slug) WHERE is_deleted=false
- Applied migration cleanly to dev database (`alembic current` shows 20260307_0600 as head)
- Updated `create_page` to wrap commit in try/except IntegrityError returning HTTP 409 (race-condition safe)
- Soft-deleted pages do not block slug reuse (the WHERE clause excludes them from the constraint)

## Task Commits

Work was included in surrounding commits:

1. **Task 1: Create Alembic migration** — included in `99887a2` feat(14-04): migration file created + import order fixed by ruff
2. **Task 2: Add IntegrityError handler** — included in `99887a2` feat(14-04): pages.py IntegrityError import + try/except wrap

## Files Created/Modified
- `backend/alembic/versions/20260307_0600_add_pages_slug_unique.py` — Migration: partial unique index on pages(site_id, slug) for non-deleted pages
- `backend/src/api/pages.py` — create_page wraps commit in try/except IntegrityError returning 409

## Decisions Made
- Used partial index (WHERE is_deleted=false) rather than a full unique constraint — this is the key design decision that allows slug reuse after soft-delete. A plain UniqueConstraint would block re-creation of a slug that was previously used by a deleted page.
- Kept the existing SELECT-based fast-path check (returns 400 for single-request duplicates immediately) alongside the IntegrityError catch (returns 409 for race conditions after commit). Both guards serve different purposes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Import sort order in migration file**
- **Found during:** Task 1 (migration file creation)
- **Issue:** ruff isort treats the local `alembic/` directory as first-party, requiring `from sqlalchemy import text` (third-party) before `from alembic import op` (first-party) with a blank line between them
- **Fix:** Reordered imports: `from sqlalchemy import text` then blank line then `from alembic import op`
- **Files modified:** backend/alembic/versions/20260307_0600_add_pages_slug_unique.py
- **Verification:** `./cli.sh lint:backend` passes
- **Committed in:** 99887a2 (prior commit that included migration)

**2. [Rule 1 - Bug] Duplicate `# type: ignore` comment in admin.py**
- **Found during:** Task 2 (typecheck verification)
- **Issue:** admin.py line 159 had duplicate `# type: ignore[call-overload]  # type: ignore[call-overload]` annotation
- **Fix:** Removed duplicate comment, leaving single `# type: ignore[call-overload]`
- **Files modified:** backend/src/api/admin.py
- **Verification:** `./cli.sh typecheck:backend` passes with "no issues found in 55 source files"
- **Committed in:** 606e419

---

**Total deviations:** 2 auto-fixed (both Rule 1 bug fixes)
**Impact on plan:** Both fixes required for lint/typecheck to pass. No scope creep.

## Issues Encountered
- The alembic binary is located at `/app/.venv/bin/alembic` in the container (not on PATH), requiring explicit path when running migrations.
- The migration file and pages.py IntegrityError handler were already committed in commit 99887a2 by a parallel plan execution — no duplicate work needed.

## Next Phase Readiness
- DB-level uniqueness constraint active on dev database
- create_page endpoint returns 409 (not 500) on slug conflict
- test_slug_uniqueness.py stubs (XFAIL) ready to be activated when integration test DB is wired up

---
*Phase: 14-polish-stability*
*Completed: 2026-03-07*
