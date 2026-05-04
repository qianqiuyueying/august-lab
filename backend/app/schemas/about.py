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
    eyebrow: Optional[str] = None
    title: Optional[str] = None
    avatar_url: Optional[str] = None
    hero_subtitle: Optional[str] = None
    cover_image: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    tech_stack: Optional[str] = None
    info_cards: Optional[list] = None
    contacts: Optional[list] = None
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

    @field_validator(
        "eyebrow", "title", "avatar_url", "hero_subtitle",
        "cover_image", "content", "content_type", "tech_stack",
        mode="before"
    )
    @classmethod
    def empty_to_str(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    model_config = {"from_attributes": True}
