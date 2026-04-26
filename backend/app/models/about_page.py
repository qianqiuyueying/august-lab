from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON
from app.database import Base


class AboutPage(Base):
    __tablename__ = "about_pages"

    id = Column(Integer, primary_key=True, index=True)
    eyebrow = Column(String(100), default="About")
    title = Column(String(255), nullable=False, default="")
    avatar_url = Column(String(500), default="")
    hero_subtitle = Column(String(200), default="")
    cover_image = Column(String(500), default="")
    content = Column(Text, default="")
    content_type = Column(String(20), default="markdown")
    tech_stack = Column(Text, default="[]")
    info_cards = Column(JSON, default=list)
    contacts = Column(JSON, default=list)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
