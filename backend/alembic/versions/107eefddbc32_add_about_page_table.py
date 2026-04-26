"""add about page table

Revision ID: 107eefddbc32
Revises: b42f4f8d7a21
Create Date: 2026-04-26 20:40:46.293192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '107eefddbc32'
down_revision: Union[str, Sequence[str], None] = 'b42f4f8d7a21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create about_pages table
    op.create_table(
        "about_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("eyebrow", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=20), nullable=True),
        sa.Column("tech_stack", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_about_pages_id"), "about_pages", ["id"], unique=False)

    # Migrate old about_bio to about_pages.content
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT value FROM site_configs WHERE key = 'about_bio'"))
    row = result.fetchone()
    if row:
        op.execute(
            sa.text("INSERT INTO about_pages (eyebrow, title, content, content_type, tech_stack) VALUES ('About', '关于 August''s Lab', :content, 'markdown', '[]')").bindparams(content=row[0])
        )

    # Drop old pages table
    op.drop_table("pages")


def downgrade() -> None:
    # Restore pages table
    op.create_table(
        "pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("content_type", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pages_id"), "pages", ["id"], unique=False)
    op.create_index(op.f("ix_pages_slug"), "pages", ["slug"], unique=True)

    # Drop about_pages table
    op.drop_index(op.f("ix_about_pages_id"), table_name="about_pages")
    op.drop_table("about_pages")
