---
phase: 15-wordpress-plugin
plan: "03"
subsystem: ui
tags: [react, nextjs, typescript, stripe, wordpress, shadcn]

# Dependency graph
requires:
  - phase: 15-01
    provides: WordPressSite model, CRUD API at /api/wordpress/sites
  - phase: 15-02
    provides: WP-MCP dispatch endpoint

provides:
  - WordPress dashboard page at /dashboard/wordpress (site list, MCP URL/token copy, delete)
  - RegisterWordPressSite form component with app password helper
  - Typed API client lib/api/wordpress.ts (register, list, delete)
  - WordPress nav link in dashboard sidebar
  - Public landing page at /wordpress with Matrix pill hero, how-it-works, pricing
  - wp_starter + wp_pro billing plans in backend (VALID_PLANS + _price_id)
  - NEXT_PUBLIC_STRIPE_WP_*_PRICE_ID env vars + .env.example documentation

affects: [15-04, billing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Server component page.tsx exporting metadata + separate client WordPressLanding.tsx component
    - "Coming soon" button pattern when NEXT_PUBLIC env var is empty (graceful degradation)
    - Delete confirmation via Dialog state instead of AlertDialog (not in shadcn/ui install)

key-files:
  created:
    - frontend/src/lib/api/wordpress.ts
    - frontend/src/components/wordpress/RegisterWordPressSite.tsx
    - frontend/src/app/dashboard/wordpress/page.tsx
    - frontend/src/app/(public)/wordpress/page.tsx
    - frontend/src/app/(public)/wordpress/WordPressLanding.tsx
  modified:
    - frontend/src/components/admin/sidebar.tsx
    - backend/src/config.py
    - backend/src/api/billing.py
    - backend/src/api/wordpress.py
    - .env.example

key-decisions:
  - "WordPress landing page split into server page.tsx (metadata) + client WordPressLanding.tsx (hooks/interactivity)"
  - "AlertDialog not in shadcn/ui install — used Dialog with open state instead for delete confirmation"
  - "Checkout buttons show 'Coming soon' when NEXT_PUBLIC_STRIPE_WP_*_PRICE_ID is empty string"
  - "wp_starter and wp_pro added to VALID_PLANS; _price_id() raises 503 if env var not configured"

patterns-established:
  - "server-client split pattern: page.tsx exports metadata, imports client component for interactivity"
  - "env-var-gated feature: check NEXT_PUBLIC_ var, show disabled state if empty"

requirements-completed: [WP-01, WP-02, WP-07, WP-08]

# Metrics
duration: 6min
completed: 2026-03-07
---

# Phase 15 Plan 03: WordPress Frontend + Billing Summary

**WordPress dashboard with site registration/MCP token display, public /wordpress landing page with Matrix pill framing, and wp_starter/wp_pro Stripe billing plan support**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-07T16:13:51Z
- **Completed:** 2026-03-07T16:20:00Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Dashboard page `/dashboard/wordpress` renders registration form and site card list with MCP URL + masked MCP token copy fields, delete confirmation dialog, and "Add another site" flow
- WordPress nav link (Globe icon) added to dashboard sidebar between "Connect AI" and "Settings"
- Public landing page `/wordpress` with dark Matrix-style hero (red/blue pill choice), 3-step how-it-works, 4-feature grid, pricing cards with Stripe checkout integration
- Backend billing extended with `wp_starter` and `wp_pro` plans; raises 503 gracefully if Stripe price IDs not configured
- Checkout buttons show "Coming soon" disabled state when `NEXT_PUBLIC_STRIPE_WP_*_PRICE_ID` env vars are absent

## Task Commits

Each task was committed atomically:

1. **Task 1: API client and dashboard WordPress registration page** - `c78d29c` (feat)
2. **Task 2: /wordpress public landing page with Matrix pill framing and Stripe checkout** - `5d15a5a` (feat)

## Files Created/Modified
- `frontend/src/lib/api/wordpress.ts` - Typed API client: registerWordPressSite, listWordPressSites, deleteWordPressSite + WordPressSite interface
- `frontend/src/components/wordpress/RegisterWordPressSite.tsx` - Registration form with app password helper text and error toast
- `frontend/src/app/dashboard/wordpress/page.tsx` - Dashboard WordPress page with site list, copy fields, dialog confirmation, add-another flow
- `frontend/src/app/(public)/wordpress/page.tsx` - Server component with SEO metadata export
- `frontend/src/app/(public)/wordpress/WordPressLanding.tsx` - Client component: full marketing landing page
- `frontend/src/components/admin/sidebar.tsx` - Added WordPress nav item with Globe icon
- `backend/src/config.py` - Added stripe_wp_starter_price_id + stripe_wp_pro_price_id settings
- `backend/src/api/billing.py` - Added wp_starter + wp_pro to VALID_PLANS, extended _price_id() with 503 guard
- `backend/src/api/wordpress.py` - Auto-fixed ruff lint (unsorted imports + unused Header import)
- `.env.example` - Added WP Stripe price ID documentation

## Decisions Made
- Split public landing page into server component (metadata) + client component (hooks) to support both Next.js metadata exports and React hooks
- Used existing `Dialog` component for delete confirmation since `AlertDialog` is not in this project's shadcn/ui install
- Pricing buttons gracefully degrade to "Coming soon" when `NEXT_PUBLIC_STRIPE_WP_*_PRICE_ID` is not set
- Checkout POST sends `success_url` and `cancel_url` as body but plan as query param (matching existing billing API contract)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used Dialog instead of AlertDialog for delete confirmation**
- **Found during:** Task 1 (dashboard page)
- **Issue:** Plan specified AlertDialog but `@/components/ui/alert-dialog` does not exist in this project's shadcn/ui install
- **Fix:** Replaced AlertDialog with Dialog + open state (same UX, different component name)
- **Files modified:** frontend/src/app/dashboard/wordpress/page.tsx
- **Verification:** TypeScript typecheck passes
- **Committed in:** c78d29c (Task 1 commit)

**2. [Rule 1 - Bug] Fixed ruff lint errors in backend/src/api/wordpress.py**
- **Found during:** Task 1 (pre-commit hook ran lint)
- **Issue:** wordpress.py had unsorted imports (I001) and unused `Header` import (F401) — from Phase 15-01 commit
- **Fix:** Ran `ruff check --fix src/api/wordpress.py`
- **Files modified:** backend/src/api/wordpress.py
- **Verification:** Backend lint passes
- **Committed in:** c78d29c (Task 1 commit)

**3. [Rule 2 - Pattern] Split landing page into server + client components**
- **Found during:** Task 2 (public landing page)
- **Issue:** Plan said to export `metadata` from the page, but page needs `useAuth`, `useRouter`, `useState` hooks — incompatible with Server Components
- **Fix:** Created `page.tsx` (server, exports metadata) + `WordPressLanding.tsx` (client, all hooks and interactivity)
- **Files modified:** frontend/src/app/(public)/wordpress/page.tsx, WordPressLanding.tsx
- **Verification:** TypeScript typecheck passes, metadata exported correctly
- **Committed in:** 5d15a5a (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (1 blocking, 1 bug, 1 missing critical pattern)
**Impact on plan:** All auto-fixes necessary for correctness and TypeScript compliance. No scope creep.

## Issues Encountered
- `frontend/src/lib/` is in `.gitignore` (Python `lib/` pattern catches it). Force-added with `git add -f` consistent with other files in that directory already tracked.

## User Setup Required
None required for base functionality. To enable Stripe checkout buttons:
1. Create WP Starter price ($7/mo) and WP Pro price ($24/mo) in Stripe Dashboard
2. Set env vars: `STRIPE_WP_STARTER_PRICE_ID`, `STRIPE_WP_PRO_PRICE_ID`, `NEXT_PUBLIC_STRIPE_WP_STARTER_PRICE_ID`, `NEXT_PUBLIC_STRIPE_WP_PRO_PRICE_ID`
3. Without these, pricing buttons show "Coming soon" — safe default.

## Next Phase Readiness
- Dashboard and landing page complete — users can register WP sites and see MCP credentials
- Billing plan support ready for when Stripe price IDs are created
- 15-04 (WP plugin zip download) can proceed independently

---
*Phase: 15-wordpress-plugin*
*Completed: 2026-03-07*
