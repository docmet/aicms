"""Database seed script.

Creates demo data for development:
  - norbi@docmet.com (admin)
  - client@docmet.com (standard user)
  - 5 themes (modern, warm, startup, minimal, dark)
  - Demo site "Brew & Bean Coffee" with a full landing page
    Sections: hero, features, testimonials, about, cta, pricing, contact

All section content is set in both content_draft and content_published
(simulating a page that has been published once already).
"""

import asyncio
import json
import os
import sys
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import AsyncSessionLocal
from src.models import ContentSection, Page, Site, Theme, User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ── Demo content ──────────────────────────────────────────────────────────────

DEMO_SECTIONS = [
    (
        "hero",
        json.dumps({
            "headline": "Specialty Coffee & Fresh-Roasted Beans",
            "subheadline": "Enjoy specialty coffee, fresh-roasted beans, espresso drinks, and pastries served by expert baristas in the heart of downtown.",
            "badge": "Now open 7 days a week",
            "cta_primary": {"label": "See Our Menu", "href": "#menu"},
            "cta_secondary": {"label": "Our Story", "href": "#about"},
        }),
        0,
    ),
    (
        "features",
        json.dumps({
            "headline": "Why Coffee Lovers Choose Us",
            "subheadline": "From farm to cup, we carefully source, roast, and brew every coffee bean for exceptional flavor.",
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
            "items": [
                {
                    "quote": "Best flat white in the city. I come here every single morning before work. The staff knows my order by heart.",
                    "name": "Sarah M.",
                    "role": "Product Designer",
                    "company": "Acme Corp",
                },
                {
                    "quote": "I've been a coffee snob for 15 years. Brew & Bean is one of the few places that actually impresses me.",
                    "name": "James T.",
                    "role": "Coffee Enthusiast",
                },
                {
                    "quote": "We hold all our team meetings here. The atmosphere is perfect and the pastries are incredible.",
                    "name": "Priya K.",
                    "role": "Startup Founder",
                    "company": "LaunchPad",
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
            "headline": "Find Us",
            "email": "hello@brewandbean.co",
            "phone": "+1 (555) 234-5678",
            "address": "42 Maple Street, Downtown, CA 94103",
            "hours": "Mon–Fri 7am–7pm · Sat–Sun 9am–5pm",
        }),
        6,
    ),
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
            print("Demo site already exists, skipping...")
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

        # ── Landing page ───────────────────────────────────────────────────────
        result = await session.execute(
            select(Page).where(Page.site_id == demo_site.id, Page.slug == "home")
        )
        landing_page = result.scalar_one_or_none()
        if landing_page:
            print("Landing page already exists, skipping...")
        else:
            landing_page = Page(
                id=uuid4(),
                site_id=demo_site.id,
                title="Home",
                slug="home",
                is_published=True,
                order=0,
            )
            session.add(landing_page)
            await session.flush()
            print(f"Landing page created: {landing_page.title}")

        # ── Content sections ───────────────────────────────────────────────────
        for section_type, content, order in DEMO_SECTIONS:
            result = await session.execute(
                select(ContentSection).where(
                    ContentSection.page_id == landing_page.id,
                    ContentSection.section_type == section_type,
                )
            )
            if result.scalar_one_or_none():
                print(f"Section already exists: {section_type}")
                continue

            session.add(ContentSection(
                id=uuid4(),
                page_id=landing_page.id,
                section_type=section_type,
                content_draft=content,
                content_published=content,  # Already "published" in seed
                order=order,
            ))
            print(f"Section created: {section_type}")

        await session.commit()
        print("Database seeding completed!")
        print("  Demo site: http://localhost:3000/demo-site")
        print("  Admin user: norbi@docmet.com / password123")
        print("  Client user: client@docmet.com / password123")


if __name__ == "__main__":
    asyncio.run(seed_database())
