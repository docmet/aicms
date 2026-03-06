"""add form_submissions table

Revision ID: 20260307_0200
Revises: 20260307_0100
Create Date: 2026-03-07 02:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "20260307_0200"
down_revision = "20260307_0100"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "form_submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "site_id",
            UUID(as_uuid=True),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_form_submissions_site_id", "form_submissions", ["site_id"])
    op.create_index("ix_form_submissions_created_at", "form_submissions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_form_submissions_created_at", table_name="form_submissions")
    op.drop_index("ix_form_submissions_site_id", table_name="form_submissions")
    op.drop_table("form_submissions")
