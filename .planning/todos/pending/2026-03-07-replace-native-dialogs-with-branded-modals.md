---
created: 2026-03-07T15:00:00.000Z
title: Replace native alert/confirm dialogs with branded modals
area: frontend
files:
  - frontend/src/components/admin/MediaLibrary.tsx
  - frontend/src/app/dashboard/admin/page.tsx
  - frontend/src/app/dashboard/sites/[site_id]/page.tsx
---

## Problem

Native `confirm()` and `alert()` dialogs are used throughout the admin UI (delete user, delete section, delete media, restore version). These are OS-native popups — ugly, not brand-compatible, can't be styled.

## Solution

Create a reusable `<ConfirmDialog>` component using shadcn Dialog:
- Violet primary button, destructive variant for destructive actions
- Title + description props
- `onConfirm` / `onCancel` callbacks
- Replace all `confirm("...")` calls across the codebase

## Locations to replace

- `MediaLibrary.tsx` — `confirm(\`Delete "${file.original_filename}"?\`)`
- `admin/page.tsx` — `confirm(\`Delete user ${userEmail}...\`)`
- `sites/[site_id]/page.tsx` — version restore confirm, section delete confirm, page delete confirm
- Any other `confirm()` / `alert()` calls

## Notes

Low priority — functionality works fine with native dialogs. Do this during a UI polish pass before public launch.
