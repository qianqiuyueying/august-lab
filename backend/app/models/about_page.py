from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class AboutPage(Base):
    __tablename__ = "about_pages"

    id = Column(Integer, primary_key=True, index=True)
    eyebrow = Column(String(100), default="About")
    title = Column(String(255), nullable=False, default="")
    cover_image = Column(String(500), default="")
    content = Column(Text, default="")
    content_type = Column(String(20), default="markdown")
    tech_stack = Column(Text, default="[]")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
