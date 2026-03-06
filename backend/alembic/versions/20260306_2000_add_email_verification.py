"""Add email verification and password reset columns to users.

Revision ID: 20260306_2000_add_email_verification
Revises: 20260306_1800_add_stripe_fields
Create Date: 2026-03-06
"""

import sqlalchemy as sa

from alembic import op

revision = "20260306_2000_add_email_verification"
down_revision = "20260306_1800_add_stripe_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_token", sa.String(64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("reset_token", sa.String(64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("reset_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email_verification_token", "users", ["email_verification_token"])
    op.create_index("ix_users_reset_token", "users", ["reset_token"])


def downgrade() -> None:
    op.drop_index("ix_users_reset_token", table_name="users")
    op.drop_index("ix_users_email_verification_token", table_name="users")
    op.drop_column("users", "reset_token_expires_at")
    op.drop_column("users", "reset_token")
    op.drop_column("users", "email_verification_token")
    op.drop_column("users", "email_verified")
