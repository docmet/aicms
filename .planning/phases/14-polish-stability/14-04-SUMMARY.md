---
phase: 14-polish-stability
plan: "04"
subsystem: infra
tags: [sentry, error-monitoring, fastapi, python]

# Dependency graph
requires: []
provides:
  - sentry-sdk[fastapi] installed in backend (v2.54.0)
  - Conditional Sentry init in main.py before FastAPI app creation
  - sentry_dsn Setting field (empty string default = disabled)
  - backend/.env.example created documenting all env vars
affects: [production-ops, error-alerting]

# Tech tracking
tech-stack:
  added: [sentry-sdk[fastapi]==2.54.0]
  patterns:
    - Conditional SDK init on settings field — disabled when env var absent (safe for local dev)
    - traces_sample_rate=0.0 — errors-only capture, no performance tracing cost

key-files:
  created:
    - backend/.env.example
  modified:
    - backend/src/config.py
    - backend/src/main.py
    - backend/pyproject.toml
    - backend/uv.lock

key-decisions:
  - "traces_sample_rate=0.0 — errors only, no performance tracing cost until explicitly enabled"
  - "Sentry disabled when SENTRY_DSN is empty string — safe default for local dev, no code changes needed"
  - "sentry_sdk.init() placed after settings = get_settings() and before app = FastAPI() — module-level init"
  - "SENTRY_DSN already set in Coolify production env vars — no Coolify API call needed"

patterns-established:
  - "Monitoring pattern: conditional SDK init via settings field — copy for future integrations (Datadog, etc.)"

requirements-completed: [PLSH-05]

# Metrics
duration: 4min
completed: 2026-03-07
---

# Phase 14 Plan 04: Sentry SDK Integration Summary

**sentry-sdk[fastapi] v2.54.0 integrated with conditional init before FastAPI app creation — errors captured in production, disabled in local dev via empty SENTRY_DSN**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-07T13:52:35Z
- **Completed:** 2026-03-07T13:56:06Z
- **Tasks:** 3 (2 code tasks + 1 documented)
- **Files modified:** 5

## Accomplishments

- Installed `sentry-sdk[fastapi]==2.54.0` via `uv add` (pyproject.toml + uv.lock updated)
- Added `sentry_dsn: str = ""` to Settings class — empty string disables Sentry cleanly
- Added `sentry_sdk.init()` in main.py after `settings = get_settings()`, before `app = FastAPI()` — correct module-level placement
- Created `backend/.env.example` documenting all 25+ environment variables including `SENTRY_DSN`
- Backend starts cleanly in dev with no SENTRY_DSN set — zero startup errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Install sentry-sdk and add config field** - `99887a2` (feat)
2. **Task 2: Initialize Sentry in main.py before app creation** - `51b68b9` (feat)
3. **Task 3: Coolify SENTRY_DSN** - N/A (already set, documented only)

**Plan metadata:** see final commit below

## Files Created/Modified

- `backend/src/config.py` - Added `sentry_dsn: str = ""` field to Settings class
- `backend/src/main.py` - Added `import sentry_sdk` and conditional `sentry_sdk.init()` before `app = FastAPI()`
- `backend/pyproject.toml` - Added `sentry-sdk[fastapi]>=2.54.0` dependency
- `backend/uv.lock` - Updated lockfile with sentry-sdk 2.54.0
- `backend/.env.example` - Created with all env vars documented, including `SENTRY_DSN=`

## Decisions Made

- `traces_sample_rate=0.0` chosen to capture errors only, avoiding performance tracing costs. Can be increased later (e.g., 0.1 for 10% of requests) when performance profiling is needed.
- Sentry's FastAPI integration (`sentry-sdk[fastapi]` extra) installs `SentryAsgiMiddleware` automatically — no manual middleware registration needed.
- Empty string default for `sentry_dsn` rather than `Optional[str]` — simpler conditional `if settings.sentry_dsn:` with no None checks.

## Production Setup

**SENTRY_DSN is already set in Coolify production environment variables.** No action required.

For new deployments or environment resets:
1. Create a Sentry project at https://sentry.io for "MyStorey" (Python/FastAPI platform)
2. Copy the DSN from Project Settings > Client Keys
3. Set `SENTRY_DSN=https://...@sentry.io/...` in Coolify environment variables for the backend service
4. Redeploy — Sentry will immediately start capturing unhandled exceptions

## Alerting Recommendations

Configure Sentry alert rules for low-noise alerting:
- **New Issue** alerts only (first occurrence) — not "every event" (spam)
- Email or Slack channel (#mystorey-errors) for notification delivery
- Consider setting an issue owner (auto-assign to team)
- Daily digest rather than immediate-per-error email for non-critical projects

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed isort ordering in pre-existing alembic migration**
- **Found during:** Task 1 (first commit attempt)
- **Issue:** `backend/alembic/versions/20260307_0600_add_pages_slug_unique.py` had unsorted imports (`from alembic import op` before `from sqlalchemy import text` but ruff/isort treats alembic as local package requiring a blank line separator)
- **Fix:** Ran `uv run ruff check --fix` to auto-sort the imports — `sqlalchemy` moved before `alembic` with blank line separator
- **Files modified:** `backend/alembic/versions/20260307_0600_add_pages_slug_unique.py`
- **Verification:** `ruff check .` passes with "All checks passed!"
- **Committed in:** `99887a2` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking/pre-existing lint error)
**Impact on plan:** Auto-fix necessary to unblock commit. No scope creep. The migration file was from a prior task (14-03) and had an import ordering issue that ruff hadn't caught until this commit's pre-commit hook ran.

## Issues Encountered

- `uv add` on the host correctly updates `pyproject.toml` and `uv.lock`, but the running dev container has a persistent `.venv` volume. Running `uv sync` inside the container was required to install sentry_sdk into the active virtual environment without a full container rebuild.
- `python` in the container is system Python (not venv); app runs via `uv run uvicorn`. Verification must use `uv run python -c "import sentry_sdk"`.

## Next Phase Readiness

- Sentry is ready for production error capture — activate by ensuring SENTRY_DSN is set in Coolify (already done per operator)
- No blockers for next plan
- The `backend/.env.example` file created here serves as a reference for all env vars — useful for new developer onboarding

---
*Phase: 14-polish-stability*
*Completed: 2026-03-07*
