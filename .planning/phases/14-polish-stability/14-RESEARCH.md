# Phase 14: Polish & Stability - Research

**Researched:** 2026-03-07
**Domain:** Frontend UX polish, mobile responsiveness, DB integrity, error monitoring, MCP tool quality, admin operator tooling
**Confidence:** HIGH (all findings based on direct codebase inspection)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PLSH-01 | Section editors render correctly for all 8 section types without visual glitches | Editors scanned — HeroEditor and AboutEditor have ImagePicker with dimension hints; TestimonialsEditor missing avatar_url picker |
| PLSH-02 | Image field UX — clear upload/paste/URL flow with dimension hints visible | ImagePicker exists but opens MediaLibrary (no URL paste flow); hints are present but not on all image fields |
| PLSH-03 | Admin editor is usable on mobile (hamburger, scrollable editors) | Site editor page has no hamburger menu; header buttons overflow on mobile; Tabs use `max-w-lg` which may clip |
| PLSH-04 | Slug uniqueness enforced at DB level (unique constraint, no race condition) | Sites slug has UNIQUE; pages slug has NO unique constraint — missing DB-level enforcement |
| PLSH-05 | Structured error logging with Sentry integration in production | sentry-sdk NOT in pyproject.toml; main.py has no Sentry init; config.py has no sentry_dsn field |
| PLSH-06 | MCP tool descriptions and response copy enriched with richer examples and field hints | Tools exist and have decent descriptions, but some are terse (update_page, delete_page) |
| OPS-01 | `get_platform_stats` tool (admin-only): total users, sites, pages, plans breakdown | Backend has GET /api/admin/stats endpoint with PlatformStats — missing plans breakdown; no MCP tool exists |
| OPS-02 | `list_all_sites` tool (admin-only): cross-user site list with last activity and plan | Backend has GET /api/admin/users (with site_count) but no cross-user sites list endpoint; no MCP tool exists |
| OPS-03 | `trigger_deployment` tool (admin-only): fires Coolify deploy via API | Coolify API token available in infra .env; Coolify API is at hosting.docmet.com; no MCP tool exists |
</phase_requirements>

---

## Summary

Phase 14 is a targeted polish and tooling phase. Findings from direct code inspection reveal that most work is mechanical but concrete: 5 distinct categories of gaps, each with a clear fix path.

The most critical gap is **PLSH-04**: the `pages` table has no unique constraint on `slug` per site. This means concurrent page creation (especially via MCP) can produce duplicate slugs within a site, resulting in routing collisions on the public site. The `sites.slug` column correctly has `unique=True` globally. The fix requires a new Alembic migration adding a composite unique constraint `(site_id, slug)` on the `pages` table.

The second critical gap is **PLSH-05**: sentry-sdk is absent from `backend/pyproject.toml`, and `main.py` has no Sentry initialization. Adding Sentry is a 3-step task: add dependency, add `sentry_dsn` to config.py, call `sentry_sdk.init()` before the FastAPI app is created.

For OPS-01/02/03, the backend already has the admin REST endpoints needed (GET /api/admin/stats, GET /api/admin/users). The MCP server needs three new admin tools that hit these endpoints using an admin user's Bearer token. The Coolify deployment trigger uses the standard Coolify REST API: `POST https://hosting.docmet.com/api/v1/deploy?uuid={app_uuid}` with `Authorization: Bearer {COOLIFY_API_TOKEN}`.

**Primary recommendation:** Address PLSH-04 (slug constraint) and PLSH-05 (Sentry) first — these are correctness/production-safety issues. Then add OPS tools (admin MCP tooling), then UI polish (PLSH-01/02/03/06).

---

## Standard Stack

