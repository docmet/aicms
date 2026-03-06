# Payment Processor & Tax Research: MyStorey (Hungarian SaaS, US + EU Markets)

**Date:** March 2026
**Context:** MyStorey is a SaaS platform built by a Hungarian company, currently piloting a Revolut Merchant integration. Plans to charge $9.99/mo (Pro) and $99/mo (Agency) to US and EU customers. Considering switching to Stripe.

---

## 1. Revolut Merchant vs. Stripe for SaaS Subscriptions

### 1.1 Revolut Merchant — Current State

Revolut launched its merchant acquiring service for 16 new European countries (including Hungary) in early 2025. Revolut Business is available for companies registered in EEA countries, the UK, and the US.

**Subscription billing:** Revolut launched a native "Subscriptions" tool for recurring billing in **January 2026 — but currently for UK merchants only**. EEA rollout was announced but no confirmed timeline. The API does exist (developer.revolut.com/docs/merchant/subscriptions) for API-level integration, but the managed in-app subscriptions product is UK-first.

**What Revolut Merchant does support (via API):**
- Recurring charges on saved payment methods (merchant-initiated transactions / MIT)
- Flexible billing cycles and plan phases
- Free trial periods followed by paid phases
- Automated payment reminders (basic)
- Payment links and hosted checkout pages

**What Revolut Merchant notably lacks (compared to Stripe):**
- No native customer self-service portal (customers cannot update cards, view invoices, cancel, or upgrade themselves — all must be built custom)
- No automated dunning system — when a payment fails, the merchant is responsible for building their own notification and retry logic
- No out-of-the-box proration handling for plan changes
- No revenue recognition tooling
- No metered/usage-based billing support
- No embedded tax calculation (no VAT/sales tax automation)
- Significantly thinner developer ecosystem and fewer third-party integrations
- No equivalent to Stripe's Sigma (analytics), Radar (fraud scoring), or Atlas

**Revolut Merchant — Fee Structure (EU merchants, 2025/2026):**

| Card Type | Rate | Flat Fee |
|-----------|------|----------|
| EEA consumer cards | 1.0% | €0.20 |
| Non-EEA / international cards (incl. US) | 2.8% | €0.20 |
| No setup fees | — | — |
| No monthly platform fee | — | — |

For a $9.99 subscription from a US customer: ~$0.48 fee (2.8% + $0.20)
For a $9.99 subscription from an EU customer: ~$0.30 fee (1.0% + €0.20)

