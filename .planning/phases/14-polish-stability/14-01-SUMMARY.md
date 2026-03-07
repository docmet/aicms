---
phase: 14-polish-stability
plan: "01"
subsystem: frontend
tags: [image-picker, editors, testimonials, ux]
dependency_graph:
  requires: []
  provides: [ImagePicker-url-paste, TestimonialsEditor-avatar]
  affects: [frontend/admin]
tech_stack:
  added: []
  patterns: [two-mode-toggle, inline-validation]
key_files:
  created: []
  modified:
    - frontend/src/components/admin/ImagePicker.tsx
    - frontend/src/components/admin/section-editors/HeroEditor.tsx
    - frontend/src/components/admin/section-editors/AboutEditor.tsx
decisions:
  - "URL mode toggle hidden when image already set; mode only affects the empty-state UX"
  - "Validate with new URL() constructor on blur + Enter; error shown inline without calling onChange"
  - "Auto-fixed pre-existing import sort error in alembic migration (Rule 3 — blocked hook)"
metrics:
  duration: "~15 minutes"
  completed: "2026-03-07"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 4
---

# Phase 14 Plan 01: ImagePicker URL Paste Mode + Editor Improvements Summary

**One-liner:** Added Library/Paste URL two-mode toggle to ImagePicker with `new URL()` validation, and updated dimension hints on HeroEditor (logo: 400x200) and AboutEditor (image: 1200x800).

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Add URL-paste tab to ImagePicker | 99887a2 | ImagePicker.tsx |
| 2 | Fix dimension hints on HeroEditor + AboutEditor | 99887a2 | HeroEditor.tsx, AboutEditor.tsx |

## What Was Done

### Task 1: URL-paste tab in ImagePicker

`ImagePicker.tsx` redesigned with internal `mode: "library" | "url"` state:

- Two-button toggle (Library / Paste URL) shown when no image is set
- Active mode button uses `variant="default"`, inactive uses `variant="outline"`
- Library mode: existing dashed-button behavior, opens MediaLibrary modal
- URL mode: `Input` field with `onBlur` + `onKeyDown` (Enter) validation via `new URL(value.trim())`
- Valid URL calls `onChange(trimmedUrl)`; invalid URL shows inline error "Enter a valid URL — e.g. https://example.com/image.jpg" without calling onChange
- Clearing the input calls `onChange(null)`
- Mode toggle is hidden when an image value is already set (preview with Change/Remove shows instead)

### Task 2: Testimonials avatar + dimension hints

**TestimonialsEditor** was already complete (prior session had done this):
- `siteId: string` in Props
- `avatar_url?: string | null` in `TestimonialItem`
- `ImagePicker` rendered per item with label "Avatar photo"
- `imageEditorProps` (including siteId) already passed in `page.tsx`

**HeroEditor** logo hint updated:
- From: `"Optional logo shown in the hero area."`
- To: `"Optional logo shown in the hero area. Recommended: 400×200 px PNG (transparent bg)."`

**AboutEditor** image hint updated:
- From: `"Displayed alongside your about text in a two-column layout."`
- To: `"Displayed alongside your about text. Recommended: 1200×800 px."`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed import sort order in alembic migration**
- **Found during:** Pre-commit hook (blocked commit)
- **Issue:** `20260307_0600_add_pages_slug_unique.py` had `from alembic import op` before `from sqlalchemy import text` without a separating blank line; ruff I001 treated alembic as first-party
- **Fix:** Applied `ruff check --fix`; ruff's correct format puts `from sqlalchemy import text` (third-party) first, then blank line, then `from alembic import op` (first-party)
- **Files modified:** `backend/alembic/versions/20260307_0600_add_pages_slug_unique.py`
- **Commit:** 99887a2

## Success Criteria Check

- [x] All 8 section editors render without TypeScript errors — typecheck passes clean
- [x] TestimonialsEditor renders avatar_url ImagePicker per item — already wired
- [x] ImagePicker supports both library and URL-paste modes — implemented
- [x] Dimension hints visible on HeroEditor (logo) and AboutEditor (image) — updated
- [x] `./cli.sh typecheck:frontend` passes clean — verified

## Self-Check: PASSED

Files verified present:
- `frontend/src/components/admin/ImagePicker.tsx` — contains "Paste URL", "urlInput", "urlError" (12 matches)
- `frontend/src/components/admin/section-editors/HeroEditor.tsx` — contains "400×200 px"
- `frontend/src/components/admin/section-editors/AboutEditor.tsx` — contains "1200×800 px"

Commits present:
- `99887a2` — contains ImagePicker.tsx changes (77 line additions)
- `606e419` — feat(frontend): ImagePicker URL paste mode + testimonials avatar picker [14-01]
