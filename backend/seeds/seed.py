"""Database seed script.

Creates demo data for development:
  - norbi@docmet.com (admin)
  - client@docmet.com (standard user)
  - 5 themes (modern, warm, startup, minimal, dark)
  - Demo site "Brew & Bean Coffee" with two pages:
      Home: hero, features, testimonials, about, pricing, cta, contact
      Menu: custom (markdown rich text)
  - 2 blog posts

All section content is set in both content_draft and content_published
(simulating a page that has been published once already).
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import AsyncSessionLocal
from src.models import ContentSection, Page, Site, Theme, User
from src.models.blog import BlogPost

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ── Demo content ──────────────────────────────────────────────────────────────
# All Unsplash images use fixed IDs (no random/API key needed)

HERO_BG = "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1600&q=80"
ABOUT_IMG = "https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=800&q=80"
AVATAR_SARAH = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80"
AVATAR_JAMES = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80"
AVATAR_PRIYA = "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&q=80"

HOME_SECTIONS = [
    (
        "hero",
        json.dumps({
            "headline": "Specialty Coffee & Fresh-Roasted Beans",
            "subheadline": "Enjoy specialty coffee, fresh-roasted beans, espresso drinks, and pastries served by expert baristas in the heart of downtown.",
            "badge": "Now open 7 days a week",
            "cta_primary": {"label": "See Our Menu", "href": "/demo-site/menu"},
            "cta_secondary": {"label": "Our Story", "href": "#about"},
            "background_image": HERO_BG,
            "layout": "centered",
        }),
        0,
    ),
    (
        "features",
        json.dumps({
            "headline": "Why Coffee Lovers Choose Us",
            "subheadline": "From farm to cup, we carefully source, roast, and brew every coffee bean for exceptional flavor.",
            "layout": "grid-3",
            "background": "default",
            "items": [
                {
                    "icon": "☕",
                    "title": "Single-Origin Specialty Beans",
                    "description": "We source specialty-grade coffee beans directly from farms in Ethiopia, Colombia, and Guatemala to ensure exceptional flavor and ethical sourcing.",
                },
                {
                    "icon": "🔥",
                    "title": "Fresh Coffee Roasted Daily",
                    "description": "Our beans are roasted fresh every morning so your espresso, cappuccino, or latte is brewed from coffee roasted hours ago.",
                },
                {
                    "icon": "🌱",
                    "title": "Sustainably Sourced Coffee",
                    "description": "We partner with ethical farms and fair-trade producers to support sustainable coffee growing and better farmer livelihoods.",
                },
                {
                    "icon": "🎓",
                    "title": "Expert Coffee Baristas",
                    "description": "Our baristas train extensively in espresso extraction, milk steaming, and coffee brewing to deliver consistently excellent drinks.",
                },
            ],
        }),
        1,
    ),
    (
        "testimonials",
        json.dumps({
            "headline": "What Our Regulars Say",
            "layout": "cards",
            "background": "gray",
            "items": [
                {
                    "quote": "Best flat white in the city. I come here every single morning before work. The staff knows my order by heart.",
                    "name": "Sarah M.",
                    "role": "Product Designer",
                    "company": "Acme Corp",
                    "avatar_url": AVATAR_SARAH,
                },
                {
                    "quote": "I've been a coffee snob for 15 years. Brew & Bean is one of the few places that actually impresses me.",
                    "name": "James T.",
                    "role": "Coffee Enthusiast",
                    "avatar_url": AVATAR_JAMES,
                },
                {
                    "quote": "We hold all our team meetings here. The atmosphere is perfect and the pastries are incredible.",
                    "name": "Priya K.",
                    "role": "Startup Founder",
                    "company": "LaunchPad",
                    "avatar_url": AVATAR_PRIYA,
                },
            ],
        }),
        2,
    ),
    (
        "about",
        json.dumps({
            "headline": "Started With a Dream and a French Press",
            "body": "Brew & Bean was founded in 2019 by Marco and Elena, two coffee obsessives who left their corporate jobs to do something they actually loved. We started at the local farmers market with a cart, a grinder, and an embarrassing amount of passion. Three years later we opened our first shop — and we haven't looked back.",
            "layout": "image-right",
            "image_url": ABOUT_IMG,
            "stats": [
                {"number": "5+", "label": "Years in business"},
                {"number": "12,000+", "label": "Happy regulars"},
                {"number": "8", "label": "Origin countries"},
            ],
        }),
        3,
    ),
    (
        "pricing",
        json.dumps({
            "headline": "Simple, Honest Pricing",
            "subheadline": "No subscriptions. No hidden fees. Just great coffee.",
            "plans": [
                {
                    "name": "Espresso Bar",
                    "price": "$4–6",
                    "period": " per drink",
                    "features": [
                        "Single & double espresso",
                        "Flat white & cortado",
                        "Cappuccino & latte",
                        "Seasonal specials",
                    ],
                    "cta_label": "View Menu",
                    "highlighted": False,
                },
                {
                    "name": "Monthly Subscription",
                    "price": "$59",
                    "period": "/month",
                    "features": [
                        "250g freshly-roasted beans",
                        "Choose your roast level",
                        "Free shipping",
                        "Subscriber-only blends",
                        "10% off in-store",
                    ],
                    "cta_label": "Subscribe",
                    "highlighted": True,
                },
                {
                    "name": "Wholesale",
                    "price": "Custom",
                    "period": "",
                    "features": [
                        "Minimum 5kg/month",
                        "Custom label available",
                        "Dedicated account manager",
                        "Tasting sessions included",
                    ],
                    "cta_label": "Get in Touch",
                    "highlighted": False,
                },
            ],
        }),
        4,
    ),
    (
        "cta",
        json.dumps({
            "headline": "Visit Our Downtown Coffee Shop Today",
            "subheadline": "Stop by for fresh-roasted specialty coffee, espresso drinks, and pastries. Open daily from 7am–7pm.",
            "button_label": "Get Directions",
            "button_href": "https://maps.google.com",
        }),
        5,
    ),
    (
        "contact",
        json.dumps({
            "headline": "Find Us or Say Hello",
            "email": "hello@brewandbean.co",
            "phone": "+1 (555) 234-5678",
            "address": "42 Maple Street, Downtown, CA 94103",
            "hours": "Mon–Fri 7am–7pm · Sat–Sun 9am–5pm",
            "show_form": True,
        }),
        6,
    ),
]

MENU_CONTENT = """## Espresso Drinks