### Core (already in project — no new deps except Sentry)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sentry-sdk[fastapi] | ^2.x | Backend error monitoring | FastAPI integration, automatic exception capture, <30s reporting |
| fastapi | >=0.115 | Already in use | No change |
| sqlalchemy[asyncio] | >=2.0 | Already in use — migration needed | Composite unique constraint via `UniqueConstraint` |
| alembic | >=1.14 | Migration tooling | New migration for pages slug constraint |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | >=0.28 | HTTP client for Coolify API trigger | Already in backend; use in MCP server for OPS-03 |

**Installation (new dep only):**
```bash
# In backend/
uv add sentry-sdk[fastapi]
```

---

## Architecture Patterns

### PLSH-01 / PLSH-02: Section Editor UX Audit

**Findings from scanning all 8 editors:**

| Editor | Image Fields | Dimension Hint | URL Paste Flow |
|--------|-------------|---------------|---------------|
| HeroEditor | background_image, logo_url | YES (background_image has hint, logo_url missing hint) | No — MediaLibrary only |
| FeaturesEditor | None | N/A | N/A |
| TestimonialsEditor | avatar_url (defined in SECTION_DEFAULTS) | MISSING — no ImagePicker rendered | No |
| AboutEditor | image_url | YES (generic hint, no dimensions) | No — MediaLibrary only |
| ContactEditor | None | N/A | N/A |
| CtaEditor | None | N/A | N/A |
| PricingEditor | None | N/A | N/A |
| CustomEditor | None | N/A | N/A |

**Gap 1 — TestimonialsEditor missing avatar picker:** The MCP SECTION_DEFAULTS defines `avatar_url` per testimonial, but TestimonialsEditor has no ImagePicker. Testimonial items render headshots if present; editor cannot set them.

**Gap 2 — ImagePicker has no URL paste flow:** Current ImagePicker opens MediaLibrary (file upload dialog) only. No way to type/paste an external URL directly. The component needs a "Paste URL" tab or input alongside the media library button.

**Gap 3 — Missing dimension hints:** logo_url in HeroEditor and image_url in AboutEditor lack specific dimension guidance. The MCP SECTION_DEFAULTS comments have the right values (logo_url: 400×200, about: 1200×800) — these should surface in the UI.

**Fix pattern for ImagePicker (PLSH-02):**
```tsx
// Two-mode ImagePicker: library button OR URL input
// Mode A: Click "Choose from library" → opens MediaLibrary
// Mode B: "Paste URL" input field — direct string entry, clears on blur if invalid URL
// Dimension hint shown below regardless of mode
```

### PLSH-03: Mobile Admin Editor

**Current state:** The site editor page (`frontend/src/app/dashboard/sites/[site_id]/page.tsx`) renders as:
- A fixed header row with 5 buttons (Analytics, Share Draft, Preview Draft, Publish) that will overflow/wrap on narrow viewports
- `TabsList` with `className="grid w-full max-w-lg grid-cols-4"` — the `max-w-lg` (512px) may clip on small phones
- Section cards are full-width — they scroll vertically but section editors have `grid grid-cols-2` layouts that will be too narrow on mobile
- No hamburger menu; no mobile nav sheet

**Fix pattern:**
```tsx
// 1. Header: stack buttons vertically on mobile using flex-wrap or responsive hidden classes
// 2. TabsList: remove max-w-lg on mobile (sm:max-w-lg)
// 3. Section editors: replace grid-cols-2 with grid-cols-1 sm:grid-cols-2 where needed
// 4. FeaturesEditor item grid: "flex gap-2" is okay; confirm on 375px
// 5. No hamburger needed — the dashboard layout likely has its own nav; the site editor
//    page itself just needs responsive button layout
```

**Editors with grid-cols-2 (will overflow on phone):**
- FeaturesEditor: main section uses `grid-cols-2 gap-4` for headline/subheadline
- ContactEditor: `grid grid-cols-2 gap-4` for email/phone
- PricingEditor: `grid-cols-3 gap-2` for plan name/price/period (will be very cramped)
- HeroEditor: `grid grid-cols-2 gap-4` for CTA buttons

