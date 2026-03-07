"""Add name and phone columns to users table.

Revision ID: 20260307_0700
Revises: 20260307_0600
Create Date: 2026-03-07 07:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "20260307_0700"
down_revision = "20260307_0600"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone")
    op.drop_column("users", "name")
