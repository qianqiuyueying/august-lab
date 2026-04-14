from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.article import Article
from app.models.tag import Tag
from app.models.article_tag import article_tag
from app.dependencies import get_current_user
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleOut,
    ArticleListItem,
    ArticleListResponse,
)
from app.schemas.tag import TagOut
from app.utils.slug import slugify

router = APIRouter()


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    tag: str = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Article).where(Article.status == "published")

    if tag:
        query = query.join(article_tag).join(Tag).where(Tag.name == tag)

    if search:
        query = query.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = (
        query
        .options(selectinload(Article.tags))
        .order_by(Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    articles = result.scalars().all()

    items = [
        ArticleListItem(
            id=a.id,
            slug=a.slug,
            title=a.title,
            summary=a.summary,
            status=a.status,
            tags=[TagOut(id=t.id, name=t.name) for t in a.tags],
            created_at=a.created_at,
        )
        for a in articles
    ]

    return ArticleListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{slug}", response_model=ArticleOut)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(Article)
        .where(Article.slug == slug)
        .options(selectinload(Article.tags), selectinload(Article.author))
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_slug = slugify(data.title)
    slug = base_slug
    counter = 1
    while True:
        existing = await db.execute(select(Article).where(Article.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    article = Article(
        slug=slug,
        title=data.title,
        content=data.content,
        summary=data.summary or data.content[:200],
        status=data.status,
        author_id=current_user.id,
    )

    if data.tags:
        for tag_name in data.tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            article.tags.append(tag)

    db.add(article)
    await db.commit()

    result = await db.execute(
        select(Article)
        .where(Article.id == article.id)
        .options(selectinload(Article.tags), selectinload(Article.author))
    )
    article = result.scalar_one()
    return article


@router.put("/{article_id}", response_model=ArticleOut)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Article)
        .where(Article.id == article_id)
        .options(selectinload(Article.tags), selectinload(Article.author))
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = data.model_dump(exclude_unset=True)
    tags_data = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(article, field, value)

    if tags_data is not None:
        article.tags.clear()
        for tag_name in tags_data:
            tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = tag_result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            article.tags.append(tag)

    await db.commit()

    result = await db.execute(
        select(Article)
        .where(Article.id == article.id)
        .options(selectinload(Article.tags), selectinload(Article.author))
    )
    article = result.scalar_one()
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await db.delete(article)
    await db.commit()