### Classic Espresso
Single or double shot of our house blend, pulled to 9 bar precision.
**From $3.50**

### Flat White
Double ristretto with silky steamed whole milk. Melbourne-style.
**$5.00**

### Cappuccino
Equal parts espresso, steamed milk, and velvety microfoam.
**$4.75**

### Oat Latte
Our most popular. Double espresso with oat milk, lightly sweetened.
**$5.50**

---

## Filter & Brew Bar

### Pour Over (V60)
Single-origin, brewed to order. Ask your barista what's on the rotation today.
**$6.00**

### Cold Brew
Steeped 18 hours. Smooth, low-acid, seriously refreshing.
**$5.50**

### Batch Brew
Classic drip coffee, freshly brewed every 30 minutes.
**$3.00**

---

## Food

### Almond Croissant
Flaky, buttery, filled with almond cream. Baked in-house daily.
**$4.50**

### Avocado Toast
Sourdough, smashed avocado, chili flakes, lemon. Add a poached egg +$2.
**$9.00**

### Seasonal Fruit Bowl
Rotating selection of fresh seasonal fruit with Greek yoghurt and granola.
**$7.50**

---

## Beans to Take Home

All beans are roasted within 48 hours of your purchase.

| Origin | Process | Tasting Notes | Price |
|---|---|---|---|
| Ethiopia Yirgacheffe | Washed | Blueberry, jasmine, citrus | $22 / 250g |
| Colombia Huila | Natural | Dark chocolate, caramel | $20 / 250g |
| Guatemala Antigua | Honey | Brown sugar, almond, plum | $19 / 250g |
| House Blend | Espresso | Hazelnut, dark chocolate | $18 / 250g |
"""

MENU_SECTIONS = [
    (
        "hero",
        json.dumps({
            "headline": "Our Menu",
            "subheadline": "Seasonal drinks, fresh food, and beans to take home. Everything made with care.",
            "badge": "Updated seasonally",
            "background_image": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=1600&q=80",
            "layout": "centered",
        }),
        0,
    ),
    (
        "custom",
        json.dumps({
            "title": "Full Menu",
            "body": MENU_CONTENT,
            "render_mode": "markdown",
        }),
        1,
    ),
]

BLOG_POSTS = [
    {
        "slug": "how-we-source-our-beans",
        "title": "How We Source Our Beans: A Direct Trade Story",
        "excerpt": "Every bag of Brew & Bean coffee starts with a relationship. Here's how we find the world's best farmers.",
        "body": """When most people think about coffee, they think about the cup. We think about the farm.

Three years ago, Marco flew to the Yirgacheffe region of Ethiopia with a notebook, a cupping kit, and zero expectation of what he'd find. He came back with a relationship with a third-generation farmer named Tadesse — and a 200kg commitment that changed how we source everything.

## What Direct Trade Actually Means

"Direct trade" gets thrown around a lot in specialty coffee. For us it means one thing: we know the farmer's name, we've visited the farm, and we pay above fair-trade floor price — always.

Our current partner farms:

