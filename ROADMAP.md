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

## Phase 9: Content Expansion

- Image upload + CDN hosting (Cloudflare R2 or S3-compatible)
- Rich text sections (headings, lists, links in body)
- Blog/posts system (date, author, slug, RSS)
- Custom HTML/embed sections (advanced users)
- Custom domain support (CNAME + SSL via Let's Encrypt)

---

## Phase 10: Growth & Analytics

- Site analytics: pageviews, referrers, top pages (self-hosted, privacy-first)
- AI-powered SEO suggestions ("Your about section is missing keywords")
- Shareable preview URLs (token-protected, 24hr expiry)
- Scheduled publishing (publish at specific datetime)
- Industry-specific templates: Restaurant, Portfolio, Agency/SaaS, Services

---

## Backlog

**AI:**
- AI translation for multilingual sites
- AI image generation (DALL-E, Flux)
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
- Contact form builder with email notifications
- eCommerce product pages (links to external cart)
- Multilingual content with language switcher
- Site-level publish ("deploy all pages at once")
- Diff view between page versions

---

## Progress

| Phase | Status |
|-------|--------|
| Foundation | Done |
| Backend | Done |
| Frontend | Done |
| Integration | Done |
| MCP Server | Done |
| Content Architecture + Renderer | Done |
| Growth Features | Done |
| Admin + Billing Foundation | Partial (Stripe pending) |
| Stripe Integration | Next |
| Email Service | Next |
| WordPress Plugin | Parallel track |
| Content Expansion | Planned |
| Growth & Analytics | Planned |

---

**Last updated:** 2026-03-06
