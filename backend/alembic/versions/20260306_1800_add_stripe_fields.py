"""Add Stripe customer/subscription ID columns to users.

Revision ID: 20260306_1800_add_stripe_fields
Revises: 20260305_2030_theme_draft
Create Date: 2026-03-06
"""

import sqlalchemy as sa

from alembic import op

revision = "20260306_1800_add_stripe_fields"
down_revision = "20260305_2030_theme_draft"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("stripe_customer_id", sa.String(255), nullable=True, unique=True),
    )
    op.add_column(
        "users",
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
    )
    op.create_index("ix_users_stripe_customer_id", "users", ["stripe_customer_id"])


def downgrade() -> None:
    op.drop_index("ix_users_stripe_customer_id", table_name="users")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
