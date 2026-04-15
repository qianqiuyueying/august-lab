from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PageCreate(BaseModel):
    slug: str
    title: str
    content: str = ""
    description: str = ""
    content_type: str = "markdown"
    status: str = "draft"


class PageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None


class PageOut(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    description: str
    content_type: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
