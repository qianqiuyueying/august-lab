from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.site_config import SiteConfig
from pydantic import BaseModel

router = APIRouter()


class ConfigItem(BaseModel):
    key: str
    value: str


class ConfigUpdate(BaseModel):
    value: str


@router.get("/{key}")
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SiteConfig).where(SiteConfig.key == key))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return ConfigItem(key=config.key, value=config.value)


@router.put("/{key}", response_model=ConfigItem)
async def update_config(
    key: str,
    data: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SiteConfig).where(SiteConfig.key == key))
    config = result.scalar_one_or_none()
    if config:
        config.value = data.value
    else:
        config = SiteConfig(key=key, value=data.value)
        db.add(config)
    await db.commit()
    await db.refresh(config)
    return ConfigItem(key=config.key, value=config.value)
