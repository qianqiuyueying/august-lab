from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.about_page import AboutPage
from app.schemas.about import AboutPageUpdate, AboutPageOut

router = APIRouter()


@router.get("", response_model=AboutPageOut)
async def get_about(db: AsyncSession = Depends(get_db)):
    """公开接口：获取关于页数据。"""
    result = await db.execute(select(AboutPage).limit(1))
    about = result.scalar_one_or_none()
    if not about:
        raise HTTPException(status_code=404, detail="About page not configured")
    return about


@router.put("", response_model=AboutPageOut)
async def update_about(
    data: AboutPageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """认证接口：更新关于页（upsert）。"""
    result = await db.execute(select(AboutPage).limit(1))
    about = result.scalar_one_or_none()
    if about:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(about, field, value)
    else:
        defaults = {
            "eyebrow": "About",
            "title": "",
            "avatar_url": "",
            "hero_subtitle": "",
            "cover_image": "",
            "content": "",
            "content_type": "markdown",
            "tech_stack": "[]",
            "info_cards": [],
            "contacts": [],
        }
        defaults.update(data.model_dump(exclude_unset=True))
        about = AboutPage(**defaults)
        db.add(about)
    await db.commit()
    await db.refresh(about)
    return about
