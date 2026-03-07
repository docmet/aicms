---
phase: 14
slug: polish-stability
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-07
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (backend), vitest (frontend) |
| **Config file** | `backend/pyproject.toml`, `frontend/vitest.config.ts` |
| **Quick run command** | `./cli.sh test` |
| **Full suite command** | `./cli.sh lint && ./cli.sh typecheck && ./cli.sh test` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `./cli.sh test`
- **After every plan wave:** Run `./cli.sh lint && ./cli.sh typecheck && ./cli.sh test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-00-01 | 00 | 0 | PLSH-04 | unit | `pytest backend/src/tests/test_slug_uniqueness.py --collect-only` | ❌ created by this plan | ⬜ pending |
| 14-00-02 | 00 | 0 | OPS-01/02/03 | unit | `pytest backend/src/tests/test_admin_ops.py --collect-only` | ❌ created by this plan | ⬜ pending |
| 14-01-01 | 01 | 1 | PLSH-01/02 | manual | — | ✅ | ⬜ pending |
| 14-01-02 | 01 | 1 | PLSH-01/02 | manual | — | ✅ | ⬜ pending |
| 14-02-01 | 02 | 1 | PLSH-03 | manual | — | ✅ | ⬜ pending |
| 14-03-01 | 03 | 1 | PLSH-04 | unit | `pytest backend/src/tests/test_slug_uniqueness.py -x` | ✅ (created by 14-00) | ⬜ pending |
| 14-04-01 | 04 | 1 | PLSH-05 | unit | `./cli.sh test` | ✅ | ⬜ pending |
| 14-05-01 | 05 | 1 | PLSH-06 | manual | — | ✅ | ⬜ pending |
| 14-06-01 | 06 | 1 | OPS-01/02/03 | unit | `pytest backend/src/tests/test_admin_ops.py -x` | ✅ (created by 14-00) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Plan 14-00 creates the test scaffold files before any implementation plans run:
- `backend/src/tests/test_slug_uniqueness.py` — 3 tests for PLSH-04 (2 xfail until migration applied, 1 passes immediately)
- `backend/src/tests/test_admin_ops.py` — 4 stubs for OPS-01/02/03 (all xfail until plan 14-06 ships)

Plans 14-03 and 14-06 depend on 14-00 (`depends_on: ["14-00"]`) so pytest targets exist before they run.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Section editors render correctly, no glitches | PLSH-01 | Visual regression | Open each of 8 section types in editor, check for clipped/overflowing content |
| Image fields show dimension hints + URL paste flow | PLSH-02 | Visual/UX | Open hero/about/testimonials editors, verify hint text and URL input appear |
| Admin editor usable on mobile | PLSH-03 | Responsive layout | Resize browser to 375px width, verify hamburger, scrollable editors, save works |
| Sentry captures exceptions in production | PLSH-05 | Live environment | Trigger intentional 500 error in staging, verify Sentry receives event within 30s |
| Admin MCP tools work via chat | OPS-01/02/03 | End-to-end AI | Connect Claude.ai MCP, ask for stats/sites/deploy, verify correct responses |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
