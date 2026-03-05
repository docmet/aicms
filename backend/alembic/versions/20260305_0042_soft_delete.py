"""Add soft delete fields to sites, pages, and content_sections

Revision ID: 20260305_0042_soft_delete
Revises: 20260304_1357_77d1e7b8e390
Create Date: 2026-03-05

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = '20260305_0042_soft_delete'
down_revision = '77d1e7b8e390'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_deleted and deleted_at to sites
    op.add_column('sites', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('sites', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_sites_is_deleted'), 'sites', ['is_deleted'], unique=False)

    # Add is_deleted and deleted_at to pages
    op.add_column('pages', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('pages', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_pages_is_deleted'), 'pages', ['is_deleted'], unique=False)

    # Add is_deleted and deleted_at to content_sections
    op.add_column('content_sections', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('content_sections', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_content_sections_is_deleted'), 'content_sections', ['is_deleted'], unique=False)


def downgrade():
    # Remove from content_sections
    op.drop_index(op.f('ix_content_sections_is_deleted'), table_name='content_sections')
    op.drop_column('content_sections', 'deleted_at')
    op.drop_column('content_sections', 'is_deleted')

    # Remove from pages
    op.drop_index(op.f('ix_pages_is_deleted'), table_name='pages')
    op.drop_column('pages', 'deleted_at')
    op.drop_column('pages', 'is_deleted')

    # Remove from sites
    op.drop_index(op.f('ix_sites_is_deleted'), table_name='sites')
    op.drop_column('sites', 'deleted_at')
    op.drop_column('sites', 'is_deleted')
