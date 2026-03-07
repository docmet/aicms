# Roadmap: MyStorey

## Milestones

- ✅ **v1.0 Foundation** - Phases 1–13 (shipped 2026-03-07)
- 🚧 **v1.1 Launch Ready** - Phases 14–17 (in progress)

## Phases

<details>
<summary>✅ v1.0 Foundation (Phases 1–13) - SHIPPED 2026-03-07</summary>

### Phase 1: Project Setup
**Goal**: Development environment and CI/CD foundation established
**Plans**: Complete

### Phase 2: Auth & Multi-tenancy
**Goal**: Users can securely register, log in, and own isolated sites
**Requirements**: AUTH-01–04, SITE-01–06
**Plans**: Complete

### Phase 3: Pages & Sections
**Goal**: Users can create multi-page sites with typed content sections
**Requirements**: PAGE-01–05, SECT-01–08
**Plans**: Complete

### Phase 4: MCP Server (Core)
**Goal**: AI assistants can connect to MyStorey via MCP and manage sites
**Requirements**: MCP-01–10
**Plans**: Complete

### Phase 5: MCP Tools (Full Suite)
**Goal**: Full 25-tool MCP surface covering all platform capabilities
**Requirements**: MCP-11–25
**Plans**: Complete

### Phase 6: Themes & Live Preview
**Goal**: Sites are visually styled with real-time AI preview
**Requirements**: THEME-01–12, SECT-01–08 (section editors)
**Plans**: Complete

### Phase 7: Onboarding & Navigation
**Goal**: New users can build a complete site in under 10 minutes
**Requirements**: ONBD-01–03, SEO-01–03
**Plans**: Complete

### Phase 8: Billing, Email & Admin
**Goal**: Users can pay for plans; admin can manage the platform
**Requirements**: BILL-01–04, EMAIL-01–05, ADMIN-01–04
**Plans**: Complete

### Phase 9: Media Library
**Goal**: Users can upload images and use them in site content
**Requirements**: MEDIA-01–05
**Plans**: Complete

### Phase 10: Section & Theme Expansion
**Goal**: Richer design options via layout variants and background controls
**Plans**: Complete

### Phase 11: Blog, Forms & Rich Content
**Goal**: Sites support blog posts, contact forms, and embedded rich content
**Requirements**: BLOG-01–05, FORM-01–04
**Plans**: Complete

### Phase 12: Custom Domains & Site-Level Publish
**Goal**: Sites can be published to custom domains in a single action
**Plans**: Complete

### Phase 13: Analytics, Preview Links & Scheduling
**Goal**: Owners can track traffic, share drafts, and schedule publication
**Requirements**: ANAL-01–04, SHARE-01–02, PAGE-01–05 (scheduled)
**Plans**: Complete

</details>

---

### 🚧 v1.1 Launch Ready (In Progress)

**Milestone Goal:** Polish the platform to production quality, ship the WordPress plugin, activate the agency track, and publicly launch MyStorey with working pricing and an affiliate program.

## Phase Details

### Phase 14: Polish & Stability
**Goal**: The platform is production-grade — visually polished, error-monitored, and safe to hand to cold users and the operator
**Depends on**: Phase 13
**Requirements**: PLSH-01, PLSH-02, PLSH-03, PLSH-04, PLSH-05, PLSH-06, OPS-01, OPS-02, OPS-03
**Success Criteria** (what must be TRUE):
  1. All 8 section type editors render without visual glitches; image fields show dimension hints and a clear upload/paste/URL flow
  2. The admin editor is fully navigable on a phone — hamburger menu opens, section editors scroll, saves work
  3. Slug creation never results in a duplicate — DB constraint enforces uniqueness even under concurrent requests
  4. Sentry captures and reports backend exceptions in production within 30 seconds of occurrence
  5. An admin user connected to MyStorey MCP can ask Claude for platform stats, a cross-user site list, and trigger a deployment — all via chat with no UI
**Plans**: TBD

### Phase 15: WordPress Plugin
**Goal**: WordPress site owners can control their WP content via AI chat by connecting to MyStorey as a bridge, with a compelling landing page and working Stripe billing
**Depends on**: Phase 14
**Requirements**: WP-01, WP-02, WP-03, WP-04, WP-05, WP-06, WP-07, WP-08, WP-09
**Success Criteria** (what must be TRUE):
  1. A WordPress admin can install the plugin zip, enter their site URL and Application Password, and see their MyStorey MCP URL on the settings page
  2. Pasting the MCP URL into Claude.ai connects successfully and the full WP tool suite is listed
  3. Claude can create, update, and publish a WordPress page and blog post via MCP tools with no manual steps
  4. The `/wordpress` landing page on mystorey.io is live with Matrix pill framing and a Stripe checkout link
  5. The plugin connection flow works identically with ChatGPT (Developer mode) — end-to-end test passes
**Plans**: TBD

### Phase 16: Agency & Webshop
**Goal**: Agency client sites on MyStorey can sell products via embedded payment links, and the internal migration path is documented and proven with 3 live client sites
**Depends on**: Phase 14
**Requirements**: AGCY-01, AGCY-02, AGCY-03
**Success Criteria** (what must be TRUE):
  1. The embed section type accepts a Stripe Payment Link or Gumroad embed URL and renders the payment widget correctly on the public site
  2. An internal migration guide exists describing how to move a docmet.com client site to the MyStorey engine (templates, DNS, domain settings)
  3. Three real client sites are live on MyStorey and publicly accessible before any launch announcement goes out
**Plans**: TBD

### Phase 17: Pricing, Affiliate & Public Launch
**Goal**: MyStorey is publicly launched with modular pricing, early bird urgency, an affiliate program, and polished launch assets that communicate the platform's velocity
**Depends on**: Phase 16
**Requirements**: PRIC-01, PRIC-02, PRIC-03, PRIC-04, LAUN-01, LAUN-02, LAUN-03, LAUN-04, LAUN-05
**Success Criteria** (what must be TRUE):
  1. The pricing page shows modular add-ons (custom domain, extra sites, priority support) with early bird strikethrough prices and a lock-in message; checkout completes correctly for any combination
  2. Every logged-in user sees their referral link in the dashboard; clicking it tracks attribution; affiliates see earnings in real time
  3. Affiliate payouts route via Stripe once earnings exceed $50; the payout flow completes without manual intervention
  4. A new user can sign up, create a site, connect Claude.ai, and publish a live page in under 10 minutes — verified by walking through the onboarding funnel cold
  5. The mystorey.io landing page is live with demo video, Matrix pill framing, testimonials, pricing, and the AI connection guide; the Product Hunt launch asset (2-min video) is ready
**Plans**: TBD

---

## Progress

**Execution Order:** 14 → 15 → 16 → 17 (Phase 16 can start in parallel with 15 after Phase 14)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–13. Foundation | v1.0 | All | Complete | 2026-03-07 |
| 14. Polish & Stability | v1.1 | 0/TBD | Not started | - |
| 15. WordPress Plugin | v1.1 | 0/TBD | Not started | - |
| 16. Agency & Webshop | v1.1 | 0/TBD | Not started | - |
| 17. Pricing, Affiliate & Launch | v1.1 | 0/TBD | Not started | - |
