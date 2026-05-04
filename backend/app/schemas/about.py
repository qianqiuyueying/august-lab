from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, field_validator


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
    info_cards: Optional[list] = []
    contacts: Optional[list] = []
    updated_at: Optional[str] = None

    @field_validator("info_cards", "contacts", mode="before")
    @classmethod
    def ensure_list(cls, value: Any) -> list:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return []

    @field_validator("updated_at", mode="before")
    @classmethod
    def format_updated_at(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    model_config = {"from_attributes": True}
