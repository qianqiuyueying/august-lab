"""add about section fields

Revision ID: 1a13359f9afa
Revises: 107eefddbc32
Create Date: 2026-04-26 21:39:42.147161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a13359f9afa'
down_revision: Union[str, Sequence[str], None] = '107eefddbc32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('about_pages', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('about_pages', sa.Column('hero_subtitle', sa.String(length=200), nullable=True))
    op.add_column('about_pages', sa.Column('info_cards', sa.JSON(), nullable=True))
    op.add_column('about_pages', sa.Column('contacts', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('about_pages', 'contacts')
    op.drop_column('about_pages', 'info_cards')
    op.drop_column('about_pages', 'hero_subtitle')
    op.drop_column('about_pages', 'avatar_url')