Note: Revolut has no additional subscription management fee on top of acquiring fees (unlike Stripe Billing's 0.7%). This is a real cost advantage — but only if you build dunning, customer portal, and proration yourself.

---

### 1.2 Stripe — Current State

Stripe is fully available in Hungary. Hungarian companies can open a Stripe account with full feature access. Stripe has a dedicated Services Agreement for Hungary.

**Fee Structure (EU/Hungarian merchant, 2026):**

| Transaction Type | Rate | Flat Fee |
|-----------------|------|----------|
| European card (standard) | 1.4% | ~€0.25 (approx 85 HUF) |
| International card (non-EEA, incl. US) | +1.5% surcharge | same flat |
| US customer paying EU merchant (total) | ~2.9% | + flat fee |
| Currency conversion (if applicable) | +2% | — |
| Stripe Billing (subscriptions) | +0.7% of volume | — |
| Stripe Tax (VAT/sales tax automation) | +0.5% of volume | — |

**Realistic total cost for a US customer paying $9.99/mo via Stripe (with Billing):**
- 1.4% + 1.5% (international) + 0.7% (Billing) = **3.6% + ~€0.25 flat**
- On $9.99: ~$0.61 in fees
- If currency conversion also applies: add ~2% → ~$0.81

**Realistic total for an EU customer paying $9.99/mo via Stripe (with Billing):**
- 1.4% + 0.7% (Billing) = **2.1% + ~€0.25 flat**
- On $9.99: ~$0.46 in fees

**What Stripe Billing (0.7% fee) includes:**
- Full subscription lifecycle management (create, upgrade, downgrade, cancel, pause)
- **Automatic proration** for mid-cycle plan changes
- **Smart Retries** — ML-powered retry scheduling that recovers ~57% of failed payments
- **Automated dunning emails** — expiring card reminders, failed payment notifications, renewal notices, with one-click payment update links
- **Customer Portal** — fully hosted, zero-code: customers self-manage subscriptions, update cards, view invoices, cancel/upgrade — branded to your product
- Revenue Recognition (accrual-basis, GAAP-aligned reporting)
- Free trials, coupons, multiple pricing models (flat, tiered, per-seat, metered)
- Metered/usage-based billing via Meters API

**Stripe Tax (additional 0.5% of transactions):**
- Automatic VAT calculation and collection for EU B2C sales
- Automatic US sales tax calculation across all states
- Handles reverse charge for EU B2B (validated VAT numbers)
- Supports OSS filing data export
- Covers 100+ countries

**Stripe ecosystem advantages:**
- 195+ countries, 135+ currencies
- Decades of battle-tested SaaS tooling
- Enormous third-party ecosystem (analytics, CRMs, tax, auth platforms)
- Stripe Radar (ML fraud protection, included)
- Stripe Sigma (SQL analytics on your payments data)
- Recognized as Leader in Forrester Wave Recurring Billing Q1 2025 and Gartner Magic Quadrant 2025

---

### 1.3 Direct Comparison Summary

| Feature | Revolut Merchant | Stripe |
|---------|-----------------|--------|
| Available in Hungary | Yes | Yes |
| Recurring subscriptions (managed) | UK only (Jan 2026 launch); API available | Full, all countries |
| Customer self-service portal | No | Yes (included) |
| Automated dunning / smart retries | Manual (merchant builds) | Yes (included) |
| Proration on plan changes | Must build manually | Yes (automatic) |
| Metered / usage-based billing | No | Yes |
| Free trials | Via API phases | Yes |
| VAT/tax automation | No | Stripe Tax (0.5% extra) |
| Revenue recognition | No | Yes (included with Billing) |
| Developer ecosystem | Limited | Industry-leading |
| EEA card processing fee | 1.0% + €0.20 | 1.4% + ~€0.25 |
| Non-EEA (US) card fee | 2.8% + €0.20 | 2.9% + ~€0.25 (incl. intl surcharge) |
| Subscription management fee | 0% | 0.7% of volume |
| Tax automation fee | 0% | 0.5% of volume |
| Monthly platform fee | None | None |

**Bottom line on fees:** Revolut is cheaper per transaction for EEA cards and has no subscription management fee. However, that 0.7% saving on a $10 subscription equals $0.07/month. The operational cost of building dunning, customer portal, and proration from scratch vastly outweighs this saving for a startup team.

---

## 2. Regional Limitations

### 2.1 Can a Hungarian Company Use Revolut Merchant to Charge US Customers?

**Yes**, technically. Revolut merchant acquiring supports international (non-EEA) cards including US-issued cards. The fee is 2.8% + €0.20 per transaction. However:
- The advanced subscription management product (in-app Subscriptions tool) is currently UK-only
- Support and documentation are UK-centric
- There is no indication of a specific US checkout optimization
- USD settlement may add FX complexity

### 2.2 Can a Hungarian Company Use Stripe to Charge US and International Customers?

**Yes, fully.** Stripe's global network covers 195+ countries and 135 currencies. A Hungarian company on Stripe can:
- Charge US cards in USD (with international card surcharge applied)
- Charge EU customers in EUR or their local currency
- Settle to a Hungarian bank account in EUR or HUF
- Access the full Stripe product suite globally

### 2.3 Countries Where Either Processor Is Blocked or Limited

**Revolut Merchant:** Currently available for businesses registered in EEA, UK, and USA. Cannot be used by businesses in most non-EEA countries. Limited to 25 currencies for acceptance.

**Stripe:** Available in 47+ countries for businesses (account holders). Some sanctioned countries are excluded (Iran, North Korea, Cuba, Syria, etc.) as standard. For a Hungarian company, no meaningful restrictions apply.

**Key note:** Both processors can accept payments from customers in countries other than where the merchant is based. The restriction is about where the *merchant/business* is registered, not where their customers are located.

---

## 3. VAT and Taxation — Hungarian Company Selling SaaS

### 3.1 Hungary Baseline VAT Context

Hungary has the **highest standard VAT rate in the EU: 27%**. This applies to most digital services and SaaS. However, a Hungarian company selling SaaS cross-border must apply the **customer's country VAT rate**, not 27%, for sales to other EU countries (once the €10,000 OSS threshold is crossed).

For a B2B sale to another EU company: 0% (reverse charge applies, customer self-accounts).

### 3.2 EU VAT — OSS (One Stop Shop)

**What OSS is:** OSS is an EU-wide portal that lets a business registered for VAT in one EU member state (Hungary, via NAV) file a single quarterly return covering all B2C cross-border digital service sales across all EU member states. Without OSS, a company would need to register for VAT separately in every EU country where it has B2C customers.

**The threshold:** €10,000 per year in combined cross-border B2C sales across all EU member states. This is a single pan-EU threshold (since July 2021 — the old per-country thresholds no longer apply).

**Below €10,000:** You can charge Hungarian VAT (27%) on all EU B2C sales and keep compliance simple (single domestic filing). However, voluntary OSS registration is allowed at any scale.

**Above €10,000:** You must either:
- Register for OSS in Hungary (via NAV), file quarterly returns, apply each customer's country rate, and remit centrally through NAV; OR
- Register for VAT individually in each EU country where you have customers (not recommended)

**OSS is strongly recommended** once you exceed the threshold. It is the standard approach for European SaaS companies.

**OSS filing deadlines (2025+ rules):**
- Q1 return: due April 30
- Q2 return: due July 31
- Q3 return: due October 31
- Q4 return: due January 31
- (As of 2025, deadline extended from 20 days to 30 days after quarter end)

**For MyStorey specifically:** At launch, you will very likely stay below €10,000 in cross-border EU B2C sales. You can defer OSS registration until you approach that threshold. Once you cross it, register with NAV.

### 3.3 B2B vs. B2C EU VAT for SaaS

**B2C (selling to consumers, individuals without a VAT number):**
- You charge VAT at the customer's country rate
- You collect and remit via OSS
- No burden on the customer; they pay the gross price including VAT

**B2B (selling to businesses with a valid EU VAT number):**
- **Reverse charge applies** — you do NOT charge VAT
- Invoice shows "0% — reverse charge" / "VAT exempt under Art. 44 VAT Directive"
- The customer self-accounts for VAT in their own country
- You must validate and record the customer's VAT number at time of purchase
- This is simpler and no VAT cash-flow issue for you

**Practical implication for MyStorey:** Most SaaS buyers at the Pro/Agency tier are small businesses or freelancers. Many will have VAT numbers. Stripe Tax automates B2B VAT number validation and reverse charge handling.

### 3.4 US Sales Tax — What a Hungarian Company Must Know

**The Wayfair Ruling (2018):** US states can require remote sellers (no physical presence) to collect sales tax if they cross "economic nexus" thresholds — usually $100,000 in annual sales to customers in that state.

**Which states tax SaaS:** As of 2026, approximately **25 US states** tax SaaS in some form. The major states include:
- New York, Texas, Pennsylvania, Washington, Ohio, Connecticut, Tennessee, Kentucky, Hawaii, and others
- Notable **non-taxing states for SaaS:** California (generally exempt), Florida (generally exempt), Illinois (depends on use)
- **No sales tax at all:** Alaska, Delaware, Montana, New Hampshire, Oregon

**Economic nexus thresholds — key states:**

| State | Sales Threshold | Transaction Threshold |
|-------|----------------|----------------------|
| Most states | $100,000 | 200 transactions (many states removing this) |
| California | $500,000 | None (and SaaS often exempt in CA) |
| New York | $500,000 | AND 100 transactions |
| Texas | $500,000 | None |
| Washington | $100,000 | None |
| Illinois (as of Jan 1, 2026) | $100,000 | None (removed 200-transaction threshold) |

**Is there a threshold below which a Hungarian SaaS company doesn't need to worry about US taxes?**

**Yes — effectively yes, at the revenue levels MyStorey will operate at initially.** Here is the practical reality:

- A Hungarian company with no US physical presence (no employees, no office, no servers) has no physical nexus in any US state.
- Economic nexus only triggers when you reach $100,000 (or $500,000 in CA/NY/TX) in sales *to customers in that specific state*.
- At $9.99/mo, reaching $100,000 in a single state means acquiring ~834 paying customers in that state alone. For a startup, this is a meaningful milestone, not a launch-day concern.
- **Below those thresholds in each state, you have zero legal obligation to collect or remit US sales tax in that state.**

**Federal income tax:** US federal tax treaties with Hungary generally protect a Hungarian company from US federal corporate income tax unless they have a "permanent establishment" in the US. No US office or employees = no permanent establishment in most cases. US sales tax is a state-level matter, not covered by federal treaties.

### 3.5 What Do Most Small European SaaS Companies Do at Launch?

The practical consensus among European SaaS founders (well-documented by practitioners):

1. **At launch, ignore US sales tax entirely.** Below economic nexus thresholds in every state, there is no legal obligation. The risk of enforcement against a small European company below thresholds is negligible to zero.

2. **Start with basic EU VAT compliance.** Below €10,000 in cross-border EU B2C sales, charge Hungarian VAT (27%) or register for OSS voluntarily and use Stripe Tax to automate. Above €10,000, register for OSS.

3. **Use Stripe Tax or a Merchant of Record (Paddle)** to automate the complexity rather than managing manually.

4. **Scale into US tax compliance** when revenue justifies it: typically when approaching $100,000 in a major state. At that point, tools like TaxJar or Avalara can automate registration, calculation, and filing.

5. Some founders choose **Paddle (Merchant of Record)** to offload *all* tax compliance globally from day one, at the cost of a higher fee (5% + $0.50 vs Stripe's ~3.6% all-in with Billing).

---

## 4. Practical Recommendations

### 4.1 Payment Processor: Use Stripe

**Recommendation: Switch from Revolut Merchant to Stripe. Do not build MyStorey's subscription infrastructure on Revolut.**

Reasons:

1. **Revolut's subscription management product is UK-only as of early 2026.** As a Hungarian company, you cannot access the managed subscriptions product without building everything via raw API calls — and that API is less documented and less battle-tested than Stripe's.

2. **The missing features matter enormously for SaaS churn and revenue.** Smart Retries (recovering ~57% of failed payments), automated dunning emails, and a self-service customer portal are not nice-to-haves — they directly impact monthly revenue and support load. Building these from scratch on Revolut's API represents weeks of engineering work that Stripe provides on day one.

3. **The fee difference is trivial at MyStorey's current scale.** Revolut saves roughly €0.07 per $10 EU subscription compared to Stripe Billing. That saving becomes meaningful at millions in ARR, not at launch.

4. **Stripe's ecosystem is essential for a SaaS product.** Stripe Tax, revenue recognition, customer portal, coupons, trials, proration — these are integrated into your product's UX. Revolut requires you to build all of this custom.

5. **Stripe is fully available and well-supported in Hungary** with a dedicated Services Agreement and pricing page for Hungarian businesses.

6. **US customers are a priority market.** Stripe is the de-facto standard for US SaaS customers, offers better checkout conversion, and handles USD natively. Revolut is unknown to US customers and may cause friction.

### 4.2 Tax Setup: Minimum Viable Compliance at Launch

**Phase 1: Launch (pre-€10,000 EU B2C revenue)**

- Register Stripe and enable **Stripe Tax** (0.5% per transaction).
- Stripe Tax will automatically calculate correct VAT rates for EU B2C customers, handle reverse charge for EU B2B customers (validate VAT numbers), and calculate US sales tax where applicable.
- Keep a watch on cross-border EU B2C cumulative revenue. Below €10,000, you can charge Hungarian 27% VAT on all EU B2C sales (Stripe Tax handles this automatically based on your registered location).
- US customers: collect whatever Stripe Tax calculates for states where you are registered. At launch, you are registered nowhere in the US — Stripe Tax will not charge US sales tax until you register in a state. Do not register in any US state until you approach the threshold in that state. **This is legal and the standard practice for early-stage European SaaS.**
- File Hungarian VAT returns domestically as normal (Stripe provides downloadable tax reports).

**Phase 2: Above €10,000 EU B2C annual cross-border sales**

- Register for **OSS (Union One Stop Shop) via NAV** (Hungary's tax authority).
- Once registered, Stripe Tax will collect the correct per-country VAT rate from each EU B2C customer automatically.
- File quarterly OSS returns via NAV's online portal. Stripe Tax exports the data in the format needed for OSS filing.
- Cost: ~€500-1,500 for an accountant to set up OSS filing; ongoing quarterly returns are straightforward.

**Phase 3: US tax — when approaching $100,000 ARR in a single state**

- Use **TaxJar, Avalara, or Stripe Tax** to monitor economic nexus proximity by state.
- Register in each state as thresholds are approached. Washington ($100k), New York ($500k + 100 transactions), Texas ($500k), California ($500k, and SaaS is often exempt anyway).
- In practice, most SaaS companies at $100k-$500k total ARR are unlikely to have $100k in a single US state. This is a milestone-based concern.

**Alternative: Use Paddle instead of Stripe**

If the team wants to eliminate all tax compliance overhead entirely, **Paddle** acts as Merchant of Record: Paddle owns the customer relationship for tax purposes, handles all VAT/GST/sales tax globally, files in every jurisdiction, and remits on your behalf. You receive net revenue. Cost: **5% + $0.50 per transaction** (vs. Stripe's ~2.9–3.6% + flat depending on configuration).

At $9.99/mo, Paddle costs ~$1.00 per transaction vs. Stripe's ~$0.61. The ~$0.39 premium buys you complete, permanent tax compliance freedom — no accountant, no OSS filing, no US state registrations, ever. For a two-person team, this is worth serious consideration.

### 4.3 Recommended Stack at Launch

| Component | Recommendation | Notes |
|-----------|---------------|-------|
| Payment processor | **Stripe** | Full subscription management, global coverage |
| Subscription billing | **Stripe Billing** (0.7% of volume) | Smart retries, dunning, customer portal, proration |
| Tax automation | **Stripe Tax** (0.5% of volume) | EU VAT + US sales tax, OSS-ready reports |
| EU VAT filing | File Hungarian domestic VAT until OSS threshold; then register OSS with NAV | |
| US sales tax | Do nothing at launch. Monitor nexus by state. Register as thresholds approach. | |
| Accountant | Engage a Hungarian accountant familiar with SaaS VAT | For NAV filings and OSS setup |

**Alternative if tax complexity is a blocker:** Replace Stripe with **Paddle** (Merchant of Record). Accept higher fees (~5% + $0.50) in exchange for zero tax compliance responsibility, forever.

### 4.4 On the Existing Revolut Merchant Integration

The existing partial integration should be abandoned or kept as a fallback payment method (e.g., SEPA direct debit for EU B2B customers who prefer Revolut) but not used as the primary subscription billing infrastructure. The engineering investment required to replicate Stripe Billing's features on Revolut's API is not justified.

---

## Summary

| Question | Answer |
|----------|--------|
| Does Revolut support automatic recurring subscriptions? | Via API yes; managed product UK-only as of 2026 |
| Can a Hungarian company use Revolut for US customers? | Yes, at 2.8% + €0.20; limited tooling |
| Can a Hungarian company use Stripe for US + EU? | Yes, fully supported |
| Revolut EEA card fee | 1.0% + €0.20 |
| Revolut non-EEA (US) card fee | 2.8% + €0.20 |
| Stripe EU card fee | 1.4% + ~€0.25 |
| Stripe US card fee (via EU merchant) | ~2.9% + ~€0.25 (includes intl surcharge) |
| Stripe Billing fee | +0.7% of subscription volume |
| Stripe Tax fee | +0.5% of taxable volume |
| EU VAT OSS threshold | €10,000/yr cross-border B2C |
| Hungary domestic VAT rate on SaaS | 27% |
| EU B2B VAT rule | Reverse charge — no VAT collected |
| US sales tax obligation at launch? | None — below economic nexus in all states |
| US economic nexus (most states) | $100,000/yr in that state |
| US economic nexus (CA/NY/TX) | $500,000/yr |
| SaaS taxable in US states | ~25 states as of 2026 |
| Recommended processor | **Stripe** |
| Minimum viable tax setup | Stripe Tax + Hungarian domestic VAT + OSS when >€10k |
| Alternative: full tax offload | **Paddle** (MoR, 5% + $0.50) |

---

*Sources consulted during research (March 2026):*
- Revolut Developer Docs — Subscriptions API
- Revolut Business: "Subscriptions" launch announcement (FFNews / The Fintech Times, Jan 2026)
- Revolut Business merchant fees help pages (UK, HU)
- Stripe pricing documentation (en-hu)
- Stripe Billing feature documentation
- Stripe Tax documentation
- EU VAT One Stop Shop — European Commission (vat-one-stop-shop.ec.europa.eu)
- Hungary VAT compliance guides (Numeral, Commenda, Quaderno, Anrok)
- US economic nexus state guides (TaxJar, Avalara, TaxCloud, Anrok)
- Paddle pricing and MoR model (paddle.com)
- Practitioner guides: Stefan Bauer (stefanbauer.me), Lukas Hermann (lukashermann.dev)
- Airwallex: Stripe vs. Revolut comparison
- Quaderno: SaaS sales tax guide
- Galvix: International SaaS and US sales tax
