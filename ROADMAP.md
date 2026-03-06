# MyStorey Roadmap

Development roadmap: from MVP proof-of-concept to production-ready freemium SaaS.

---

## Completed

### Foundation (Phase 1)
- Project structure, Docker Compose (dev + prod), GitHub Actions CI/CD
- Git hooks (lefthook: format, lint, test on commit)
- SQLAlchemy models + Alembic migrations
- Seed data (admin + client user, themes)
- `cli.sh` development CLI (30+ commands)

### Backend (Phase 2)
- FastAPI + JWT authentication
- User registration/login
- Site, Page, ContentSection CRUD (multi-tenant, user-scoped)
- Theme service (7 themes)
- Integration tests: auth, data isolation, theme switching

### Frontend (Phase 3)
- Next.js 15 App Router
- Login/register pages
- Admin dashboard (shadcn/ui)
- Site editor: name, slug, theme, sections
- Public site renderer (`[site_slug]/page.tsx`)
- TailwindCSS CSS-variable themes

### Integration & Testing (Phase 4)
- Frontend ↔ backend fully connected
- Multi-user isolation tested
- Instant save (auto-save on blur)
- Local Docker stack verified end-to-end

### MCP Server (Phase 5)
- FastAPI HTTP+SSE MCP server
- OAuth 2.0 + token auth per AI client
- 17 tools: sites, pages, content, themes, versions
- Working with Claude.ai, Claude Desktop, ChatGPT (Developer mode), Claude Code

### Content Architecture + Renderer (Phase 6)
- Structured JSON content schemas per section type
- Draft/publish split (`content_draft` vs `content_published`)
- Last 5 versions per page with AI-triggered rollback
- Real-time SSE preview
- 8 section types: Hero, Features, Testimonials, About, Contact, CTA, Pricing, Custom
- 7 themes: modern, warm, startup, minimal, dark + default/nature aliases
- Admin structured editors + live preview pane
- Full SEO: meta tags, OG, JSON-LD

### Growth Features (Phase 7)
- Onboarding wizard: industry picker → starter site → connect AI (6 industry templates)
- Site navigation (multi-page sites with nav bar)
- Mobile-responsive admin (hamburger + slide-down drawer)
- Sitemap.xml + robots.txt per site
- Landing page with pricing, features, testimonials, custom dev block
- AI tool connection guide (Claude.ai, ChatGPT, Perplexity) with brand icons
- Auth UX: expired session redirect, login auto-redirect, register plan redirect
- `NavAuthButtons` — smart nav (logged-in vs logged-out state)

### Admin + Billing Foundation (Phase 8 — partial)
- Admin panel: user management, impersonation, platform stats
- Admin: inline plan management (Free / Pro / Agency) per user
- Plan enforcement: site creation limits per plan
- "Made with MyStorey" badge on free plan public sites
- Billing UI: `/dashboard/billing` upgrade page
- Billing backend: checkout/verify/webhook endpoints (Revolut stub — to be replaced with Stripe)
- Payment + tax research: Stripe preferred, EU VAT OSS, US sales tax documented

---

## Up Next

