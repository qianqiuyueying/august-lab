from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AboutPageUpdate(BaseModel):
    eyebrow: Optional[str] = "About"
    title: Optional[str] = None
    avatar_url: Optional[str] = ""
    hero_subtitle: Optional[str] = ""
    cover_image: Optional[str] = ""
    content: Optional[str] = ""
    content_type: Optional[str] = "markdown"
    tech_stack: Optional[str] = "[]"
    info_cards: Optional[list] = []
    contacts: Optional[list] = []


class AboutPageOut(BaseModel):
    id: int
    eyebrow: str
    title: str
    avatar_url: str
    hero_subtitle: str
    cover_image: str
    content: str
    content_type: str
    tech_stack: str
    info_cards: list
    contacts: list
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
