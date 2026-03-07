# MyStorey — Business Strategy

**Date:** 2026-03-07
**Status:** Working document

---

## What We're Building

MyStorey is an AI-first website platform with three modes of use:

1. **SaaS product** — anyone signs up, builds a site via AI chat (Claude, ChatGPT), publishes to mystorey.io subdomain or custom domain
2. **Agency engine** — internal tool for docmet.com to run client sites (landing pages, blogs, webshops) on the MyStorey stack instead of legacy solutions
3. **WordPress plugin** — paid add-on that gives any WordPress site AI-powered content editing via MCP, with MyStorey as the backend bridge

All three share the same engine, MCP server, and billing infrastructure. Each has a different go-to-market.

---

## Go-to-Market Order

### Track 1: Agency use (internal, now)
- Move existing docmet.com client sites to MyStorey engine first
- Zero marketing needed — captures real usage patterns and bugs before public launch
- Forces us to build the features real clients need (eCommerce links, custom domains, contact forms working end-to-end)
- Target: 3 client sites live before any public announcement

### Track 2: WordPress plugin (next 2–3 weeks)
- Fastest path to external revenue — WP market is established and paying
- Plugin is a free PHP install; subscription billed via MyStorey Stripe
- Pricing: $9/mo (1 site) / $29/mo (5 sites + WooCommerce tools)
- `/wordpress` landing page with Matrix pill framing (see research doc)
- Distribution: direct zip download first, WordPress.org listing later for organic
- Every WP plugin customer is a warm lead for full MyStorey upsell

### Track 3: MyStorey public launch (within 1–2 months)
- Launch only when: (a) the product is solid enough for cold users, (b) we have 1–2 real testimonials
- Landing page with demo video showing AI building a site in real time
- Free plan as top-of-funnel (1 site, badge), Pro $9.99/mo, Agency $99/mo
- Channels: Product Hunt, Hacker News "Show HN", AI/no-code communities
- Content marketing: blog posts on "how to build a site with Claude" drive SEO

---

## Client Sites on MyStorey (Agency Track)

What client types the engine already supports:
- **Landing pages** — hero + features + testimonials + CTA + contact: fully done
- **Blogs** — blog posts with RSS, tags, cover images: fully done
- **Multi-page sites** — nav, multiple pages, per-page publishing: done
- **Contact/lead capture** — form submissions + email notification + admin inbox: done

What's needed for webshops (next):
- Product page section type (image, title, description, price, external "Buy" link)
- Or: embed section to drop in a Gumroad / Snipcart / Stripe Payment Link widget
- Custom domain + SSL (Cloudflare proxy): planned Phase 12 completion

**Immediate action:** identify 1–2 docmet clients whose sites are simple enough to migrate first. Use the onboarding wizard to build their new site alongside them, then cut over DNS.

---

## AI-Automated Operations

The goal: run the platform with near-zero human ops overhead by using AI for support, feedback triage, and development planning.

### Support automation (Phase 14+)
- In-app help widget: user types question → Claude answers from a MyStorey knowledge base
- Escalation only if Claude confidence is low or user explicitly requests human
- Contact form on the landing page routes to Claude first → summarized ticket in Slack/email
- Build the knowledge base as we document features (each new phase = update KB)

### Feedback triage
- Form submissions from `/contact` tagged by intent: bug report / feature request / billing / general
- AI categorizes + drafts response → human reviews before sending (for now)
- Later: fully automated for common cases (billing questions, "how do I..." queries)

### Development planning
- Claude Code as the primary development tool (already in place)
- Roadmap + STRATEGY.md as the persistent context — update after every session
- Each week: review metrics (signups, active sites, support volume) → prioritize backlog
- Bug reports from Sentry (planned) feed directly into planning sessions

---

## Marketing Strategy

### Positioning
- Not "website builder" (crowded, feature war with Squarespace)
- "The website platform built for AI assistants" — unique, defensible
- Secondary: "build and manage your site just by chatting with Claude or ChatGPT"

### WordPress plugin angle
- "Your WordPress stays WordPress. Your AI finally gets to work."
- Matrix pill: blue pill (stay in WP + add AI) vs red pill (go native with MyStorey)
- Content: blog post "How to give Claude access to your WordPress site in 5 minutes" → SEO + sharing

### MyStorey SaaS angle
- Hero demo: screencast of Claude building a full site in under 5 minutes
- Testimonial from first real client (get permission from docmet client)
- Free trial implicit: Free plan lets anyone start without credit card

### Channels (prioritized)
1. Product Hunt — single coordinated launch day, all votes concentrated
2. "Show HN" on Hacker News — technical audience, good for MCP angle
3. Twitter/X — post the demo video, tag AI/developer communities
4. WordPress community (forums, r/Wordpress, WPBeginner) — for plugin specifically
5. SEO — "build website with Claude", "MCP website builder" — low competition right now

---

## Revenue Model

| Product | Free | Paid |
|---|---|---|
| MyStorey SaaS | 1 site, badge, mystorey.io subdomain | $9.99/mo Pro (3 sites, custom domain) · $99/mo Agency (15 sites) |
| WordPress Plugin | — | $9/mo Starter (1 site) · $29/mo Pro (5 sites + WooCommerce) |

Revenue target milestones:
- **€500 MRR** — validation. Pay for hosting + MCP API costs. Achievable with ~50 Pro users.
- **€2,000 MRR** — ramen profitable. Focus full-time justified.
- **€10,000 MRR** — hire part-time support/dev. Start Agency white-label track seriously.

---

## Open Questions (to resolve)

1. **Webshop approach** — embed external (Stripe Payment Links / Gumroad) or build native product pages? Embed is faster; native is stickier.
2. **WordPress.org listing** — submit immediately for organic reach, or keep as direct download to stay nimble on updates? Recommendation: direct download first, submit after v1.1.
3. **Support tooling** — build in-app AI help widget now (Phase 14) or rely on email for first 100 users? Recommendation: email first, build widget when ticket volume warrants it.
4. **Agency pricing** — bill internal docmet clients separately, or treat as internal cost? Recommendation: no billing for internal use until platform is stable.
5. **Staging environment** — mystorey-staging is live but not consistently used for QA. Should it mirror production data? Recommendation: yes, run seed against staging before each release.
