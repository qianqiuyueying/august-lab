from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.article import Article
from app.models.article_tag import article_tag
from app.models.tag import Tag
from app.schemas.article import (
    ArticleCreate,
    ArticleListItem,
    ArticleListResponse,
    ArticleOut,
    ArticleUpdate,
    ArticleUpload,
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

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()

    result = await db.execute(
        query.options(selectinload(Article.tags))
        .order_by(Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
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


@router.get("/{slug}", response_model=ArticleOut)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Article)
        .where(Article.slug == slug)
        .options(selectinload(Article.tags))
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
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
        cover_image=data.cover_image,
        status=data.status,
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
        .options(selectinload(Article.tags))
    )
    return result.scalar_one()


@router.put("/{article_id}", response_model=ArticleOut)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Article)
        .where(Article.id == article_id)
        .options(selectinload(Article.tags))
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
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            article.tags.append(tag)

    await db.commit()

    result = await db.execute(
        select(Article)
        .where(Article.id == article.id)
        .options(selectinload(Article.tags))
    )
    return result.scalar_one()


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)
    await db.commit()


@router.post("/upload", response_model=ArticleUpload)
async def upload_md(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """上传 Markdown 文件，解析标题和内容后返回给前端编辑。"""
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are allowed")

    content = await file.read()
    text = content.decode("utf-8")

    title = file.filename[:-3]
    lines = text.split("\n")
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            content_start = i + 1
            break
        if line.startswith("---") and i == 0:
            for j, line2 in enumerate(lines[i + 1 :], i + 1):
                if line2.startswith("---"):
                    content_start = j + 1
                    break
            break

    content_text = "\n".join(lines[content_start:]).strip()
    return ArticleUpload(title=title, content=content_text)
