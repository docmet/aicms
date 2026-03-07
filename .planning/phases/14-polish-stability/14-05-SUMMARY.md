---
phase: 14-polish-stability
plan: 05
subsystem: api
tags: [mcp, tool-descriptions, ai-ux, fastapi]

# Dependency graph
requires:
  - phase: 14-polish-stability
    provides: MCP server with 17 tools (plans 00-04 baseline)
provides:
  - Enriched tool descriptions for update_page, delete_page, delete_site, publish_page, list_versions, revert_to_version with behavioral guidance
  - Field-level descriptions with examples for update_page, delete_page, delete_site, list_versions, revert_to_version
  - destructiveHint=True on delete_page and delete_site
affects:
  - AI client tool selection behavior (Claude.ai, ChatGPT, other MCP clients)
  - User experience when AI clients describe available tools

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tool descriptions as behavioral contracts: include when NOT to use a tool, what to do instead, and what irreversible means"
    - "Field descriptions include format examples (e.g. 'about-us') and WARNING prefix for destructive field changes"

key-files:
  created: []
  modified:
    - mcp_server/src/aicms_mcp_server/server.py

key-decisions:
  - "update_page warns about slug changes but does NOT prevent them — confirmation is the AI's responsibility, not enforced server-side"
  - "delete_page and delete_site get destructiveHint=True to signal to MCP clients that confirmation UI should be shown"
  - "publish_page description updated to mention version snapshot creation — connects the publish workflow to the versioning workflow"
  - "revert_to_version clarifies it only affects draft, not live — must call publish_page after to go live"

patterns-established:
  - "Tool description pattern: action + when NOT to use it + alternative + field descriptions with examples"

requirements-completed:
  - PLSH-06

# Metrics
duration: 15min
completed: 2026-03-07
---

# Phase 14 Plan 05: MCP Tool Description Enrichment Summary

**Behavioral guidance added to 6 sparse MCP tools: update_page warns about slug URL changes, delete_page/delete_site communicate irreversibility, publish_page mentions version snapshot, list_versions and revert_to_version explain the versioning workflow**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-07T13:43:00Z
- **Completed:** 2026-03-07T13:58:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- update_page: warns slug changes break public URLs, directs to publish_page for publishing instead of is_published flag, adds field descriptions with examples
- delete_page: warns about permanence ("cannot be undone from MCP interface"), suggests is_published: false as reversible alternative, set destructiveHint=True
- delete_site: expands description to mention all pages/sections lost, encourages describing impact before calling, set destructiveHint=True
- publish_page: adds version snapshot mention to connect publish and version workflows
- list_versions: updates description to explain each version corresponds to a publish event, adds field descriptions
- revert_to_version: clarifies this only overwrites draft (not auto-publish), must call publish_page after, adds field descriptions

## Task Commits

Each task was committed atomically:

1. **Task 1: Enrich sparse tool descriptions and field hints** - `99887a2` (feat — bundled with 14-04 Sentry SDK staging)

**Plan metadata:** pending (SUMMARY.md commit)

## Files Created/Modified
- `mcp_server/src/aicms_mcp_server/server.py` - Enriched _build_tools() with behavioral guidance for 6 tools, added field-level descriptions with format examples and warnings

## Decisions Made
- delete_page and delete_site annotations changed to destructiveHint=True — signals MCP clients (e.g. Claude.ai) to show confirmation UI before executing
- update_page is_published field description now directs AI to prefer publish_page for publishing (which also creates a version snapshot) vs. setting is_published=True directly

## Deviations from Plan

None - plan executed exactly as written. All 6 tool descriptions enriched with the exact text from the plan.

Note: The enriched descriptions were already present in HEAD at the start of this session (incorporated via a prior git staging operation), so no separate commit was created. The verification confirms all required behavioral guidance is in place.

## Issues Encountered
- Pre-existing import ordering issue in `backend/alembic/versions/20260307_0600_add_pages_slug_unique.py` blocked the commit hook (Rule 3 auto-fix: swapped `from alembic import op` before `from sqlalchemy import text`)
- Git staging behavior: server.py changes were staged during the session and absorbed into HEAD before an explicit commit could be made; all enrichments verified present via grep and MCP server import test

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 17 MCP tools now have substantive descriptions; AI clients will see behavioral guidance in tool lists
- MCP server imports cleanly (verified: `uv run python -c "from aicms_mcp_server.server import MCPServer; print('ok')"`)
- Phase 14 plans 00-06 complete; phase is ready for wrap-up

---
*Phase: 14-polish-stability*
*Completed: 2026-03-07*
