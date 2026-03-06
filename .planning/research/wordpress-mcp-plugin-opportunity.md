# WordPress MCP Plugin — Market Research & Plan

**Date:** 2026-03-06
**Status:** Planned (weekend project)

---

## 1. Verdict

**Build it.** Weekend project scope. ~2 days core, 3-4 days with polish.

WordPress 6.9 ships MCP in core (~Q2 2026) — this will mainstream the concept and create organic demand.
AI Engine has 100k+ installs at $59/yr proving the market pays. Nobody ships the combo that matters.

---

## 2. The Gap Nobody Fills

Every existing WP MCP tool is a raw adapter for developers. None ship:

- Real-time SSE live preview while AI edits
- Draft/publish safety gate (AI writes to draft, human publishes)
- Version rollback via MCP
- OAuth flow that works in Claude.ai and ChatGPT (consumer AI, not just Claude Desktop)

**Market landscape (for reference):**

| Product | Reach | Gap |
|---|---|---|
| AI Engine | 100k+ installs, $59/yr | No preview, no draft/publish, no rollback |
| Respira | Early-stage, €19/yr | No live preview, limited to blocks |
| WordPress/mcp-adapter | Official OSS | Developer-only, no UI, no preview |
| StifLi Flex MCP | Free, GitHub | Developer-only, no SaaS |
| Angie by Elementor | Beta | Locked to Elementor |
| WordPress 6.9 core | Ships Q2 2026 | Adapter only — no UX layer |

---

## 3. Architecture

**Hosted SaaS bridge** — plugin is a free install, all intelligence lives in MyStorey's infrastructure.

```
Claude.ai / ChatGPT
      |
      | MCP (HTTP+SSE, OAuth)
      v
MyStorey MCP Bridge (hosted — reuses existing server)
      |
      | WP REST API (Application Password auth)
      v
WordPress Plugin (free install on user's site)
```

Why hosted bridge, not self-contained plugin:
- SSE doesn't work reliably on shared WP hosting (most WP sites)
- Reuses 100% of existing MyStorey OAuth, SSE, token infra
- Enables recurring revenue, not one-time purchase
- Preview relay works even on $3/mo hosting

---

## 4. MVP Scope (Weekend Build)

### What's already done (zero new work)
- MCP server, OAuth, SSE infrastructure
- Token auth, tool routing
- Connection UI pattern ("Connect AI Tools" page)
- Draft/publish concept, version model

### What's new

| Task | Time |
|---|---|
| WordPress plugin (PHP) — settings page, Application Password setup, "Your MCP URL" display | 0.5 day |
| WP tool handlers in MCP server — `httpx` calls to `wp-json/wp/v2/*` (pages, posts, site settings) | 0.5 day |
| Connection flow: install plugin → get credentials → paste MCP URL into Claude/ChatGPT | 0.5 day |
| MyStorey landing page for WP plugin (see section 6) | 0.5 day |

**Total: ~2 days core, 3-4 with polish**

### v1 tools (read + write, no preview yet)

Read: `get_site_info`, `list_pages`, `list_posts`, `get_page_content`, `get_theme_info`

Write (draft-safe): `update_page_content`, `create_page`, `publish_page`, `update_post`, `update_site_settings`

Bonus (WP has revisions built-in, easy win): `list_versions`, `revert_to_version`

Skip for v1: live SSE preview (WP has built-in preview URLs Claude can open), WooCommerce, multi-site

---

## 5. Strategy: WP Plugin First, MyStorey Alongside

**Both products are unreleased.** MyStorey has no existing user base to cross-sell into yet.

**Option A — WP plugin ships first (next week)**
Faster to monetize. WP has an established, paying audience right now. MyStorey can follow shortly after, or launch the same week. Plugin gives MyStorey a warm top-of-funnel from day one.

**Option B — Launch both together**
Single launch moment. Plugin brings WP users in; Matrix pill framing converts some of them to MyStorey. More coordinated story.

**Recommendation: lean toward Option A or same-week double launch.** The WP plugin is 2-3 days of work and can start generating revenue before MyStorey is fully polished for launch.

**Phase 1 — WP plugin as standalone product**
Own focused landing at `/wordpress` within mystorey.io (or a simple static page). No dependency on MyStorey being live. Paid-only from day one (see section 8).

**Phase 2 — MyStorey launch (same week or shortly after)**
Matrix pill page connects both. WP plugin customers are already warm leads.

**Phase 3 — Full integration**
WordPress sites as a first-class site type inside MyStorey dashboard. One-click migration tool (WP → MyStorey). Only after both products have paying users.

---

## 6. Marketing: The Matrix Pill

**Positioning on the landing page:**

> Managing content on WordPress but wish your AI could just... do it?
>
> You have two choices.
>
> **The blue pill** — the best WordPress plugin for non-technical content managers. Install it, connect Claude or ChatGPT, let AI update your pages while you watch. Safe, familiar, WordPress stays WordPress.
>
> **The red pill** — skip WordPress entirely. MyStorey gives you the same AI-powered editing with a real-time live preview, draft/publish safety, and version rollback — built from the ground up for AI-first content management.
>
> Either way, your AI gets to work. You choose how deep you want to go.

**Why this works:**
- Sells the plugin on its own merits to people who need WP
- Sells MyStorey as the "escape hatch" for people ready to leave WP
- Non-pushy — the user picks; both choices are framed positively
- Every WP plugin customer is a warm lead for MyStorey upsell

**Landing page location:** `/wordpress` within the existing MyStorey Next.js project. Single page, no new infra, ships with the rest.

---

## 7. Migration Path (Later — Automated)

Once the WP plugin exists, build a one-click migration tool:

- Plugin exports: pages, posts, images, theme colors, nav structure
- MyStorey importer creates equivalent pages + sections
- AI runs `generate_section` to reconstruct content in MyStorey format
- User reviews draft, publishes

This turns every WP plugin user into a potential full MyStorey convert. The plugin becomes a top-of-funnel for the main product.

**Marketing line:** "Switch from WordPress to MyStorey in one click. Your content comes with you."

---

## 8. Pricing — Paid Only From Day One

No free tier. Reasons:
- Free users generate support noise, drain API/hosting costs, and dilute focus
- Neither product has a user base yet — no funnel to justify a free plan
- Paid-only signals quality and filters for serious users
- Can always add a free tier later once there's capacity to handle it

| Tier | Price | Limits |
|---|---|---|
| Starter | $9/mo | 1 WP site, all read + write tools |
| Pro | $29/mo | 5 WP sites, WooCommerce tools |

No trial needed — keep the landing page demo video clear enough that buyers know what they're getting. Stripe checkout, same billing infra as MyStorey.

---

## 9. Build Order

1. WP plugin (PHP) — minimal, just settings + Application Password + copy-the-URL
2. WP tool handlers in existing MCP server
3. `/wordpress` landing page in MyStorey (Matrix pill framing)
4. Connection flow end-to-end test
5. Zip download + install instructions (no WordPress.org submission needed for v1)
6. (Later) WordPress.org listing for organic reach
7. (Later) One-click WP → MyStorey migration tool
