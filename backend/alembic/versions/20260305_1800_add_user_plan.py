"""Add plan column to users table.

Revision ID: 20260305_1800_add_user_plan
Revises: 20260305_1300_initial_schema
Create Date: 2026-03-05
"""

import sqlalchemy as sa  # noqa: E402

from alembic import op

revision = "20260305_1800_add_user_plan"
down_revision = "20260305_1300_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE user_plan_enum AS ENUM ('free', 'pro', 'agency')")
    op.add_column(
        "users",
        sa.Column(
            "plan",
            sa.Enum("free", "pro", "agency", name="user_plan_enum"),
            nullable=False,
            server_default="free",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "plan")
    op.execute("DROP TYPE user_plan_enum")
