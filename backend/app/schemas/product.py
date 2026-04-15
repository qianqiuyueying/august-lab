from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    slug: str
    title: str
    description: str = ""
    cover_image: Optional[str] = None
    status: str = "draft"


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    cover_image: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
