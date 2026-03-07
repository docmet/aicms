---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Launch Ready
status: executing
stopped_at: Completed 15-03-PLAN.md (WordPress frontend + billing plans)
last_updated: "2026-03-07T16:21:30.204Z"
last_activity: 2026-03-07 — Phase 14 planned (research → 7 plans → verified)
progress:
  total_phases: 17
  completed_phases: 1
  total_plans: 11
  completed_plans: 10
  percent: 14
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-07)

**Core value:** Any AI assistant a user already has can build, update, and publish their entire website through conversation — with zero new AI subscriptions required on our end.
**Current focus:** Phase 14 — Polish & Stability

## Current Position

Phase: 14 of 17 (Polish & Stability)
Plan: 7 plans across 2 waves (14-00 through 14-06) — ready to execute
Status: Planned, ready to execute
Last activity: 2026-03-07 — Phase 14 planned (research → 7 plans → verified)

Progress: [█░░░░░░░░░] 14%

## Performance Metrics

**Velocity:**
- Total plans completed: 0 (v1.1 milestone)
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 14–17 | TBD | - | - |

*Updated after each plan completion*
| Phase 14-polish-stability P00 | 3min | 2 tasks | 2 files |
| Phase 14 P00 | 3min | 2 tasks | 2 files |
| Phase 14 P01 | 15m | 2 tasks | 4 files |
| Phase 14-polish-stability P06 | 12 | 2 tasks | 2 files |
| Phase 14 P04 | 4 | 2 tasks | 5 files |
| Phase 14-polish-stability P05 | 15min | 1 tasks | 1 files |
| Phase 14-polish-stability P02 | 10min | 2 tasks | 6 files |
| Phase 15-wordpress-plugin P01 | 12min | 2 tasks | 9 files |
| Phase 15-wordpress-plugin P03 | 6min | 2 tasks | 9 files |

## Accumulated Context

### Decisions

From PROJECT.md Key Decisions table — decisions affecting current work:

- **Hosted bridge architecture for WP plugin**: SSE unreliable on shared WP hosting; reuse existing MCP infra — pending implementation
- **Modular add-on pricing over rigid tiers**: More flexible, better perceived value, easier upsell — pending UI
- **Affiliate tooling**: Use Rewardful ($49/mo) rather than build in-house until €5k MRR
- **WP plugin sequencing**: Ship WP plugin (Phase 15) before operator AI tools (OPS tools now in Phase 14 but scoped small); WP plugin is revenue
- **Webshop approach**: Embed first (Stripe Payment Links / Gumroad), native product section later
- [Phase 14-polish-stability]: Mark slug uniqueness tests xfail not skip so pytest discovers/counts them while SQLite cannot enforce PostgreSQL partial indexes
- [Phase 14-polish-stability]: Wave 0 xfail scaffold pattern: create test files before production code to satisfy Nyquist compliance for downstream plans
- [Phase 14]: Mark slug uniqueness tests xfail(strict=False) so pytest discovers them while SQLite cannot enforce PostgreSQL partial indexes
- [Phase 14]: URL mode toggle hidden when image already set; mode only affects empty-state UX
- [Phase 14]: Validate URL with new URL() constructor on blur + Enter; error shown inline without calling onChange
- [Phase 14-polish-stability]: Partial unique index (WHERE is_deleted=false) used instead of plain UniqueConstraint to allow slug reuse after soft-delete
- [Phase 14-polish-stability]: create_page wraps db.commit() in try/except IntegrityError returning 409, alongside SELECT fast-path for race-condition safety
- [Phase 14-polish-stability]: trigger_deployment is a stub explaining GitHub Actions flow — Coolify API wiring deferred to per-user site deployment phase
- [Phase 14-polish-stability]: Admin MCP tools verify access by catching 403 from /admin/stats — no new auth layer needed
- [Phase 14]: traces_sample_rate=0.0 — errors only, no performance tracing cost until explicitly enabled
- [Phase 14]: Sentry disabled via empty SENTRY_DSN string — safe local dev default, SENTRY_DSN already set in Coolify prod
- [Phase 14-polish-stability]: delete_page and delete_site get destructiveHint=True to signal MCP clients to show confirmation UI
- [Phase 14-polish-stability]: update_page warns about slug URL changes and directs AI to use publish_page for publishing (version snapshot)
- [Phase 14-polish-stability]: revert_to_version only writes to draft — must call publish_page after to go live
- [Phase 14-polish-stability]: flex-wrap on site editor header keeps all action buttons visible while allowing them to wrap to second row on mobile (375px)
- [Phase 14-polish-stability]: Tailwind grid-cols-1 sm:grid-cols-N pattern established for all section editor two/three-column grids
- [Phase 15-wordpress-plugin]: app_password_encrypted column stores plaintext for now; encryption layer deferred
- [Phase 15-wordpress-plugin]: mcp_token rotated automatically on credential change in WP site PATCH
- [Phase 15-wordpress-plugin]: Server/client split for landing page: page.tsx exports metadata, WordPressLanding.tsx handles hooks
- [Phase 15-wordpress-plugin]: AlertDialog not in shadcn/ui install — Dialog with open state used for WP site delete confirmation
- [Phase 15-wordpress-plugin]: wp_starter/wp_pro billing: VALID_PLANS extended, 503 guard if Stripe price ID env var not set; checkout buttons show Coming soon if NEXT_PUBLIC_ var empty

### Pending Todos

None yet.

### Blockers/Concerns

From CONCERNS.md — items relevant to Phase 14:
- Slug collision race condition: needs DB-level unique constraint (PLSH-04)
- No Sentry / structured logging in production (PLSH-05)
- MCP tool descriptions sparse — this IS the product for AI clients (PLSH-06)
- No email verification or password reset flows (not in active v1 scope — deferred)

## Session Continuity

Last session: 2026-03-07T16:21:30.202Z
Stopped at: Completed 15-03-PLAN.md (WordPress frontend + billing plans)
Resume file: None
