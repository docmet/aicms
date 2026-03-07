---
phase: 14-polish-stability
plan: "00"
subsystem: testing
tags: [pytest, xfail, slug-uniqueness, admin-ops, integration-tests]

# Dependency graph
requires:
  - phase: 13-sharing-beta
    provides: stable codebase with conftest.py fixtures and async test infrastructure
provides:
  - "test_slug_uniqueness.py with 3 tests covering PLSH-04 page slug uniqueness behaviors"
  - "test_admin_ops.py with 4 xfail stubs for OPS-01/02/03 admin endpoint and MCP tools"
affects:
  - 14-03-PLAN
  - 14-06-PLAN

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "xfail scaffolding: write test stubs in Wave 0 before production code ships so downstream plans have verify targets"
    - "trailing slash pattern: FastAPI routes with prefix+trailing-slash require /api/sites/ not /api/sites"

key-files:
  created:
    - backend/src/tests/test_slug_uniqueness.py
    - backend/src/tests/test_admin_ops.py
  modified: []

key-decisions:
  - "Mark slug uniqueness tests xfail (not skip) so pytest discovers and counts them while SQLite in-memory DB cannot enforce PostgreSQL partial indexes"
  - "Mark admin ops tests xfail rather than skip to maintain discoverability and count for Nyquist compliance"

patterns-established:
  - "Wave 0 scaffold: test files created before production code to satisfy Nyquist compliance for downstream plans"
  - "xfail not skip: xfail allows pytest to discover and count tests while communicating they need infrastructure not yet in place"

requirements-completed:
  - PLSH-04
  - OPS-01
  - OPS-02
  - OPS-03

# Metrics
duration: 3min
completed: 2026-03-07
---

# Phase 14 Plan 00: Test Scaffold for Slug Uniqueness and Admin Ops Summary

**xfail test scaffolds for PLSH-04 (slug uniqueness) and OPS-01/02/03 (admin ops) — 3 + 4 tests importable and discoverable by pytest before production code ships**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-07T13:49:21Z
- **Completed:** 2026-03-07T13:52:13Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created `test_slug_uniqueness.py` with 3 tests: 2 xfail (duplicate slug 409, soft-delete reuse) pending plan 14-03 migration, 1 passing immediately (cross-site slug sharing)
- Created `test_admin_ops.py` with 4 xfail stubs for admin sites endpoint + 3 MCP tool tests pending plan 14-06
- Full test suite remains green: 6 passed, 6 xfailed across all backend tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Create test_slug_uniqueness.py** - `f7c4e63` (test)
2. **Task 2: Create test_admin_ops.py stubs** - `ffb174a` (test)

## Files Created/Modified
- `backend/src/tests/test_slug_uniqueness.py` - 3 integration tests for page slug uniqueness (PLSH-04)
- `backend/src/tests/test_admin_ops.py` - 4 xfail stubs for admin endpoint and MCP admin tools (OPS-01/02/03)

## Decisions Made
- Used `xfail(strict=False)` rather than `pytest.mark.skip` so tests are discovered and counted, while clearly communicating they need infrastructure not yet shipped. The `strict=False` allows them to unexpectedly pass without causing failures.
- Fixed trailing slash issue in `_create_user_and_site` helper: FastAPI redirects `/api/sites` (no trailing slash) to `/api/sites/` — used `/api/sites/` to avoid 307 redirect.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused imports and fixed trailing slash in site creation URL**
- **Found during:** Task 1 (test_slug_uniqueness.py)
- **Issue:** Plan template included unused imports (`User`, `Site`, `AuthService`) causing ruff F401 errors. Site creation URL `/api/sites` caused 307 redirect (FastAPI trailing-slash redirect), making `test_pages_on_different_sites_can_share_slug` fail unexpectedly.
- **Fix:** Removed the three unused imports. Changed `/api/sites` to `/api/sites/` in the `_create_user_and_site` helper.
- **Files modified:** `backend/src/tests/test_slug_uniqueness.py`
- **Verification:** `uv run ruff check` passes; test passes; full suite green.
- **Committed in:** `f7c4e63` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Necessary correctness fix. No scope creep. Plan template had imports that were not used in the final test file.

## Issues Encountered
- Plan template imports (`User`, `Site`, `AuthService`) were appropriate for `test_admin_ops.py` (where `AuthService` and `User` ARE used in `_create_admin_user`) but not for `test_slug_uniqueness.py` (which uses only the HTTP client). Removed the unused imports from the slug test file.
- FastAPI trailing-slash redirect: the sites router mounts at prefix `/api/sites` with route `POST /` — the full path is `/api/sites/`. Using `/api/sites` without trailing slash triggers a 307.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Wave 0 scaffold complete — plans 14-03 and 14-06 now have pytest-importable test files they can run against
- plan 14-03 (slug uniqueness DB constraint) can remove xfail markers from test_slug_uniqueness.py after adding the migration
- plan 14-06 (admin ops endpoint + MCP tools) can remove xfail markers from test_admin_ops.py after shipping the endpoint and tools

---
*Phase: 14-polish-stability*
*Completed: 2026-03-07*

## Self-Check: PASSED

- FOUND: backend/src/tests/test_slug_uniqueness.py
- FOUND: backend/src/tests/test_admin_ops.py
- FOUND: .planning/phases/14-polish-stability/14-00-SUMMARY.md
- FOUND: commit f7c4e63 (test_slug_uniqueness.py)
- FOUND: commit ffb174a (test_admin_ops.py)
