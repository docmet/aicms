"""Add scheduled_at to pages for scheduled publishing.

Revision ID: 20260307_0500
Revises: 20260307_0400
Create Date: 2026-03-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260307_0500"
down_revision: str | None = "20260307_0400"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "pages",
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_pages_scheduled_at", "pages", ["scheduled_at"])


def downgrade() -> None:
    op.drop_index("ix_pages_scheduled_at", "pages")
    op.drop_column("pages", "scheduled_at")
