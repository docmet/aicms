# Requirements: MyStorey

**Defined:** 2026-03-07
**Core Value:** Any AI assistant a user already has can build, update, and publish their entire website through conversation — with zero new AI subscriptions required on our end.

---

## Validated (Phases 1–13 complete)

All requirements below are shipped and confirmed working.

- ✓ **AUTH-01–04**: Register, login, session persistence, JWT auth
- ✓ **SITE-01–06**: Multi-tenant site CRUD, slug, theme, user isolation
- ✓ **PAGE-01–05**: Page CRUD, ordering, publish, scheduled publish
- ✓ **SECT-01–08**: 8 section types, draft/publish split, version rollback (last 5)
- ✓ **MCP-01–25**: 25 MCP tools via HTTP+SSE with OAuth 2.0
- ✓ **THEME-01–12**: 12 themes, CSS variables, layout variants, background options
- ✓ **MEDIA-01–05**: File upload (local + R2), media library, plan limits
- ✓ **BLOG-01–05**: Blog posts, RSS, tags, cover image, published_at
- ✓ **FORM-01–04**: Contact form submissions, email notification, admin inbox
- ✓ **BILL-01–04**: Stripe Checkout, webhook, Customer Portal, plan enforcement
- ✓ **EMAIL-01–05**: Welcome, plan upgraded, limit reached, published, contact notification
- ✓ **ADMIN-01–04**: User management, impersonation, stats, inline plan management
- ✓ **ANAL-01–04**: Pageview tracking, top pages, referrers, daily chart
- ✓ **SHARE-01–02**: Shareable draft preview link (24h token)
- ✓ **ONBD-01–03**: Onboarding wizard, 6 industry templates, nav bar
- ✓ **SEO-01–03**: Sitemap.xml, robots.txt, OG/JSON-LD meta tags

---

## v1 Requirements (Active milestone — public launch ready)

### Polish & Stability

- [x] **PLSH-01**: Section editors render correctly for all 8 section types without visual glitches
- [x] **PLSH-02**: Image field UX — clear upload/paste/URL flow with dimension hints visible
- [x] **PLSH-03**: Admin editor is usable on mobile (hamburger, scrollable editors)
- [x] **PLSH-04**: Slug uniqueness enforced at DB level (unique constraint, no race condition)
- [x] **PLSH-05**: Structured error logging with Sentry integration in production
- [x] **PLSH-06**: MCP tool descriptions and response copy enriched with richer examples and field hints

### WordPress Plugin

- [x] **WP-01**: PHP plugin installable via zip — settings page shows site URL and Application Password instructions
- [x] **WP-02**: Plugin generates and displays the MyStorey MCP URL for the user to paste into their AI client
- [x] **WP-03**: MCP server authenticates WP sites via Application Password stored in MyStorey
- [ ] **WP-04**: MCP tools available for WP: `wp_list_pages`, `wp_get_page`, `wp_update_page`, `wp_create_page`, `wp_publish_page`
- [ ] **WP-05**: MCP tools available for WP: `wp_list_posts`, `wp_update_post`, `wp_create_post`, `wp_publish_post`
- [ ] **WP-06**: MCP tools available for WP: `wp_get_site_info`, `wp_update_site_settings`
- [x] **WP-07**: `/wordpress` landing page with Matrix pill framing live on mystorey.io
- [x] **WP-08**: Stripe checkout for WP plugin subscription ($7/mo Starter, $24/mo Pro)
- [ ] **WP-09**: WP plugin connection flow tested end-to-end with Claude.ai and ChatGPT

### Operator Admin MCP Tools

- [x] **OPS-01**: `get_platform_stats` tool (admin-only): total users, sites, pages, plans breakdown
- [x] **OPS-02**: `list_all_sites` tool (admin-only): cross-user site list with last activity and plan
- [x] **OPS-03**: `trigger_deployment` tool (admin-only): fires Coolify deploy via API

### Agency / Client Sites

- [ ] **AGCY-01**: Embed section type supports Stripe Payment Links and Gumroad widgets (iframe/script)
- [ ] **AGCY-02**: Internal migration guide: how to move a docmet client site to MyStorey engine
- [ ] **AGCY-03**: 3 real client sites live on MyStorey before public launch announcement

### Pricing & Growth

