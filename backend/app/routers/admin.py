from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.article import Article
from app.models.product import Product
from app.schemas.article import ArticleListItem, ArticleListResponse
from app.schemas.product import ProductListResponse
from app.schemas.tag import TagOut

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=50)]
StatusQuery = Annotated[str | None, Query(pattern="^(all|draft|published)$")]
SearchQuery = Annotated[str | None, Query()]


@router.get("/articles", response_model=ArticleListResponse)
async def list_admin_articles(
    current_user: CurrentUserDep,
    db: DbDep,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 10,
    status: StatusQuery = None,
    search: SearchQuery = None,
):
    query = select(Article)

    if status and status != "all":
        query = query.where(Article.status == status)

    if search:
        query = query.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.summary.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
            )
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()

    query = (
        query.options(selectinload(Article.tags))
        .order_by(Article.updated_at.desc(), Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    articles = result.scalars().all()

    items = [
        ArticleListItem(
            id=article.id,
            slug=article.slug,
            title=article.title,
            summary=article.summary,
            cover_image=article.cover_image,
            status=article.status,
            tags=[TagOut(id=tag.id, name=tag.name) for tag in article.tags],
            created_at=article.created_at,
        )
        for article in articles
    ]

    return ArticleListResponse(items=items, total=total or 0, page=page, page_size=page_size)


@router.get("/products", response_model=ProductListResponse)
async def list_admin_products(
    current_user: CurrentUserDep,
    db: DbDep,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 10,
    status: StatusQuery = None,
    search: SearchQuery = None,
):
    query = select(Product)

    if status and status != "all":
        query = query.where(Product.status == status)

    if search:
        query = query.where(
            or_(
                Product.title.ilike(f"%{search}%"),
                Product.slug.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()

    query = (
        query.order_by(Product.updated_at.desc(), Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)

    return ProductListResponse(
        items=list(result.scalars().all()),
        total=total or 0,
        page=page,
        page_size=page_size,
    )
