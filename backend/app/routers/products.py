import os
import zipfile
import tempfile
import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.dependencies import get_current_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter()

PRODUCTS_DIR = "/app/products"


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    """公开接口：按 slug 获取单个已发布产品。"""
    result = await db.execute(
        select(Product).where(Product.slug == slug, Product.status == "published")
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)):
    """公开接口：仅返回已发布的产品。"""
    result = await db.execute(
        select(Product)
        .where(Product.status == "published")
        .order_by(Product.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Product slug already exists")
    product = Product(
        slug=data.slug,
        title=data.title,
        description=data.description,
        status=data.status,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_dir = os.path.join(PRODUCTS_DIR, product.slug)
    if os.path.exists(product_dir):
        shutil.rmtree(product_dir)
    await db.delete(product)
    await db.commit()


@router.post("/{product_id}/upload")
async def upload_product_zip(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """上传 ZIP 文件并解压为产品静态页面。"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

    product_dir = os.path.join(PRODUCTS_DIR, product.slug)
    os.makedirs(product_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                member_path = os.path.realpath(os.path.join(tmpdir, member))
                if not member_path.startswith(os.path.realpath(tmpdir)):
                    raise HTTPException(status_code=400, detail="Invalid ZIP: path traversal detected")
            zf.extractall(tmpdir)

        extracted_root = tmpdir
        for item in os.listdir(tmpdir):
            item_path = os.path.join(tmpdir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "index.html")):
                extracted_root = item_path
                break

        for item in os.listdir(extracted_root):
            src = os.path.join(extracted_root, item)
            dst = os.path.join(product_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    return {"message": "Product uploaded successfully", "url": f"/products/{product.slug}/"}
