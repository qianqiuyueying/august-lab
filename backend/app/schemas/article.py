from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemas.user import UserOut


class ArticleCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = ""
    status: str = "draft"
    tags: List[str] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class ArticleOut(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    summary: str
    status: str
    author: Optional["UserOut"] = None
    tags: List["TagOut"] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    status: str
    tags: List["TagOut"] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    items: List[ArticleListItem]
    total: int
    page: int
    page_size: int


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
