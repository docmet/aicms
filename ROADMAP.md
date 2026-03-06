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

## Phase 9: Media & Files

> **Foundational — unblocks layouts, blog, logos, and documents.**

- File upload API with pluggable storage: local volume (dev) + Cloudflare R2 (prod)
- Image uploads per site: logo, hero background, section images, favicon
- File attachments: PDFs, downloadable documents
- Media library per site (grid view, reuse assets across sections)
- nginx serves local uploads at `/uploads/`; R2 public URL in prod
- Image fields added to content schemas: hero bg, logo, about image, feature/testimonial images
- MCP tools: `list_media`, `import_image_from_url`, `delete_media`
- Plan limits: Free (50MB / 20 files), Pro (500MB), Agency (5GB)

---

## Phase 10: Design System Expansion

> **Makes the builder feel like a real product. Section variants + more themes.**

- Section layout variants:
  - Hero: centered / image-left / image-right / fullscreen video
  - Features: 2/3/4-col grid, icon list, alternating rows
  - Testimonials: cards / carousel / masonry
  - About: image-left / image-right / stats-only
- Per-section background: white / gray / brand / image overlay
- 5 new themes (10–12 total) with distinct layout personalities, not just color swaps
- Font pairing selector: 5 curated heading+body combinations
- Color accent customizer per site (primary / accent override)
- Spacing/density control: compact / normal / spacious
- MCP tool: `set_section_layout`

---

## Phase 11: Blog, Forms & Rich Content

> **Content marketing + lead capture for every site on the platform.**

- Blog post system: title, slug, excerpt, body (rich text JSON), author, tags, cover image, published_at
- Blog index section + individual post pages at `/[site_slug]/blog/[slug]`
- RSS feed at `/[site_slug]/feed.xml`
- Contact form: real submissions with email notifications to site owner
- Form submission inbox in admin dashboard (read/unread, delete)
- Rich text body section (headings, lists, links, inline images)
- Custom HTML/embed section (advanced users)
- MCP tools: `create_post`, `list_posts`, `update_post`, `publish_post`, `delete_post`

---

## Phase 12: Static Site Generation & Hosting

> **Architecture shift: published sites become static HTML served from CDN.**

- On every publish: generate full static HTML snapshot (sections + theme + SEO)
- Serve static output from Cloudflare R2/Pages — zero Next.js per user visit
- Admin dashboard remains server-rendered (only public sites go static)
- Custom domain support: CNAME → static site (SSL via Cloudflare proxy)
- Groundwork for user site stacks on Coolify (containerized per-user, needed for contact forms / members / ecommerce backends per site)
- Site-level publish ("publish all pages at once")

---

## Phase 13: Growth & Analytics

- Self-hosted site analytics: pageviews, referrers, top pages (privacy-first, no cookies)
- AI-powered SEO suggestions per section
- Shareable preview URLs (token-protected, 24hr expiry)
- Scheduled publishing (publish at specific datetime)
- Diff view between page versions
- Industry-specific starter templates: Restaurant, Portfolio, Agency/SaaS, Freelancer

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
| Phase 9 — Media & Files | 🔨 In progress |
| Phase 10 — Design System Expansion | Planned |
| Phase 11 — Blog, Forms & Rich Content | Planned |
| Phase 12 — Static Site Generation | Planned |
| Phase 13 — Growth & Analytics | Planned |

---

**Last updated:** 2026-03-07
