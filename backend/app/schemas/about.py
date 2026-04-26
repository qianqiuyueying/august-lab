from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AboutPageUpdate(BaseModel):
    eyebrow: Optional[str] = "About"
    title: Optional[str] = None
    cover_image: Optional[str] = ""
    content: Optional[str] = ""
    content_type: Optional[str] = "markdown"
    tech_stack: Optional[str] = "[]"


class AboutPageOut(BaseModel):
    id: int
    eyebrow: str
    title: str
    cover_image: str
    content: str
    content_type: str
    tech_stack: str
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
