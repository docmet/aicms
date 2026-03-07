# MyStorey — Business Strategy

**Date:** 2026-03-07
**Status:** Living document — update after every strategic decision

---

## Core Philosophy

### The Dumb Toolbox Principle
MyStorey is a **high-quality, well-documented backend**. The user's AI client (Claude, ChatGPT, Perplexity, etc.) is the intelligence layer. We never embed user-facing AI API calls into the platform.

**Why:**
- Cost ownership stays on the user — their subscription, their bill
- Quality ownership stays on the AI provider — if ChatGPT writes bad copy, that's not our bug
- Works with any current or future MCP-compatible AI client automatically
- Keeps the platform lean, fast, and predictable

**What this means in practice:**
- Our MCP tool descriptions and response messages ARE the product — they must be exceptional
- The richer our tool docs + field comments + example values, the better any AI performs with us
- We never call Anthropic/OpenAI APIs for user-facing content generation

### AI for Platform Operations (Gradual)
We DO use AI on the operator side, and can offer it as a premium feature for users later:

**Phase 1 (now):** Claude Code (Max subscription) for development — this session is the model
**Phase 2 (soon):** Admin MCP tools — operator connects Claude.ai to MyStorey as admin, drives operations through conversation: platform stats, user audits, client site generation, deployment triggers
**Phase 3 (later):** API-backed AI features for premium user tiers — e.g., "AI content audit", "AI SEO suggestions", "bulk site generation from a spreadsheet" — charged at Agency+ plan level where the economics work

---

## What We're Building

MyStorey is an AI-first website platform with three modes of use:

1. **SaaS product** — anyone signs up, builds a site via AI chat (Claude, ChatGPT), publishes to mystorey.io subdomain or custom domain
2. **Agency engine** — internal tool for docmet.com to run client sites (landing pages, blogs, webshops) on the MyStorey stack instead of legacy solutions
3. **WordPress plugin** — paid add-on that gives any WordPress site AI-powered content editing via MCP, with MyStorey as the backend bridge

All three share the same engine, MCP server, and billing infrastructure. Each has a different go-to-market.

---

## Platform Narrative: Tip of the Iceberg

**Communicate everywhere:** what exists today is the foundation. The platform evolves at an extraordinary pace — new section types, AI tool integrations, WooCommerce support, multilingual, AI image generation, bulk site creation. Early adopters who join now lock in lower prices and shape the product directly.

This is not just a feature promise — it is a real structural advantage. Every AI capability that gets added to Claude/ChatGPT automatically becomes available to MyStorey users with zero update needed on their end. The MCP protocol means our platform compounds in value as AI improves.

---

## Go-to-Market Order

### Track 1: Agency use (internal, now)
- Move existing docmet.com client sites to MyStorey engine first
- Zero marketing needed — captures real usage patterns and bugs before public launch
- Forces us to build the features real clients need (eCommerce links, custom domains, contact forms working end-to-end)
- Target: 3 client sites live before any public announcement

### Track 2: WordPress plugin (this weekend)
- Fastest path to external revenue — WP market is established and paying
- Plugin is a free PHP install; subscription billed via MyStorey Stripe
- Pricing: modular (see Pricing section below)
- `/wordpress` landing page with Matrix pill framing (see research doc)
- Distribution: direct zip download first, WordPress.org listing later for organic
- Every WP plugin customer is a warm lead for full MyStorey upsell

### Track 3: MyStorey public launch (within 4–6 weeks)
- Launch only when: (a) solid enough for cold users, (b) 2–3 real client sites as case studies
- Landing page with demo video showing AI building a site in real time
- Communicate "tip of the iceberg" narrative prominently
- Channels: Product Hunt, Hacker News "Show HN", AI/no-code communities, WP communities
- Content marketing: "how to build a site with Claude in 5 minutes" → SEO

---

## Client Sites on MyStorey (Agency Track)

What client types the engine already supports:
- **Landing pages** — hero + features + testimonials + CTA + contact: fully done
- **Blogs** — blog posts with RSS, tags, cover images: fully done
- **Multi-page sites** — nav, multiple pages, per-page publishing: done
- **Contact/lead capture** — form submissions + email notification + admin inbox: done

What's needed for webshops:
- Option A (fast): embed section with Stripe Payment Link / Gumroad widget (2h build)
- Option B (proper): product page section type with image, price, "Buy" CTA (2 days)
- Custom domain + Cloudflare SSL: Phase 12 completion

---

## Pricing Strategy

### Principles
- **Modular packages** — base price + optional add-ons clicked together, not rigid tiers
- **Early bird urgency** — prices increase on visible schedule (e.g., +20% every 30 days until launch)
- **Annual discount** — 2 months free for yearly commitment
- **Affiliate program** — 20–30% recurring commission for referrers
- **Communicate value trajectory** — "you lock in today's price forever" + roadmap preview on pricing page

### MyStorey SaaS (proposed structure)

**Base plans:**
| Plan | Price | Sites |
|---|---|---|
| Starter | $7/mo (early bird → $9.99) | 1 site |
| Growth | $19/mo (early bird → $29) | 5 sites |
| Agency | $79/mo (early bird → $99) | 20 sites |