### PLSH-04: Slug Uniqueness DB Constraint

**Current state:**
- `sites.slug`: `Column(String(255), unique=True, nullable=False)` — globally unique. CORRECT.
- `pages.slug`: `Column(String(255), nullable=False)` — NO unique constraint. The public router resolves `/{site_slug}/{page_slug}`, so duplicate page slugs within a site produce routing ambiguity.
- Initial migration confirms: `pages` table created with no unique index on `slug`.

**Required fix — new Alembic migration:**
```python
# Migration: add unique constraint (site_id, slug) on pages
def upgrade() -> None:
    op.create_unique_constraint(
        "uq_pages_site_id_slug",
        "pages",
        ["site_id", "slug"],
    )

def downgrade() -> None:
    op.drop_constraint("uq_pages_site_id_slug", "pages", type_="unique")
```

**Application-level guard (sites API):** The site creation endpoint already handles `IntegrityError` for slug conflicts on sites. The same pattern should be applied to page creation in `backend/src/api/pages.py` — catch `IntegrityError` and return HTTP 409 with a user-friendly message.

**Race condition note:** PostgreSQL enforces the constraint at commit time; concurrent INSERTs with the same `(site_id, slug)` pair will result in one succeeding and the other receiving an IntegrityError. This is the correct behavior.

### PLSH-05: Sentry Integration

**Current state:** No Sentry in the project. `main.py` has only stdlib `logging`. `config.py` has no `sentry_dsn`.

**Standard FastAPI Sentry integration pattern:**
```python
# backend/src/config.py — add field
sentry_dsn: str = ""  # Empty string = disabled

# backend/src/main.py — add before app = FastAPI(...)
import sentry_sdk

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,   # 10% of transactions
        profiles_sample_rate=0.1,
    )
```

The `sentry-sdk[fastapi]` extra installs the FastAPI integration automatically — exceptions are captured without manual try/except wrappers. The `[fastapi]` extra also captures request context (route, user agent, etc.).

**Production requirement:** Set `SENTRY_DSN=https://...@sentry.io/...` in production `.env`. The DSN is obtained from the Sentry project settings. Create a Sentry project at sentry.io (free tier sufficient for this phase).

**30-second reporting:** Sentry's default behavior captures and sends events synchronously at the point of exception handling — typically < 1 second, well within 30 seconds.

### PLSH-06: MCP Tool Description Enrichment

**Current state assessment:**

Tools with GOOD descriptions (specific, behavioral guidance):
- `list_sites`, `create_site`, `describe_site`, `apply_theme`, `create_page`, `update_section`

Tools with SPARSE descriptions (missing guidance):
- `update_page`: "Update page title, slug, or publish status." — no behavioral guidance
- `delete_page`: similar
- `delete_site`: decent warning but brief
- `list_versions`, `revert_to_version`: functional but no workflow context

**Enrichment pattern:**
```python
Tool(
    name="update_page",
    description=(
        "Update a page's title, URL slug, or published status. "
        "Confirm slug changes with the user first — changing a slug changes the public URL "
        "and may break links. To publish a page, prefer publish_page which also captures a version snapshot. "
        "Use is_published: false to unpublish (take offline without deleting)."
    ),
    ...
)
```

**Field hint pattern (inputSchema):**
```python
"slug": {
    "type": "string",
    "description": "URL slug — lowercase, hyphens only, e.g. 'about-us'. Changing this changes the public URL."
}
```

### OPS-01/02/03: Admin MCP Tools

**Existing backend endpoints (ready to call):**

| Tool | Backend Endpoint | Notes |
|------|-----------------|-------|
| OPS-01 get_platform_stats | GET /api/admin/stats | Returns total_users, total_sites, total_pages, total_sections. Missing plan breakdown — needs backend enhancement or second call to /api/admin/users |
| OPS-02 list_all_sites | GET /api/admin/users | Returns users with site_count, plan, email. No per-site list. Need new endpoint GET /api/admin/sites |
| OPS-03 trigger_deployment | Coolify API: POST https://hosting.docmet.com/api/v1/deploy?uuid={uuid} | Token from COOLIFY_API_TOKEN env var |

