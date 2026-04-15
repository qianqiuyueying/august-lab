"""add cover_image to articles and products

Revision ID: 11b77d8c047f
Revises: 9475a6e51b14
Create Date: 2026-04-15 18:41:31.084881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '11b77d8c047f'
down_revision: Union[str, Sequence[str], None] = '9475a6e51b14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('cover_image', sa.String(length=500), nullable=True))
    op.add_column('products', sa.Column('cover_image', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'cover_image')
    op.drop_column('articles', 'cover_image')
