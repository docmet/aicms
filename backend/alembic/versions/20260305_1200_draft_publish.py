"""Add draft/publish content model + page versioning

Renames content_sections.content -> content_draft, adds content_published.
Adds pages.last_published_at.
Creates page_versions table (max 5 snapshots per page).

Revision ID: 20260305_1200_draft_publish
Revises: 20260305_0042_soft_delete
Create Date: 2026-03-05

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "20260305_1200_draft_publish"
down_revision = "20260305_0042_soft_delete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── content_sections: rename content -> content_draft, add content_published ──
    op.alter_column(
        "content_sections",
        "content",
        new_column_name="content_draft",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
    op.add_column(
        "content_sections",
        sa.Column("content_published", sa.Text(), nullable=True),
    )

    # ── pages: add last_published_at ──────────────────────────────────────────
    op.add_column(
        "pages",
        sa.Column("last_published_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── page_versions table ───────────────────────────────────────────────────
    op.create_table(
        "page_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "page_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", sa.Text(), nullable=False),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "published_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("label", sa.String(255), nullable=True),
    )
    op.create_index(
        op.f("ix_page_versions_page_id"),
        "page_versions",
        ["page_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop page_versions
    op.drop_index(op.f("ix_page_versions_page_id"), table_name="page_versions")
    op.drop_table("page_versions")

    # Remove last_published_at from pages
    op.drop_column("pages", "last_published_at")

    # Revert content_sections: drop content_published, rename content_draft -> content
    op.drop_column("content_sections", "content_published")
    op.alter_column(
        "content_sections",
        "content_draft",
        new_column_name="content",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
