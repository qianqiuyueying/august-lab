import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.asset import Asset
from app.schemas.asset import AssetListResponse, AssetOut

router = APIRouter(prefix="/assets")

UPLOADS_DIR = settings.UPLOADS_DIR
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}

DbDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=50)]
SearchQuery = Annotated[str | None, Query()]
KindQuery = Annotated[str, Query(pattern="^image$")]


def _image_dir() -> Path:
    path = Path(UPLOADS_DIR) / "images"
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.get("", response_model=AssetListResponse)
async def list_assets(
    current_user: CurrentUserDep,
    db: DbDep,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 24,
    kind: KindQuery = "image",
    search: SearchQuery = None,
):
    query = select(Asset).where(Asset.kind == kind)

    if search:
        query = query.where(
            or_(
                Asset.original_name.ilike(f"%{search}%"),
                Asset.filename.ilike(f"%{search}%"),
            )
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(
        query.order_by(Asset.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return AssetListResponse(
        items=list(result.scalars().all()),
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.post("/upload", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    current_user: CurrentUserDep,
    db: DbDep,
    file: UploadFile = File(...),
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image file is too large")

    filename = f"{uuid.uuid4().hex}{ALLOWED_IMAGE_TYPES[content_type]}"
    asset_path = _image_dir() / filename
    asset_path.write_bytes(content)

    asset = Asset(
        filename=filename,
        original_name=file.filename or filename,
        url=f"/uploads/images/{filename}",
        mime_type=content_type,
        size=len(content),
        kind="image",
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    current_user: CurrentUserDep,
    db: DbDep,
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    path = Path(UPLOADS_DIR) / "images" / asset.filename
    if path.exists() and path.is_file():
        os.remove(path)

    await db.delete(asset)
    await db.commit()
