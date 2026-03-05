# AI CMS Roadmap

Development roadmap: from MVP proof-of-concept to a production-ready freemium SaaS.

---

## Completed Phases

### Phase 1: Foundation
- Project structure, Docker Compose (dev + prod), GitHub Actions CI/CD
- Git hooks (lefthook + pre-commit: format, lint, test)
- SQLAlchemy models and Alembic migrations
- Seed data (admin + client user, 5 themes)
- `cli.sh` development CLI

### Phase 2: Backend
- FastAPI application with JWT authentication
- User registration/login endpoints
- Site, Page, ContentSection CRUD (multi-tenant, scoped to user)
- Theme service
- Integration tests: auth, data isolation, theme switching

### Phase 3: Frontend
- Next.js 15+ with App Router
- Login/register pages
- Admin dashboard with shadcn/ui
- Site editor: name, slug, theme selector, content sections
- Public site rendering (`[site_slug]/page.tsx`)
- TailwindCSS theme variants (5 themes)

### Phase 4: Integration & Testing
- Frontend ↔ backend fully connected
- Multi-user isolation tested
- Instant save (Mac-style auto-save on blur)
- Local Docker stack verified end-to-end

### Phase 5: MCP Server
- FastAPI-based MCP server with HTTP+SSE transport
- 13 MCP tools: site, page, content, theme management
- OAuth 2.0 / token-based authentication per AI client
- Working with: Claude Desktop ✅, Claude mobile app via ngrok ✅

---

## Current Work (Phase 6: Quality + Architecture)

**Goal: Staging deployment live at aicms.docmet.systems by end of day**

- [x] **0a: Documentation overhaul** — all docs updated to reflect vision and new architecture
- [x] **0b: Claude Code skills** — 6 project slash commands in `.claude/commands/`
- [x] **1: Content model** — structured JSON schemas per section type, draft/publish split, versioning, SSE preview
- [x] **2: Framer-level renderer** — section components (Hero, Features, Testimonials, etc.), SEO, animations
- [x] **3: Admin editor** — structured field inputs + live SSE preview pane + publish/rollback UI
- [x] **4: Smarter MCP tools** — describe_site, generate_section, smart_find, publish_page, versioning tools
- [ ] **5: Admin panel** — user management, impersonation, platform stats
- [ ] **6: Staging deploy** — Coolify config, wildcard DNS, security headers, landing page

---

## Phase 7: Growth (Post-Launch)

### Core Experience
- [ ] Onboarding wizard: industry picker → starter site generated → connect AI
- [ ] Industry-specific templates: Restaurant, Portfolio, Agency/SaaS, Services
- [ ] Site navigation (multi-page sites with proper nav bar)
- [ ] Mobile-responsive admin dashboard

### Content
- [ ] Image upload and CDN hosting
- [ ] Rich text sections (headings, lists, links in body)
- [ ] Blog/posts system with date + author
- [ ] Custom HTML/embed sections (for advanced users)

### Distribution
- [ ] Custom domain support (CNAME + SSL via Let's Encrypt)
- [ ] Sitemap.xml per site
- [ ] robots.txt per site
- [ ] Site analytics: pageviews, referrers, top pages

---

## Phase 8: Scale

### Platform
- [ ] Stripe integration: free → pro upgrade flow
- [ ] Email notifications (publish confirmation, limits reached, etc.)
- [ ] Scheduled publishing (publish at specific datetime)
- [ ] A/B testing (serve version A to 50% of visitors)
- [ ] Shareable preview URLs (token-protected, 24hr expiry)

### AI
- [ ] AI-powered SEO suggestions ("Your about section is missing keywords")
- [ ] AI translation for multilingual sites
- [ ] AI image generation integration (DALL-E, etc.)
- [ ] Bulk site generation from a document/spreadsheet

---

## Future Ideas (Backlog)

**Versioning:**
- Diff view between page versions
- Site-level publish ("deploy all pages at once")

**Security:**
- 2FA for admin users
- Penetration testing
- IP allowlist for admin routes
- Security.txt at `/.well-known/security.txt`

**Admin:**
- Multiple admin roles: `super_admin`, `support`, `billing_admin`
- Bulk email to users
- Feature flags per user or globally
- Content moderation queue

**Sites:**
- Password-protected pages (coming soon, members-only)
- Contact form builder with email notifications
- eCommerce product pages (read-only, links to external cart)
- Multilingual content with language switcher

---

## Progress Tracker

| Phase | Status | Notes |
|-------|--------|-------|
| Foundation | ✅ Done | |
| Backend | ✅ Done | |
| Frontend | ✅ Done | Basic implementation |
| Integration | ✅ Done | |
| MCP Server | ✅ Done | Proven on desktop + mobile |
| Quality + Architecture | 🔄 In Progress | Today's work |
| Growth | ⏳ Planned | Post-launch |
| Scale | ⏳ Planned | Post-growth |

---

**Last updated:** 2026-03-05
