from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentCreate(BaseModel):
    author_name: str
    author_email: str
    content: str


class CommentOut(BaseModel):
    id: int
    article_id: int
    author_name: str
    author_email: str
    content: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
