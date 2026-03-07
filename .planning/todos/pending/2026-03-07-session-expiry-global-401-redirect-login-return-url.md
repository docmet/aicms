---
created: 2026-03-07T09:22:50.189Z
title: Session expiry global 401 redirect login with return URL
area: auth
files:
  - frontend/src/app/dashboard/sites/[site_id]/page.tsx
  - frontend/src/app/login/page.tsx
---

## Problem

When JWT expires, frontend API calls silently fail and pages show broken/empty state (no sites listed, broken preview). User only gets redirected to login on manual refresh. After login, lands on dashboard root — not the page they were on.

## Solution

1. Global axios/fetch interceptor: on any 401 response, immediately redirect to `/login?from=<current_path>`
2. Login page: read `from` param, redirect there after successful login
3. Or: show an in-place login modal so user stays on same page and session resumes
