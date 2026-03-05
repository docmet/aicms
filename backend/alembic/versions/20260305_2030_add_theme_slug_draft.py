"""Add theme_slug_draft column to sites table.

Revision ID: 20260305_2030_add_theme_slug_draft
Revises: 20260305_1800_add_user_plan
Create Date: 2026-03-05

theme_slug_draft holds a pending theme change from MCP or the admin editor.
NULL means no pending change (live theme = theme_slug).
On publish, theme_slug_draft is copied to theme_slug and cleared.
"""

import sqlalchemy as sa

from alembic import op

revision = "20260305_2030_add_theme_slug_draft"
down_revision = "20260305_1800_add_user_plan"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sites",
        sa.Column("theme_slug_draft", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sites", "theme_slug_draft")
