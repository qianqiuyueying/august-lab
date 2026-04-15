"""simplify_auth_and_add_product_fields

Revision ID: 756957edd966
Revises: f2884d087b89
Create Date: 2026-04-15 09:41:57.368793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '756957edd966'
down_revision: Union[str, Sequence[str], None] = 'f2884d087b89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 文章去掉 author_id 字段（先设为 nullable，SQLite 不支持直接 DROP COLUMN 旧版本）
    with op.batch_alter_table('articles') as batch_op:
        batch_op.alter_column('author_id', nullable=True)

    # 2. 页面表新增 description 和 content_type 字段
    with op.batch_alter_table('pages') as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(500), server_default=''))
        batch_op.add_column(sa.Column('content_type', sa.String(20), server_default='markdown'))

    # 3. 创建默认的 about 页面（如果不存在）
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM pages WHERE slug = 'about'"))
    if result.scalar() == 0:
        op.execute(
            "INSERT INTO pages (slug, title, content, description, content_type, status) "
            "VALUES ('about', 'About Me', '欢迎来到 August''s Lab！这里是August的个人空间，用于分享技术心得、项目经验和对世界的思考。', '关于本站和站主', 'markdown', 'published')"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('pages') as batch_op:
        batch_op.drop_column('content_type')
        batch_op.drop_column('description')

    with op.batch_alter_table('articles') as batch_op:
        batch_op.alter_column('author_id', nullable=False)
