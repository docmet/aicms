"""Add page_views table for privacy-first analytics.

Revision ID: 20260307_0300
Revises: 20260307_0200
Create Date: 2026-03-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260307_0300"
down_revision: str | None = "20260307_0200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "page_views",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_path", sa.String(500), nullable=False),
        sa.Column("referrer", sa.String(500), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_page_views_site_id", "page_views", ["site_id"])
    op.create_index("ix_page_views_created_at", "page_views", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_page_views_created_at", "page_views")
    op.drop_index("ix_page_views_site_id", "page_views")
    op.drop_table("page_views")
