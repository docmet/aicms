"""Add partial unique index on pages(site_id, slug) for active pages only.

Revision ID: 20260307_0600
Revises: 20260307_0500
Create Date: 2026-03-07 06:00:00.000000
"""

from sqlalchemy import text

from alembic import op

revision = "20260307_0600"
down_revision = "20260307_0500"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Partial unique index — only enforces uniqueness for non-deleted pages.
    # This allows re-creation of a slug after soft-deletion (is_deleted=True rows
    # are excluded from the constraint by the WHERE clause).
    op.create_index(
        "uq_pages_site_slug_active",
        "pages",
        ["site_id", "slug"],
        unique=True,
        postgresql_where=text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index("uq_pages_site_slug_active", table_name="pages")
