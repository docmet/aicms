"""Add wordpress_sites table.

Revision ID: 20260307_0800
Revises: 20260307_0700
Create Date: 2026-03-07 08:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260307_0800"
down_revision = "20260307_0700"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wordpress_sites",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("site_url", sa.String(500), nullable=False),
        sa.Column("app_username", sa.String(255), nullable=False),
        sa.Column("app_password_encrypted", sa.String(1000), nullable=False),
        sa.Column("site_name", sa.String(255), nullable=True),
        sa.Column("mcp_token", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_wordpress_sites_user_id", "wordpress_sites", ["user_id"])
    op.create_unique_constraint("uq_wordpress_sites_mcp_token", "wordpress_sites", ["mcp_token"])


def downgrade() -> None:
    op.drop_constraint("uq_wordpress_sites_mcp_token", "wordpress_sites", type_="unique")
    op.drop_index("ix_wordpress_sites_user_id", table_name="wordpress_sites")
    op.drop_table("wordpress_sites")
