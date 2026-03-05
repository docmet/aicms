# Content Schema Reference

All page content is stored as JSON in the `content_draft` and `content_published` fields
of each `ContentSection`. This document defines the schema for each section type.

## Architecture

Each page has multiple `ContentSection` records, each with:
- `section_type`: string identifier (e.g., `"hero"`, `"features"`)
- `content_draft`: JSON string — what the user/AI is editing
- `content_published`: JSON string — what the public site shows
- `order`: integer — display order on the page

The `content_draft` is always what gets edited. Use the **Publish** action (or `publish_page`
MCP tool) to push draft → published.

---

## Section Types

### `hero`

The main headline section, typically the first thing visitors see.

```json
{
  "headline": "We help small businesses grow online",
  "subheadline": "Beautiful websites, managed by your AI assistant. No coding needed.",
  "badge": "Now in public beta",
  "cta_primary": {
    "label": "Get started free",
    "href": "/register"
  },
  "cta_secondary": {
    "label": "See a demo",
    "href": "#demo"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | Yes | Main headline, shown in large bold type |
| `subheadline` | No | Supporting text below headline |
| `badge` | No | Small chip/tag above headline (e.g., "New", "Beta") |
| `cta_primary` | No | Primary call-to-action button |
| `cta_primary.label` | Yes (if cta_primary) | Button text |
| `cta_primary.href` | No | Button URL (default: `/register`) |
| `cta_secondary` | No | Secondary/outline button |

---

### `features`

Grid of features or services, with icon, title, and description per item.

```json
{
  "headline": "Everything you need",
  "subheadline": "Built for small businesses who want a professional web presence.",
  "items": [
    {
      "icon": "✨",
      "title": "AI-powered editing",
      "description": "Talk to Claude or ChatGPT to update your site content."
    },
    {
      "icon": "🎨",
      "title": "Beautiful themes",
      "description": "5 professionally designed themes, all mobile-responsive."
    },
    {
      "icon": "🚀",
      "title": "Instant publish",
      "description": "Preview your changes live before publishing to the world."
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | No | Section headline above the grid |
| `subheadline` | No | Section subtext |
| `items` | Yes | Array of feature cards (min 1) |
| `items[].icon` | No | Emoji icon (displayed in colored circle) |
| `items[].title` | Yes | Feature title |
| `items[].description` | Yes | Feature description |

---

### `testimonials`

Social proof section with customer quotes.

```json
{
  "headline": "Loved by small businesses",
  "items": [
    {
      "quote": "I updated my entire website in 10 minutes just by chatting with Claude. Amazing.",
      "name": "Sarah Chen",
      "role": "Owner",
      "company": "Bloom Florist"
    },
    {
      "quote": "Finally, a website I can actually maintain without calling my nephew.",
      "name": "Mike Torres",
      "role": "Chef & Owner",
      "company": "Torres Kitchen"
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | No | Section headline |
| `items` | Yes | Array of testimonials |
| `items[].quote` | Yes | The testimonial text |
| `items[].name` | Yes | Reviewer name |
| `items[].role` | No | Job title or role |
| `items[].company` | No | Company or business name |

---

### `about`

About section with text and optional stats row.

```json
{
  "headline": "We're passionate about local business",
  "body": "Founded in 2024, we've been helping small business owners build beautiful websites without any technical knowledge. Our AI-first approach means you can update your site in seconds by just having a conversation.",
  "stats": [
    { "number": "500+", "label": "Sites built" },
    { "number": "10 min", "label": "Average setup" },
    { "number": "99%", "label": "Uptime" }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | Yes | Section headline |
| `body` | Yes | Main body text (plain text, no HTML) |
| `stats` | No | Array of stat cards (shown in a row below body) |
| `stats[].number` | Yes | The big number/stat (e.g., "500+") |
| `stats[].label` | Yes | Stat label (e.g., "Sites built") |

---

### `contact`

Contact information section.

```json
{
  "headline": "Get in touch",
  "email": "hello@mybusiness.com",
  "phone": "+1 (555) 123-4567",
  "address": "123 Main Street, Budapest, Hungary",
  "hours": "Mon-Fri: 9am-5pm CET"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | No | Section headline |
| `email` | No | Contact email (shown as mailto link) |
| `phone` | No | Phone number (shown as tel link) |
| `address` | No | Physical address |
| `hours` | No | Business hours |

At least one of email, phone, address, or hours should be provided.

---

### `cta`

A bold call-to-action banner, typically near the bottom of the page.

```json
{
  "headline": "Ready to get your AI-powered website?",
  "subheadline": "Join 500+ businesses who edit their sites by chatting with AI.",
  "button_label": "Start for free",
  "button_href": "/register"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | Yes | Big, bold headline |
| `subheadline` | No | Supporting text |
| `button_label` | Yes | CTA button text |
| `button_href` | No | Button URL (default: `/register`) |

---

### `pricing`

Pricing plans comparison section.

```json
{
  "headline": "Simple, transparent pricing",
  "plans": [
    {
      "name": "Free",
      "price": "0",
      "period": "forever",
      "features": [
        "1 site",
        "Subdomain hosting",
        "All themes",
        "MCP AI editing",
        "Previous version rollback"
      ],
      "cta_label": "Get started",
      "cta_href": "/register"
    },
    {
      "name": "Pro",
      "price": "12",
      "period": "month",
      "features": [
        "Unlimited sites",
        "Custom domain",
        "All themes",
        "MCP AI editing",
        "Last 5 versions rollback",
        "Priority support"
      ],
      "cta_label": "Start Pro",
      "cta_href": "/register?plan=pro",
      "is_featured": true
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `headline` | No | Section headline |
| `plans` | Yes | Array of plans (2-3 recommended) |
| `plans[].name` | Yes | Plan name |
| `plans[].price` | Yes | Price number as string (e.g., "12") |
| `plans[].period` | No | Period label (e.g., "month", "year", "forever") |
| `plans[].features` | Yes | List of included features |
| `plans[].cta_label` | Yes | Button text |
| `plans[].cta_href` | No | Button URL |
| `plans[].is_featured` | No | Highlights this plan (popular/recommended badge) |

---

### `custom`

Fallback for any section type. Used when AI invents a new section type, or for freeform content.
The renderer will display this cleanly with a section title and content text.

```json
{
  "title": "Our Story",
  "content": "Started in a tiny apartment in Budapest in 2024..."
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `title` | No | Section title |
| `content` | Yes | Plain text or simple markdown content |

**Any unknown section type** will be rendered using the `custom` layout.
This means AI can freely create new section types without breaking anything.

---

## For AI Tools

When using `update_page_content`, always pass structured JSON matching the schema above.

**Examples:**

```
# Update hero section
update_page_content(
  site_id="...",
  page_id="...",
  section_type="hero",
  content='{"headline": "Welcome to Bloom Florist", "subheadline": "Fresh flowers for every occasion", "cta_primary": {"label": "Shop now", "href": "#contact"}}'
)

# Update features section
update_page_content(
  site_id="...",
  page_id="...",
  section_type="features",
  content='{"headline": "Why choose us", "items": [{"icon": "🌸", "title": "Fresh daily", "description": "We source flowers every morning from local growers."}, {"icon": "🚚", "title": "Free delivery", "description": "Free local delivery on orders over 20€."}]}'
)
```

Use `describe_site` to see what sections exist and their current content before editing.
Use `generate_section` to get a pre-filled template for any section type.

---

## Storage Notes

- Content is stored as a JSON string in the `content_draft` / `content_published` text columns
- Plain text (non-JSON) is still accepted and rendered via the `custom` fallback
- Section types not listed above use the `custom` renderer automatically
- Maximum section content size: 64KB (enforced at API level)
