# MyStorey

## What This Is

MyStorey is an AI-first website platform where users build and manage their sites by chatting with AI assistants (Claude, ChatGPT, Perplexity) via the MCP protocol. It serves three modes: a public SaaS product (mystorey.io), an internal agency engine for running docmet.com client sites, and a WordPress plugin that bridges AI tools to existing WordPress installs. All three share the same backend engine, MCP server, and Stripe billing infrastructure.

## Core Value

Any AI assistant a user already has can build, update, and publish their entire website through conversation — with zero new AI subscriptions required on our end.

## Requirements

### Validated

<!-- Phases 1–13 shipped and confirmed. -->

- ✓ JWT authentication (register, login, session) — Phase 2
- ✓ Multi-tenant site/page/section CRUD with user isolation — Phase 2
- ✓ MCP server with OAuth 2.0, HTTP+SSE, token auth — Phase 5
- ✓ 25 MCP tools: sites, pages, content, themes, versions, media, blog, publish — Phases 5–12
- ✓ Draft/publish split (content_draft vs content_published) with version rollback — Phase 6
- ✓ Real-time SSE live preview — Phase 6
- ✓ 12 themes with CSS variable system — Phases 6 + 10
- ✓ 8 section types (hero, features, testimonials, about, contact, cta, pricing, custom) — Phase 6
- ✓ Section layout variants and background options — Phase 10
- ✓ File upload: local dev volume + Cloudflare R2 production — Phase 9
- ✓ Media library per site with plan limits — Phase 9
- ✓ Blog post system with RSS feed — Phase 11
- ✓ Contact form submissions with email notifications + admin inbox — Phase 11
- ✓ Rich text (markdown) and HTML embed custom sections — Phase 11
- ✓ Plan tiers: Free / Pro / Agency with Stripe Checkout + Customer Portal — Phase 8
- ✓ Transactional emails via aiosmtplib (welcome, plan upgrade, limit reached, published) — Phase 8
- ✓ Admin panel: user management, impersonation, platform stats — Phase 8
- ✓ Privacy-first analytics: pageviews, top pages, referrers, daily chart — Phase 13
- ✓ Shareable draft preview links (24h token, public URL) — Phase 13
- ✓ Scheduled publishing (scheduled_at + background scheduler) — Phase 13
- ✓ Site-level publish-all endpoint + MCP tool — Phase 12
- ✓ Custom domain field + Settings UI + MCP tool — Phase 12
- ✓ Onboarding wizard with 6 industry templates — Phase 7
- ✓ Multi-page sites with nav bar — Phase 7
- ✓ Mobile-responsive admin — Phase 7
- ✓ Sitemap.xml + robots.txt per site — Phase 7
- ✓ "Made with MyStorey" badge for free plan — Phase 8

### Active

<!-- Current milestone: polish, WP plugin, agency track, public launch -->

- [ ] UI/UX polish: section editor quality, image field UX, admin mobile editor
- [ ] MCP tool descriptions and response copy enrichment (this IS the product for AI clients)
- [ ] WordPress plugin: PHP install + MCP bridge tools + /wordpress landing page
- [ ] Admin-only MCP tools for operator: platform stats, cross-user management, deployment trigger
- [ ] Modular pricing: base plans + optional add-on packages with early bird urgency
- [ ] Affiliate program: 25% recurring commission, referral dashboard
- [ ] Public launch: mystorey.io landing page, demo video, Product Hunt / HN
- [ ] Webshop support: embed section (Stripe Payment Links / Gumroad) for client sites
- [ ] Email verification flow + password reset (functional, needs visual polish)
- [ ] Structured logging + error monitoring (Sentry)
- [ ] Slug uniqueness DB constraint (race condition fix)
- [ ] Static HTML snapshot generation on publish + Cloudflare Pages serving

### Out of Scope

- Server-side AI API calls for user-facing content generation — philosophy: user's AI client does the generation, MyStorey is the dumb toolbox
- Drag-and-drop page builder — we are AI-first, not Squarespace
- Native mobile app — web-first, mobile later
- Multi-language admin UI — English only for v1 public launch
- Real-time collaborative editing — single user per site for now

## Context

**Stack:** Next.js 15 App Router + FastAPI + PostgreSQL 16 + MCP server (FastAPI HTTP+SSE). 6 Docker services: nginx, frontend, backend, mcp_server, postgres, mailpit (dev). Deployed via Coolify on Hetzner dedicated server. CLI: `./cli.sh`. Pre-commit hooks: lefthook (lint → typecheck → test).

**Domain:** mystorey.io / mystorey.ai. Brand: violet (#7c3aed). Repo: `git@github.com:docmet/aicms.git`.

**Current staging:** mystorey-staging on docmet infrastructure. Prod: auto-migrate on deploy via `start.sh` (alembic upgrade head → uvicorn).

**Test credentials:** norbi@docmet.com / password123 (admin, agency plan), client@docmet.com / password123 (pro plan, Brew & Bean Coffee demo site).

**MCP protocol:** HTTP+SSE. Works with Claude.ai, Claude Desktop, ChatGPT (Developer mode), Claude Code. MCP URL format: `{origin}/mcp`.

**Operator workflow:** Claude Code (Max subscription, local) for development. Plan: Claude.ai connected to MyStorey admin MCP for operations (platform stats, client site generation). No Anthropic API billing for user-facing features.

## Constraints

- **Tech stack**: Next.js 15 + FastAPI + PostgreSQL — no changes to core stack
- **AI philosophy**: Never call AI APIs for user-facing features. User's AI client is the intelligence layer.
- **Pricing**: Modular packages, not rigid tiers. Early bird pricing with visible increase schedule.
- **Commits**: Conventional commits, direct to main, no feature branches. lefthook enforces lint + typecheck + test.
- **Dev migrations**: Must run `alembic upgrade head` manually in dev container; prod auto-migrates on deploy.
- **Import style**: ruff enforces alphabetical import sort — run `ruff check --fix` after adding imports.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MCP as primary AI interface (not custom API) | Standards-based, works with any AI client automatically | ✓ Good — Claude.ai, ChatGPT, Claude Code all work |
| FastAPI HTTP+SSE for MCP (not stdio) | SSE enables real-time preview; stdio won't work on shared hosting | ✓ Good |
| Draft/publish split per section | AI writes to draft, human publishes — safety gate | ✓ Good |
| Hosted bridge architecture for WP plugin | SSE unreliable on shared WP hosting; reuses existing infra | — Pending |
| Modular add-on pricing over rigid tiers | More flexible, better perceived value, easier upsell | — Pending |
| No user-facing AI API calls | Cost/quality ownership stays on user's AI subscription | ✓ Good — core philosophy |
| Cloudflare R2 for production file storage | Cost-effective, CDN-native, no egress fees | ✓ Good |
| Stripe for billing (not Revolut) | Stripe Tax, Customer Portal, webhook reliability | ✓ Good |

---
*Last updated: 2026-03-07 after session initialization*
