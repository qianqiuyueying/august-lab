"""remove comments table

Revision ID: a3c8d7f6e2b1
Revises: 11b77d8c047f
Create Date: 2026-04-16 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c8d7f6e2b1'
down_revision: Union[str, None] = '11b77d8c047f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('comments')


def downgrade() -> None:
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('article_id', sa.Integer, sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_name', sa.String(100), nullable=False),
        sa.Column('author_email', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