- **Tadesse Bekele** — Yirgacheffe, Ethiopia (washed & natural process)
- **Familia Perez** — Huila, Colombia (washed)
- **Finca La Hermosa** — Antigua, Guatemala (honey process)

## Why It Matters in the Cup

Direct relationships mean we can request specific harvest lots, processing methods, and even drying times. This level of control is why our Ethiopia Yirgacheffe has those distinctive blueberry notes — Tadesse dries the cherries on raised beds in the shade, a process that takes 3 weeks longer but produces an extraordinarily clean, fruity cup.

Next time you taste something unexpected in your coffee, that's not an accident. It's the result of a conversation that happened on a hillside 8,000 miles away.

Come in and ask us about our current rotation. We love talking about this stuff.
""",
        "author_name": "Marco Rossi",
        "cover_image_url": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1200&q=80",
        "tags": ["sourcing", "direct trade", "ethiopia"],
        "published_at": datetime(2026, 2, 14, 9, 0, tzinfo=UTC),
    },
    {
        "slug": "perfect-home-espresso",
        "title": "5 Things You're Getting Wrong With Your Home Espresso",
        "excerpt": "Home espresso machines are better than ever. Here's how to stop wasting good beans.",
        "body": """You spent $600 on a machine. You bought our best beans. Your espresso still tastes like battery acid. We hear this all the time. Here's what's usually going wrong.

## 1. Your Grind Is Wrong

This is the biggest one. Pre-ground coffee is dead coffee. Espresso demands a very fine, consistent grind, and that grind needs to be dialed in for your specific machine on that specific day. Humidity, bean age, and temperature all affect the right setting.

**Fix:** Buy a burr grinder. Entry-level Baratza or Eureka Mignon. Nothing else matters if your grind is wrong.

## 2. You're Using Too Much (or Too Little) Coffee

The standard for a double espresso is 18–20g of ground coffee yielding 36–40g of liquid in 25–30 seconds. Most home baristas eyeball this and wonder why every shot tastes different.

**Fix:** Get a small scale. Weigh your dose. Every. Single. Time.

## 3. Your Machine Isn't Hot Enough

Most entry-level machines take 15–20 minutes to fully stabilize, not the 2 minutes the manual claims. Pull a blank shot through the portafilter first to purge cold water and heat the basket.

**Fix:** Turn on your machine 20 minutes before you plan to pull a shot.

## 4. Your Milk Steaming Technique

Flat whites and lattes require microfoam — tiny bubbles incorporated into the milk, not a thick foam cap floating on top. The tip of the steam wand should be just below the surface, and you should hear a gentle hissing, not a loud gurgle.

**Fix:** Watch 10 minutes of YouTube tutorials on milk steaming. Practice with cheap milk before using the fancy stuff.

## 5. You're Using Old Beans

Espresso is best 7–21 days after roast. Too fresh and CO2 causes channeling and sourness. Too old and you'll taste cardboard.

**Fix:** Buy beans from us. Check the roast date on the bag. We print it on every bag.

