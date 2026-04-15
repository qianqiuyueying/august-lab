from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.page import Page
from app.dependencies import get_current_user
from app.schemas.page import PageCreate, PageUpdate, PageOut

router = APIRouter()


@router.get("", response_model=list[PageOut])
async def list_pages(db: AsyncSession = Depends(get_db)):
    """公开接口：仅返回已发布的页面。"""
    result = await db.execute(
        select(Page)
        .where(Page.status == "published")
        .order_by(Page.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{slug}", response_model=PageOut)
async def get_page(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Page).where(Page.slug == slug))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.post("", response_model=PageOut, status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Page).where(Page.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Page slug already exists")
    page = Page(
        slug=data.slug,
        title=data.title,
        content=data.content,
        description=data.description,
        content_type=data.content_type,
        status=data.status,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


@router.put("/{page_id}", response_model=PageOut)
async def update_page(
    page_id: int,
    data: PageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)
    await db.commit()
    await db.refresh(page)
    return page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    await db.delete(page)
    await db.commit()

