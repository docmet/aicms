"""Required data seed — runs automatically on every deploy via start.sh.

Idempotent: safe to run repeatedly. Add new required records here and they
will be applied on the next deployment.

Do NOT add test users or demo content here — use seeds/seed.py for that.
"""

import asyncio
import os
import sys
from uuid import uuid4

from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import AsyncSessionLocal
from src.models import Theme

# ── Required themes ───────────────────────────────────────────────────────────
# Add / update theme definitions here. Existing themes are matched by slug.
# Changes to config/name will be applied on the next deploy.

THEMES = [
    ("Modern Blue",  "modern",  {"primary": "#3b82f6", "accent": "#1d4ed8"}),
    ("Warm Amber",   "warm",    {"primary": "#f97316", "accent": "#c2410c"}),
    ("Startup Green","startup", {"primary": "#10b981", "accent": "#065f46"}),
    ("Minimal Zinc", "minimal", {"primary": "#71717a", "accent": "#27272a"}),
    ("Dark Mode",    "dark",    {"primary": "#a78bfa", "accent": "#7c3aed"}),
]


async def seed_required() -> None:
    print("[seed] Seeding required data...")

    async with AsyncSessionLocal() as session:
        for name, slug, config in THEMES:
            result = await session.execute(select(Theme).where(Theme.slug == slug))
            theme = result.scalar_one_or_none()
            if theme:
                # Update in case config or name changed
                theme.name = name
                theme.config = config
                print(f"[seed] Theme updated: {slug}")
            else:
                session.add(Theme(id=uuid4(), name=name, slug=slug, config=config))
                print(f"[seed] Theme created: {slug}")

        await session.commit()

    print("[seed] Required data seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_required())