### Stripe Integration
- Replace Revolut billing stub with Stripe Checkout
- Stripe webhook: handle `checkout.session.completed`, `customer.subscription.deleted`
- Customer portal link (manage/cancel subscription)
- Stripe Tax (automatic EU VAT calculation)
- Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID`, `STRIPE_AGENCY_PRICE_ID`

### Email Service
- Mailpit container for local dev (port 8025, web UI)
- Mail-in-a-Box (docmet.systems) for staging/prod SMTP
- Transactional emails: welcome, plan upgrade confirmation, plan limit reached, publish confirmation
- Backend: `src/services/email.py` using SMTP (aiosmtplib or similar)

### WordPress Plugin (parallel track)
- WP plugin: connects WP sites to MyStorey MCP
- Sync posts/pages → MyStorey content sections
- Paid from day one ($X/mo, managed WP hosting pitch)
- 2-3 day build: plugin scaffold → MCP bridge → payment
- `/wordpress` landing page with Matrix pill angle ("stay in WordPress, add AI superpowers")
- See `.planning/research/wordpress-mcp-plugin-opportunity.md`

---

## Phase 9: Media & Files — COMPLETE

- [x] File upload API with pluggable storage: local volume (dev) + Cloudflare R2 (prod)
- [x] Image uploads per site: logo, hero background, section images, avatar
- [x] Media library per site (grid view in admin, reuse across sections)
- [x] nginx serves local uploads at `/uploads/`
- [x] Image fields: hero `background_image`/`logo_url`, about `image_url`, testimonial `avatar_url`
- [x] MCP tools: `list_media`, `import_image_from_url`, `delete_media` (23 tools total)
- [x] MCP tool descriptions enriched with image dimension recommendations per field
- [x] Plan limits: Free (50MB / 20 files), Pro (500MB), Agency (5GB)

---

## Phase 10: Design System Expansion — COMPLETE

- [x] 5 new themes: ocean (navy+cyan), rose (blush+serif), slate (indigo), forest (deep green), sunset (purple-magenta)
- [x] Font pairing: Space Grotesk for ocean, Playfair Display for rose (via Google Fonts @import)
- [x] Hero layout variants: `centered` / `split` / `fullscreen` — layout field in content JSON
- [x] Features layout variants: `grid-3` (default) / `grid-2` / `grid-4` / `list`
- [x] Features background field: `default` / `white` / `gray` / `brand` / `dark`
- [x] Testimonials layout variants: `cards` (default) / `masonry` / `featured`
- [x] Testimonials background field + avatar image support
- [x] About layout variants: `image-right` (default) / `image-left` / `stats-only`
- [x] MCP tool: `set_section_layout` — patches layout without overwriting content
- [ ] Color accent customizer per site (primary/accent override) — deferred to Phase 12
- [ ] Spacing/density control — deferred

---

## Phase 11: Blog, Forms & Rich Content ✅

> **Content marketing + lead capture for every site on the platform.**

- [x] Blog post system: title, slug, excerpt, body, author, tags, cover image, published_at
- [x] Blog index section + individual post pages at `/[site_slug]/blog/[slug]`
- [x] RSS feed at `/[site_slug]/feed.xml`
- [x] Contact form: real submissions with email notifications to site owner
- [x] Form submission inbox in admin dashboard (read/unread, delete)
- [x] Rich text body section: custom section with `render_mode: "markdown"` — headings, bold, lists, links, inline code
- [x] Custom HTML/embed section: custom section with `render_mode: "html"` — raw HTML/iframes for maps, videos, widgets
- [x] MCP tools: `create_post`, `list_posts`, `update_post`, `publish_post`, `delete_post`

---

## Phase 12: Static Site Generation & Hosting ✅ (partial)

> **Architecture shift: published sites become static HTML served from CDN.**

- [x] Site-level publish: `POST /api/sites/{id}/publish-all` — publishes every page + theme in one call
- [x] "Publish All Pages" button in admin Settings tab
- [x] `publish_site` MCP tool (publishes entire site at once)
- [x] Custom domain field: `domain` in Site model + SiteUpdate schema + Settings UI + MCP `update_site`
- [ ] Static HTML snapshot generation on publish (requires SSR headless render or Python templates)
- [ ] Serve static output from Cloudflare R2/Pages — zero Next.js per user visit
- [ ] Custom domain routing in nginx (wildcard CNAME + Coolify proxy rules)
- [ ] SSL via Cloudflare proxy for custom domains

---

## Phase 13: Growth & Analytics ✅ (partial)

- [x] Self-hosted site analytics: pageviews, referrers, top pages (privacy-first, no cookies)
  - Backend: `POST /api/public/sites/{slug}/pageview` + `GET /api/sites/{id}/analytics`
  - Frontend: Analytics dashboard at `/dashboard/sites/{id}/analytics` with daily chart, top pages, top referrers
  - Tracking call in SiteRenderer (fire-and-forget, no cookies)
- [x] Shareable preview URLs (token-protected, 24h expiry)
  - Backend: `POST /api/sites/{id}/share` → token, `GET /api/share/{token}` → draft content
  - Frontend: `/share/{token}` preview page with expired/error states + draft banner
  - "Share Draft" button in admin header — copies URL to clipboard
- [ ] AI-powered SEO suggestions per section
- [ ] Scheduled publishing (publish at specific datetime)
- [ ] Diff view between page versions
- [ ] Industry-specific starter templates: Restaurant, Portfolio, Agency/SaaS, Freelancer

---

## Backlog

**AI:**
- AI translation for multilingual sites
- AI image generation (DALL-E / Flux via MCP tool)
- Bulk site generation from document/spreadsheet
- A/B testing (serve version A to 50% of visitors)

**Platform:**
- 2FA for admin users
- Multiple admin roles: `super_admin`, `support`, `billing_admin`
- Feature flags per user or globally
- Content moderation queue
- Bulk email to users

**Sites:**
- Password-protected pages (members-only)
- eCommerce product pages (links to external cart)
- Multilingual content with language switcher
- Blog: AI translation, scheduled posts, categories

**WordPress Plugin (parallel track):**
- WP plugin connecting WP sites to MyStorey MCP
- Sync posts/pages → MyStorey content sections
- Paid from day one ($X/mo)
- `/wordpress` landing page

---

## Progress

| Phase | Status |
|-------|--------|
| Foundation | ✅ Done |
| Backend | ✅ Done |
| Frontend | ✅ Done |
| Integration | ✅ Done |
| MCP Server | ✅ Done |
| Content Architecture + Renderer | ✅ Done |
| Growth Features | ✅ Done |
| Admin + Billing (Stripe + Email) | ✅ Done |
| Phase 9 — Media & Files | ✅ Done |
| Phase 10 — Design System Expansion | ✅ Done |
| Phase 11 — Blog, Forms & Rich Content | ✅ Done |
| Phase 12 — Static Site Generation | 🔨 In progress |
| Phase 13 — Growth & Analytics | 🔨 In progress |

---

**Last updated:** 2026-03-07
