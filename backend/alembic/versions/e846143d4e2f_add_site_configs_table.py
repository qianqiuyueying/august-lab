"""add_site_configs_table

Revision ID: e846143d4e2f
Revises: 756957edd966
Create Date: 2026-04-15 10:19:55.826160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e846143d4e2f'
down_revision: Union[str, Sequence[str], None] = '756957edd966'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('site_configs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('value', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_site_configs_id'), 'site_configs', ['id'], unique=False)
    op.create_index(op.f('ix_site_configs_key'), 'site_configs', ['key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_site_configs_key'), table_name='site_configs')
    op.drop_index(op.f('ix_site_configs_id'), table_name='site_configs')
    op.drop_table('site_configs')