**Admin check mechanism in MCP server:** The MCP server authenticates via Bearer token (the user's MCP API token). The backend already validates the token and resolves the user. The admin-only tools should call `/api/admin/*` endpoints — if the MCP user is not an admin, the backend will return HTTP 403, which the MCP tool should surface as a clear error message.

**No new auth mechanism needed.** Admin tools just call admin API routes; the backend enforces `is_admin=True` via `require_admin` dependency.

**Pattern for admin tools in MCP server:**
```python
elif tool_name == "get_platform_stats":
    try:
        stats = await self._make_request("GET", "/admin/stats")
        users = await self._make_request("GET", "/admin/users")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            return self._text("This tool requires admin access. Connect with an admin account's MCP token.")
        raise
    # ... format and return
```

**OPS-02 backend gap:** There is no `GET /api/admin/sites` endpoint. The existing `GET /api/admin/users` gives user-level data. Need a new backend endpoint that returns all non-deleted sites with `user_email`, `user_plan`, `created_at`, `updated_at` (last activity). This is ~30 lines of FastAPI code.

**OPS-03 Coolify API details (HIGH confidence from infra inspection):**
- API token: `COOLIFY_API_TOKEN` in docmet_infra .env (currently `3|IbPYHzMXAQ2hkO6c1Ke...`)
- Base URL: `https://hosting.docmet.com` (Coolify runs on port 8000 behind nginx at this domain)
- Deploy endpoint: `POST /api/v1/deploy` with query param `uuid={application_uuid}`
- Auth header: `Authorization: Bearer {token}`
- The application UUID must be stored in config (env var `COOLIFY_APP_UUID`) — it is not in the current backend config.py

**Coolify deploy API pattern:**
```python
# config.py additions
coolify_api_url: str = ""        # e.g. https://hosting.docmet.com
coolify_api_token: str = ""
coolify_app_uuid: str = ""       # the MyStorey app UUID from Coolify dashboard

# MCP tool implementation
async with httpx.AsyncClient() as client:
    r = await client.post(
        f"{settings.coolify_api_url}/api/v1/deploy",
        params={"uuid": settings.coolify_app_uuid},
        headers={"Authorization": f"Bearer {settings.coolify_api_token}"},
        timeout=30.0,
    )
    r.raise_for_status()
```

**Finding the app UUID:** The operator must get it from the Coolify dashboard URL for the MyStorey app (visible in the URL when viewing the app in Coolify UI, e.g. `/project/.../application/{uuid}`).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exception monitoring | Custom logging webhook | sentry-sdk[fastapi] | Covers tracebacks, context, breadcrumbs, deduplication automatically |
| Slug collision detection | Application-level SELECT-then-INSERT | PostgreSQL UNIQUE constraint | DB constraint is atomic; SELECT-then-INSERT has TOCTOU race condition |
| Coolify deploy trigger | SSH into server, run docker commands | Coolify REST API | Coolify API is stable, authenticated, returns status |

---

## Common Pitfalls

### Pitfall 1: Soft-delete breaks unique constraint on pages slug
**What goes wrong:** If a page is soft-deleted (`is_deleted=True`) and a new page is created with the same slug, the UNIQUE constraint will fire even though the old page is "deleted".
**Why it happens:** PostgreSQL UNIQUE constraints don't understand soft-delete semantics.
**How to avoid:** Use a partial unique index instead of a plain unique constraint:
```sql
CREATE UNIQUE INDEX uq_pages_site_id_slug_active
ON pages (site_id, slug)
WHERE is_deleted = false;
```
In Alembic, use `op.create_index(..., unique=True, postgresql_where=text("is_deleted = false"))`.
**Warning signs:** Page deletion followed by recreation of same slug fails with 500 instead of succeeding.

### Pitfall 2: Sentry init timing
**What goes wrong:** Calling `sentry_sdk.init()` after `app = FastAPI(...)` may miss some startup errors.
**How to avoid:** Place `sentry_sdk.init()` before `app = FastAPI(...)` in main.py. The `lifespan` function doesn't affect this — init at module load time.

### Pitfall 3: OPS-03 app UUID hardcoded vs. wrong
**What goes wrong:** The Coolify app UUID changes if the app is deleted and recreated in Coolify. A hardcoded UUID will silently trigger deploys on the wrong app or return 404.
**How to avoid:** Store `COOLIFY_APP_UUID` in the production `.env`. Document retrieval steps. Return the Coolify API response body in the MCP tool output so the operator can see deployment status.

### Pitfall 4: ImagePicker URL paste — not validating URL format
**What goes wrong:** User pastes an invalid string (typo, relative path) and it gets saved, producing a broken image.
**How to avoid:** Validate with `new URL(value)` in JS — catch errors and show inline validation feedback. Only call `onChange` with validated URLs.

### Pitfall 5: Mobile `grid-cols-2` overflow on 375px
**What goes wrong:** Tailwind `grid-cols-2` on a 375px screen gives each column ~170px — inputs render but are very cramped. On 320px (older iPhones) it breaks.
**How to avoid:** Use `grid-cols-1 sm:grid-cols-2` for all multi-column editor grids. Test at 375px viewport width.

---

## Code Examples

### Sentry FastAPI Integration
```python
# Source: https://docs.sentry.io/platforms/python/integrations/fastapi/
import sentry_sdk

# In main.py, before app = FastAPI()
settings = get_settings()
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
    )
```

### Partial Unique Index Migration (Alembic)
```python
from sqlalchemy import text
from alembic import op

def upgrade() -> None:
    op.create_index(
        "uq_pages_site_slug_active",
        "pages",
        ["site_id", "slug"],
        unique=True,
        postgresql_where=text("is_deleted = false"),
    )

def downgrade() -> None:
    op.drop_index("uq_pages_site_slug_active", table_name="pages")
```

### Admin MCP Tool Pattern
```python
# In mcp_server/src/aicms_mcp_server/server.py _dispatch():
elif tool_name == "get_platform_stats":
    try:
        stats = await self._make_request("GET", "/admin/stats")
        users = await self._make_request("GET", "/admin/users")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            return self._text(
                "This tool requires admin access. "
                "Connect with an admin account's MCP token."
            )
        raise
    plan_counts: Dict[str, int] = {}
    for u in users:
        plan = u.get("plan", "free")
        plan_counts[plan] = plan_counts.get(plan, 0) + 1
    plan_lines = "\n".join(f"  - {k}: {v}" for k, v in sorted(plan_counts.items()))
    return self._text(
        f"**Platform Stats**\n"
        f"- Users: {stats['total_users']}\n"
        f"- Sites: {stats['total_sites']}\n"
        f"- Pages: {stats['total_pages']}\n"
        f"- Sections: {stats['total_sections']}\n\n"
        f"**By Plan:**\n{plan_lines}"
    )
```

### Backend Admin Endpoint for OPS-02 (new)
```python
# In backend/src/api/admin.py — new endpoint needed
@router.get("/sites", response_model=list[AdminSiteRow])
async def list_all_sites(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AdminSiteRow]:
    rows = await db.execute(
        select(Site, User.email, User.plan)
        .join(User, Site.user_id == User.id)
        .where(Site.is_deleted.is_(False))
        .order_by(Site.updated_at.desc())
    )
    return [
        AdminSiteRow(
            id=site.id, name=site.name, slug=site.slug,
            user_email=email, user_plan=plan,
            created_at=site.created_at, updated_at=site.updated_at,
        )
        for site, email, plan in rows.all()
    ]
```

### Coolify Deploy Trigger
```python
# In MCP server OPS-03 dispatch:
elif tool_name == "trigger_deployment":
    coolify_url = os.environ.get("COOLIFY_API_URL", "")
    coolify_token = os.environ.get("COOLIFY_API_TOKEN", "")
    coolify_uuid = os.environ.get("COOLIFY_APP_UUID", "")
    if not (coolify_url and coolify_token and coolify_uuid):
        return self._text(
            "Deployment not configured — set COOLIFY_API_URL, "
            "COOLIFY_API_TOKEN, and COOLIFY_APP_UUID on the MCP server."
        )
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{coolify_url}/api/v1/deploy",
            params={"uuid": coolify_uuid},
            headers={"Authorization": f"Bearer {coolify_token}"},
        )
        r.raise_for_status()
    data = r.json()
    return self._text(
        f"Deployment triggered.\n"
        f"- UUID: `{coolify_uuid}`\n"
        f"- Status: {data.get('message', 'queued')}\n\n"
        f"Check Coolify dashboard for live deployment logs."
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual Sentry exception calls | `sentry_sdk[fastapi]` auto-instrumentation | sentry-sdk v1.x | Zero-code exception capture |
| Global slug unique (sites) | Composite partial unique (pages) | Phase 14 (this phase) | Closes race condition |
| MCP tools with terse descriptions | Rich behavioral guidance + field examples | Phase 14 | Dramatically improves AI client behavior |

**Deprecated/outdated:**
- `sentry_sdk.init(integrations=[FastApiIntegration()])`: The `[fastapi]` pip extra handles this automatically in sdk >=1.0.

---

## Open Questions

1. **Coolify App UUID**
   - What we know: Token is available, API URL is `https://hosting.docmet.com`
   - What's unclear: The specific UUID of the MyStorey application in Coolify — must be looked up in Coolify dashboard
   - Recommendation: Plan task includes "retrieve UUID from Coolify UI and add to production .env"

2. **Sentry DSN — project to create or existing?**
   - What we know: No Sentry project exists yet for this codebase
   - What's unclear: Whether the operator wants error+performance or errors-only
   - Recommendation: Create a new Sentry project (free tier), errors-only at first (`traces_sample_rate=0`)

3. **Page slug uniqueness — existing duplicate data?**
   - What we know: The constraint is missing
   - What's unclear: Whether any existing pages have duplicate slugs per site (would block migration)
   - Recommendation: The migration plan should include a pre-migration data check query: `SELECT site_id, slug, COUNT(*) FROM pages WHERE is_deleted=false GROUP BY site_id, slug HAVING COUNT(*) > 1`

---

## Validation Architecture

nyquist_validation is enabled (workflow.nyquist_validation: true in config.json).

### Test Framework
| Property | Value |
|----------|-------|
| Framework (frontend) | Vitest (already configured — `vitest run`) |
| Framework (backend) | pytest + pytest-asyncio (deps present, no tests dir yet) |
| Config file (frontend) | vitest.config.ts or inlined in vite.config.ts (check exists) |
| Quick run command (frontend) | `./cli.sh test:frontend` |
| Full suite command | `./cli.sh test` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PLSH-01 | Section editors render for all 8 types without error | Visual / manual | Manual browser test at 1280px | N/A |
| PLSH-02 | ImagePicker shows URL paste tab, dimension hints visible | Visual / manual | Manual browser test with Chrome devtools | N/A |
| PLSH-03 | Site editor usable at 375px — no overflow, editors scroll | Visual / manual | Manual Chrome mobile emulation (375×812) | N/A |
| PLSH-04 | Duplicate page slug within a site is rejected at DB level | Integration | `pytest backend/tests/test_slug_uniqueness.py -x` | ❌ Wave 0 |
| PLSH-05 | Sentry captures an exception and it appears in dashboard | Manual smoke | Deploy to staging, trigger 500, verify in Sentry | N/A |
| PLSH-06 | MCP tools listed in Claude.ai show enriched descriptions | Manual smoke | Connect Claude.ai to MCP, run `/mcp tools list` equivalent | N/A |
| OPS-01 | get_platform_stats returns correct counts including plan breakdown | Unit | `pytest backend/tests/test_admin_ops.py::test_platform_stats -x` | ❌ Wave 0 |
| OPS-02 | list_all_sites returns cross-user site list via MCP | Integration | `pytest backend/tests/test_admin_ops.py::test_list_all_sites -x` | ❌ Wave 0 |
| OPS-03 | trigger_deployment calls Coolify API and returns status | Unit (mocked) | `pytest backend/tests/test_admin_ops.py::test_trigger_deployment -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `./cli.sh test:frontend` (Vitest, <5s)
- **Per wave merge:** `./cli.sh test` (frontend + backend)
- **Phase gate:** Full suite green + manual mobile browser check before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/` — directory does not exist, needs creation
- [ ] `backend/tests/conftest.py` — async SQLAlchemy test session fixture
- [ ] `backend/tests/test_slug_uniqueness.py` — covers PLSH-04
- [ ] `backend/tests/test_admin_ops.py` — covers OPS-01, OPS-02, OPS-03
- [ ] `backend/pytest.ini` or `[tool.pytest.ini_options]` in pyproject.toml — asyncio_mode = "auto"

---

## Sources

### Primary (HIGH confidence — direct code inspection)
- `/Users/docmet/dev/experiment/mcp_cms/backend/src/models/site.py` — slug unique=True confirmed
- `/Users/docmet/dev/experiment/mcp_cms/backend/src/models/page.py` — slug NO unique constraint confirmed
- `/Users/docmet/dev/experiment/mcp_cms/backend/alembic/versions/20260305_1300_initial_schema.py` — migration confirms pages.slug has no unique index
- `/Users/docmet/dev/experiment/mcp_cms/backend/src/config.py` — no sentry_dsn field
- `/Users/docmet/dev/experiment/mcp_cms/backend/src/main.py` — no Sentry import/init
- `/Users/docmet/dev/experiment/mcp_cms/backend/pyproject.toml` — sentry-sdk absent from dependencies
- `/Users/docmet/dev/experiment/mcp_cms/backend/src/api/admin.py` — existing admin endpoints inventoried
- `/Users/docmet/dev/experiment/mcp_cms/mcp_server/src/aicms_mcp_server/server.py` — all 17 tools inventoried, no admin tools
- `/Users/docmet/dev/experiment/mcp_cms/frontend/src/components/admin/section-editors/` — all 8 editors inspected
- `/Users/docmet/dev/experiment/mcp_cms/frontend/src/components/admin/ImagePicker.tsx` — no URL paste flow
- `/Users/docmet/dev/docmet/docmet_infra/.env` — COOLIFY_API_TOKEN and domain confirmed

### Secondary (MEDIUM confidence)
- Sentry FastAPI integration: https://docs.sentry.io/platforms/python/integrations/fastapi/ — pattern verified against Sentry docs structure (standard integration, unchanged for years)
- Coolify API: `POST /api/v1/deploy?uuid={uuid}` — inferred from infra scripts and Coolify API conventions; operator must verify UUID lookup path

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all deps inspected directly
- Architecture: HIGH — all patterns based on actual code, not assumptions
- Pitfalls: HIGH — pitfall 1 (partial index) is a well-known SQLAlchemy/Postgres pattern
- OPS-03 Coolify endpoint: MEDIUM — API path inferred from infra scripts; UUID lookup is manual operator step

**Research date:** 2026-03-07
**Valid until:** 2026-06-07 (stable stack — libraries unlikely to change significantly)
