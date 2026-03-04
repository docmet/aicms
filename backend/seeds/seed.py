"""Database seed script."""

import asyncio
import os

# Import after database setup
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


async def seed_database() -> None:
    """Seed the database with initial data."""
    print("🌱 Starting database seeding...")

    async with AsyncSessionLocal() as session:
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.email == "norbi@docmet.com")
        )
        admin_exists = result.scalar_one_or_none()

        if admin_exists:
            print("✅ Admin user already exists, skipping...")
            admin_user = admin_exists
        else:
            # Create admin user
            admin_user = User(
                id=uuid4(),
                email="norbi@docmet.com",
                password_hash=await hash_password("password123"),
                is_admin=True,
            )
            session.add(admin_user)
            await session.flush()
            print(f"✅ Admin user created: {admin_user.email}")

        # Check if client user already exists
        result = await session.execute(
            select(User).where(User.email == "client@docmet.com")
        )
        client_exists = result.scalar_one_or_none()

        if client_exists:
            print("✅ Client user already exists, skipping...")
            client_user = client_exists
        else:
            # Create client user
            client_user = User(
                id=uuid4(),
                email="client@docmet.com",
                password_hash=await hash_password("password123"),
                is_admin=False,
            )
            session.add(client_user)
            await session.flush()
            print(f"✅ Client user created: {client_user.email}")

        # Create themes
        themes_data = [
            ("Default Blue", "default", {"primary": "#3b82f6"}),
            ("Warm Orange", "warm", {"primary": "#f97316"}),
            ("Nature Green", "nature", {"primary": "#22c55e"}),
            ("Dark Mode", "dark", {"primary": "#cbd5e1"}),
            ("Minimal Black", "minimal", {"primary": "#71717a"}),
        ]

        for name, slug, config in themes_data:
            result = await session.execute(select(Theme).where(Theme.slug == slug))
            theme_exists = result.scalar_one_or_none()

            if not theme_exists:
                theme = Theme(
                    id=uuid4(),
                    name=name,
                    slug=slug,
                    config=config,
                )
                session.add(theme)
                print(f"✅ Theme created: {name} ({slug})")
            else:
                print(f"✅ Theme already exists: {name} ({slug})")

        # Create demo site for client user
        result = await session.execute(
            select(Site).where(Site.user_id == client_user.id)
        )
        site_exists = result.scalar_one_or_none()

        if site_exists:
            print("✅ Demo site already exists, skipping...")
            demo_site = site_exists
        else:
            demo_site = Site(
                id=uuid4(),
                user_id=client_user.id,
                slug="demo-site",
                name="Demo Site",
                theme_slug="default",
            )
            session.add(demo_site)
            await session.flush()
            print(f"✅ Demo site created: {demo_site.name}")

        # Create landing page for demo site
        result = await session.execute(select(Page).where(Page.site_id == demo_site.id))
        page_exists = result.scalar_one_or_none()

        if page_exists:
            print("✅ Landing page already exists, skipping...")
            landing_page = page_exists
        else:
            landing_page = Page(
                id=uuid4(),
                site_id=demo_site.id,
                title="Welcome",
                slug="welcome",
                is_published=True,
                order=0,
            )
            session.add(landing_page)
            await session.flush()
            print(f"✅ Landing page created: {landing_page.title}")

        # Create content sections for landing page
        content_sections_data = [
            (
                "hero",
                '{"headline": "Welcome to My Site", "subheadline": "A beautiful landing page"}',
                0,
            ),
            ("about", "This is a demo site showcasing the AI CMS platform.", 1),
            (
                "services",
                '{"services": [{"name": "Web Design", "description": "Beautiful designs"}, {"name": "Development", "description": "Modern technologies"}]}',
                2,
            ),
            (
                "contact",
                '{"email": "contact@example.com", "phone": "+1 234 567 890"}',
                3,
            ),
        ]

        for section_type, content, order in content_sections_data:
            result = await session.execute(
                select(ContentSection).where(
                    ContentSection.page_id == landing_page.id,
                    ContentSection.section_type == section_type,
                )
            )
            section_exists = result.scalar_one_or_none()

            if not section_exists:
                section = ContentSection(
                    id=uuid4(),
                    page_id=landing_page.id,
                    section_type=section_type,
                    content=content,
                    order=order,
                )
                session.add(section)
                print(f"✅ Content section created: {section_type}")
            else:
                print(f"✅ Content section already exists: {section_type}")

        await session.commit()
        print("✅ Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