**Add-on packages (click to add to any plan):**
| Package | Price | What it adds |
|---|---|---|
| Custom Domain | +$3/mo | 1 custom domain + SSL |
| Extra Sites | +$5/mo | +3 additional sites |
| Priority Support | +$9/mo | <4h response, dedicated channel |
| AI Automations | +$19/mo | API-backed: SEO audit, bulk generation (Phase 3+) |
| White Label | +$49/mo | Remove MyStorey branding, use own domain for dashboard |

**Early bird mechanics:**
- Current price shown prominently with strikethrough of future price
- Countdown or "price increases on [date]" visible on pricing page
- Lock-in message: "Subscribe now — your price never increases"
- First 100 users get Founder badge in their dashboard

### WordPress Plugin (proposed structure)
| Plan | Price | Sites |
|---|---|---|
| Starter | $7/mo | 1 WP site |
| Pro | $24/mo | 5 WP sites |
| Agency | $69/mo | Unlimited WP sites + WooCommerce tools |

Add-ons same structure as above.

### Affiliate Program
- 25% recurring commission for 12 months
- Simple dashboard showing referrals + earnings
- Payout via Stripe once/month at $50 minimum
- Referral link embedded in every user's dashboard ("Refer a friend → earn cash")
- Special rate for content creators: 30% for first 90 days if they produce a review/tutorial

---

## Marketing Strategy

### Positioning
- NOT "website builder" — crowded, implies drag-and-drop, implies Squarespace competitor
- "The website platform built for AI assistants"
- Sub-message: "Your AI chat builds and manages your entire website. You just approve."

### Core message hierarchy
1. **What**: AI-first website platform connected via MCP
2. **Why now**: AI models (Claude, ChatGPT) just got powerful enough to build real sites
3. **Why us**: Every AI improvement = your site gets smarter automatically. No update needed.
4. **Why today**: Early bird pricing, lock in forever, help shape the product

### Channels (prioritized)
1. Product Hunt — single coordinated launch day
2. "Show HN" — technical audience, strong for MCP angle ("I built a website platform controlled entirely via MCP")
3. Twitter/X — demo video of AI building a full site in 2 minutes
4. WordPress community — for plugin (r/Wordpress, WPBeginner, WP forums)
5. AI communities — r/ClaudeAI, r/ChatGPT, Perplexity forums
6. SEO — "build website with Claude", "MCP website editor", "ChatGPT website builder"

### Content to produce before launch
- Demo video: 2-min screencast of Claude building a full coffee shop site from one sentence
- Blog post: "How to give Claude control of your website in 5 minutes"
- Blog post: "Why we built MyStorey instead of another website builder"
- Landing page case studies: 2–3 real client sites with before/after

---

## Operator AI System (Self-Building Platform)

### Development (now)
Claude Code (Max subscription, local) is the development environment. Every feature, fix, and refactor goes through Claude Code sessions. This session is the model.

### Operations (Phase 14)
Build admin-specific MCP tools accessible only to `is_admin=True` users:
- `get_platform_stats` — total users, sites, pages, MRR estimate, active sessions
- `list_all_sites` — cross-user site list with last activity, plan, status
- `generate_client_site` — given a client brief, generate a full site (calls existing tools in sequence)
- `audit_user_content` — check all sections for quality, completeness, broken images
- `send_platform_announcement` — queue an email to all users
- `trigger_deployment` — fire Coolify deploy from chat

Operator workflow: connect Claude.ai (Max) to MyStorey MCP as `norbi@docmet.com` → ask "show me the 5 least active sites, give me suggestions for improving them" → Claude calls admin tools, synthesizes, responds.

### Future (Phase 16+)
API-backed AI features as premium add-ons for users:
- AI content audit: Claude reviews all sections, flags thin/weak content, suggests improvements
- AI SEO report: generates per-page SEO score + specific fix recommendations
- Bulk site generation: upload a CSV of business info → generate N sites
- These require Anthropic API key on our side — priced at Agency+ level to cover cost

---

## Revenue Model & Milestones

| MRR | Meaning | Action |
|---|---|---|
| €500 | Validation — covers hosting + API | Keep building |
| €2,000 | Ramen profitable | Full-time focus justified |
| €5,000 | Hire part-time (support or dev) | Start affiliate program seriously |
| €10,000 | Small team possible | Dedicated support, white-label track |

---

## Open Questions

1. **Webshop approach** — embed (Stripe Payment Links/Gumroad, 2h) vs native product section (2 days)?
   → Recommendation: embed first, native later when clients ask for it

2. **WP plugin WordPress.org listing** — immediate vs after v1.1?
   → Recommendation: direct zip download first, submit after first 10 paying users give feedback

3. **Early bird date** — when does price go up?
   → Set a real date (e.g., April 1), display prominently, stick to it

4. **Affiliate tooling** — build in-house vs use a service (Rewardful, PartnerStack)?
   → Recommendation: Rewardful ($49/mo) to start — not worth building from scratch until €5k MRR

5. **Admin MCP tools** — build before WP plugin or after?
   → After WP plugin — operator tools are nice-to-have, WP plugin is revenue

6. **AI API features for users** — which plan level makes economics work?
   → At $0.001–0.01 per call, Agency+ ($79+/mo) covers cost comfortably at expected usage
