import os
import zipfile
import tempfile
import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.page import Page
from app.dependencies import get_current_user
from app.schemas.page import PageCreate, PageUpdate, PageOut

router = APIRouter()

PRODUCTS_DIR = "/app/products"


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
    # 同时删除服务器上的产品目录
    product_dir = os.path.join(PRODUCTS_DIR, page.slug)
    if os.path.exists(product_dir):
        shutil.rmtree(product_dir)
    await db.delete(page)
    await db.commit()


@router.post("/{page_id}/upload")
async def upload_product_zip(
    page_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """上传 ZIP 文件并解压为产品静态页面。"""
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

    product_dir = os.path.join(PRODUCTS_DIR, page.slug)
    os.makedirs(product_dir, exist_ok=True)

    # 解压到临时目录，验证后再移动
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)
        with open(zip_path, "wb") as f:
            content = await file.read()
            f.write(content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            # 安全检查：确保没有路径遍历
            for member in zf.namelist():
                member_path = os.path.realpath(os.path.join(tmpdir, member))
                if not member_path.startswith(os.path.realpath(tmpdir)):
                    raise HTTPException(status_code=400, detail="Invalid ZIP: path traversal detected")
            zf.extractall(tmpdir)

        # 找到入口文件（index.html 或类似）
        # 解压后的内容可能在一个子目录里
        extracted_root = tmpdir
        for item in os.listdir(tmpdir):
            item_path = os.path.join(tmpdir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "index.html")):
                extracted_root = item_path
                break

        # 复制到产品目录
        for item in os.listdir(extracted_root):
            src = os.path.join(extracted_root, item)
            dst = os.path.join(product_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    # 更新页面内容为指向产品的链接
    page.content = f'<a href="/products/{page.slug}/">View Product</a>'
    page.content_type = "html"
    await db.commit()
    await db.refresh(page)

    return {"message": "Product uploaded successfully", "url": f"/products/{page.slug}/"}
