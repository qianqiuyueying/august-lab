import os
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.article import Article
from app.models.tag import Tag
from app.models.article_tag import article_tag
from app.models.product import Product
from app.models.page import Page
from app.models.user import User

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # 文章统计
    article_total = (await db.execute(select(func.count(Article.id)))).scalar()
    published_count = (await db.execute(
        select(func.count(Article.id)).where(Article.status == "published")
    )).scalar()
    draft_count = (await db.execute(
        select(func.count(Article.id)).where(Article.status == "draft")
    )).scalar()

    # 产品统计
    product_count = (await db.execute(select(func.count(Product.id)))).scalar()

    # 页面统计
    page_count = (await db.execute(select(func.count(Page.id)))).scalar()

    # 标签统计
    tag_count = (await db.execute(select(func.count(Tag.id)))).scalar()

    # 用户统计
    user_count = (await db.execute(select(func.count(User.id)))).scalar()

    # 最近文章
    recent_result = await db.execute(
        select(Article)
        .options(selectinload(Article.tags))
        .order_by(Article.created_at.desc())
        .limit(5)
    )
    recent_articles = recent_result.scalars().all()
    recent_list = [
        {
            "id": a.id,
            "title": a.title,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "tags": [{"id": t.id, "name": t.name} for t in a.tags],
        }
        for a in recent_articles
    ]

    # 标签分布（各标签关联的文章数）
    tag_dist_result = await db.execute(
        select(Tag.name, func.count(article_tag.c.article_id))
        .join(article_tag, Tag.id == article_tag.c.tag_id)
        .group_by(Tag.id)
        .order_by(func.count(article_tag.c.article_id).desc())
        .limit(10)
    )
    tag_distribution = [
        {"name": name, "count": count} for name, count in tag_dist_result.all()
    ]

    # 数据库大小
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if db_path and os.path.isfile(db_path):
        size_bytes = os.path.getsize(db_path)
    else:
        size_bytes = None

    return {
        "article_count": article_total,
        "published_count": published_count,
        "draft_count": draft_count,
        "product_count": product_count,
        "page_count": page_count,
        "tag_count": tag_count,
        "user_count": user_count,
        "recent_articles": recent_list,
        "tag_distribution": tag_distribution,
        "database_size": size_bytes,
    }