- [ ] **PRIC-01**: Modular pricing UI: base plan + optional add-on packages (custom domain, extra sites, priority support)
- [ ] **PRIC-02**: Early bird pricing displayed with strikethrough future price and lock-in messaging
- [ ] **PRIC-03**: Affiliate program: referral link in dashboard, 25% recurring commission tracked
- [ ] **PRIC-04**: Affiliate payout via Stripe, minimum $50 threshold

### Public Launch

- [ ] **LAUN-01**: mystorey.io landing page: demo video, Matrix pill framing, testimonials, pricing
- [ ] **LAUN-02**: "Tip of the iceberg" messaging on landing page and pricing — platform velocity communicated
- [ ] **LAUN-03**: Onboarding funnel verified: sign up → create site → connect AI → publish < 10 min
- [ ] **LAUN-04**: AI connection guide page: Claude.ai, ChatGPT, Perplexity setup instructions
- [ ] **LAUN-05**: Product Hunt launch asset: 2-min demo video of AI building a coffee shop site

---

## v2 Requirements (Deferred)

### AI-Backed Features (Agency+ add-on, Phase 16+)

- **AIX-01**: AI content audit: Claude reviews all sections, flags thin content, suggests improvements
- **AIX-02**: AI SEO report: per-page score + specific fix recommendations
- **AIX-03**: Bulk site generation from CSV/spreadsheet upload

### Static Site Generation (Phase 12 completion)

- **SSG-01**: Static HTML snapshot generated on publish (headless render or Python templates)
- **SSG-02**: Static output served from Cloudflare R2/Pages — zero Next.js per user visit
- **SSG-03**: Custom domain routing in nginx with wildcard CNAME + Coolify proxy rules
- **SSG-04**: SSL via Cloudflare proxy for custom domains

### WordPress Plugin Expansion

- **WPX-01**: WooCommerce tools: `wc_list_products`, `wc_update_product`, `wc_get_orders`
- **WPX-02**: WordPress.org plugin directory listing
- **WPX-03**: One-click WP → MyStorey migration tool

### Platform

- **PLAT-01**: Password-protected pages (members-only content)
- **PLAT-02**: eCommerce product page section type (native, not embed)
- **PLAT-03**: Multilingual content with language switcher
- **PLAT-04**: AI translation for multilingual sites
- **PLAT-05**: A/B testing (serve version A/B to visitors)
- **PLAT-06**: 2FA for admin users
- **PLAT-07**: Refresh token mechanism (no abrupt logout)

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Server-side AI API calls for user content generation | Core philosophy: user's AI is the intelligence layer |
| Drag-and-drop page builder | Squarespace competitor framing — wrong positioning |
| Native mobile app | Web-first; mobile is a later milestone |
| Multi-language admin UI | English only for v1 public launch |
| Real-time collaborative editing | Single user per site; complexity not justified yet |
| OAuth login (Google, GitHub) | Email/password sufficient for v1; add later if demand |
| Self-hosted MCP server option | Hosted bridge is the product; self-host removes revenue |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLSH-01 | Phase 14 | Complete |
| PLSH-02 | Phase 14 | Complete |
| PLSH-03 | Phase 14 | Complete |
| PLSH-04 | Phase 14 | Complete |
| PLSH-05 | Phase 14 | Complete |
| PLSH-06 | Phase 14 | Complete |
| OPS-01 | Phase 14 | Complete |
| OPS-02 | Phase 14 | Complete |
| OPS-03 | Phase 14 | Complete |
| WP-01 | Phase 15 | Complete |
| WP-02 | Phase 15 | Complete |
| WP-03 | Phase 15 | Complete |
| WP-04 | Phase 15 | Pending |
| WP-05 | Phase 15 | Pending |
| WP-06 | Phase 15 | Pending |
| WP-07 | Phase 15 | Complete |
| WP-08 | Phase 15 | Complete |
| WP-09 | Phase 15 | Pending |
| AGCY-01 | Phase 16 | Pending |
| AGCY-02 | Phase 16 | Pending |
| AGCY-03 | Phase 16 | Pending |
| PRIC-01 | Phase 17 | Pending |
| PRIC-02 | Phase 17 | Pending |
| PRIC-03 | Phase 17 | Pending |
| PRIC-04 | Phase 17 | Pending |
| LAUN-01 | Phase 17 | Pending |
| LAUN-02 | Phase 17 | Pending |
| LAUN-03 | Phase 17 | Pending |
| LAUN-04 | Phase 17 | Pending |
| LAUN-05 | Phase 17 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-07*
*Last updated: 2026-03-07 — traceability expanded to per-requirement rows, phase 14–17 assignments confirmed*