Come in for a tasting — we run free espresso workshops the last Saturday of every month.
""",
        "author_name": "Elena Vasquez",
        "cover_image_url": "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=1200&q=80",
        "tags": ["tips", "home espresso", "brewing"],
        "published_at": datetime(2026, 2, 28, 10, 30, tzinfo=UTC),
    },
]


async def seed_database() -> None:
    """Seed the database with initial data."""
    print("Starting database seeding...")

    async with AsyncSessionLocal() as session:
        # ── Users ──────────────────────────────────────────────────────────────
        result = await session.execute(
            select(User).where(User.email == "norbi@docmet.com")
        )
        admin_user = result.scalar_one_or_none()
        if admin_user:
            print("Admin user already exists, skipping...")
        else:
            admin_user = User(
                id=uuid4(),
                email="norbi@docmet.com",
                password_hash=await hash_password("password123"),
                is_admin=True,
                email_verified=True,
                plan="agency",
            )
            session.add(admin_user)
            await session.flush()
            print(f"Admin user created: {admin_user.email}")

        result = await session.execute(
            select(User).where(User.email == "client@docmet.com")
        )
        client_user = result.scalar_one_or_none()
        if client_user:
            print("Client user already exists, skipping...")
        else:
            client_user = User(
                id=uuid4(),
                email="client@docmet.com",
                password_hash=await hash_password("password123"),
                is_admin=False,
                email_verified=True,
                plan="pro",
            )
            session.add(client_user)
            await session.flush()
            print(f"Client user created: {client_user.email}")

        # ── Themes ─────────────────────────────────────────────────────────────
        themes_data = [
            ("Modern Blue", "modern", {"primary": "#3b82f6", "accent": "#1d4ed8"}),
            ("Warm Amber", "warm", {"primary": "#f97316", "accent": "#c2410c"}),
            ("Startup Green", "startup", {"primary": "#10b981", "accent": "#065f46"}),
            ("Minimal Zinc", "minimal", {"primary": "#71717a", "accent": "#27272a"}),
            ("Dark Mode", "dark", {"primary": "#a78bfa", "accent": "#7c3aed"}),
        ]

        for name, slug, config in themes_data:
            result = await session.execute(select(Theme).where(Theme.slug == slug))
            if not result.scalar_one_or_none():
                session.add(Theme(id=uuid4(), name=name, slug=slug, config=config))
                print(f"Theme created: {name} ({slug})")
            else:
                print(f"Theme already exists: {name} ({slug})")

        # ── Demo site ──────────────────────────────────────────────────────────
        result = await session.execute(
            select(Site).where(Site.user_id == client_user.id, Site.slug == "demo-site")
        )
        demo_site = result.scalar_one_or_none()
        if demo_site:
            print("Demo site already exists, skipping site creation...")
        else:
            demo_site = Site(
                id=uuid4(),
                user_id=client_user.id,
                slug="demo-site",
                name="Brew & Bean Coffee",
                theme_slug="warm",
            )
            session.add(demo_site)
            await session.flush()
            print(f"Demo site created: {demo_site.name}")

        # ── Home page ──────────────────────────────────────────────────────────
        result = await session.execute(
            select(Page).where(Page.site_id == demo_site.id, Page.slug == "home")
        )
        home_page = result.scalar_one_or_none()
        if home_page:
            print("Home page already exists, skipping...")
        else:
            home_page = Page(
                id=uuid4(),
                site_id=demo_site.id,
                title="Home",
                slug="home",
                is_published=True,
                order=0,
            )
            session.add(home_page)
            await session.flush()
            print(f"Home page created: {home_page.title}")

        for section_type, content, order in HOME_SECTIONS:
            result = await session.execute(
                select(ContentSection).where(
                    ContentSection.page_id == home_page.id,
                    ContentSection.section_type == section_type,
                )
            )
            if result.scalar_one_or_none():
                print(f"  Section already exists: {section_type}")
                continue
            session.add(ContentSection(
                id=uuid4(),
                page_id=home_page.id,
                section_type=section_type,
                content_draft=content,
                content_published=content,
                order=order,
            ))
            print(f"  Section created: {section_type}")

        # ── Menu page ──────────────────────────────────────────────────────────
        result = await session.execute(
            select(Page).where(Page.site_id == demo_site.id, Page.slug == "menu")
        )
        menu_page = result.scalar_one_or_none()
        if menu_page:
            print("Menu page already exists, skipping...")
        else:
            menu_page = Page(
                id=uuid4(),
                site_id=demo_site.id,
                title="Menu",
                slug="menu",
                is_published=True,
                order=1,
            )
            session.add(menu_page)
            await session.flush()
            print(f"Menu page created: {menu_page.title}")

        for section_type, content, order in MENU_SECTIONS:
            result = await session.execute(
                select(ContentSection).where(
                    ContentSection.page_id == menu_page.id,
                    ContentSection.section_type == section_type,
                )
            )
            if result.scalar_one_or_none():
                print(f"  Menu section already exists: {section_type}")
                continue
            session.add(ContentSection(
                id=uuid4(),
                page_id=menu_page.id,
                section_type=section_type,
                content_draft=content,
                content_published=content,
                order=order,
            ))
            print(f"  Menu section created: {section_type}")

        # ── Blog posts ─────────────────────────────────────────────────────────
        for post_data in BLOG_POSTS:
            result = await session.execute(
                select(BlogPost).where(
                    BlogPost.site_id == demo_site.id,
                    BlogPost.slug == post_data["slug"],
                )
            )
            if result.scalar_one_or_none():
                print(f"Blog post already exists: {post_data['slug']}")
                continue
            session.add(BlogPost(
                id=uuid4(),
                site_id=demo_site.id,
                slug=post_data["slug"],
                title=post_data["title"],
                excerpt=post_data["excerpt"],
                body=post_data["body"],
                author_name=post_data["author_name"],
                cover_image_url=post_data["cover_image_url"],
                tags=post_data["tags"],
                published_at=post_data["published_at"],
            ))
            print(f"Blog post created: {post_data['title']}")

        await session.commit()
        print("\nDatabase seeding completed!")
        print("  Demo site:   http://localhost:3000/demo-site")
        print("  Menu page:   http://localhost:3000/demo-site/menu")
        print("  Blog:        http://localhost:3000/demo-site/blog")
        print("  Admin:       http://localhost:3000/dashboard")
        print("  Admin user:  norbi@docmet.com / password123")
        print("  Client user: client@docmet.com / password123")


if __name__ == "__main__":
    asyncio.run(seed_database())
