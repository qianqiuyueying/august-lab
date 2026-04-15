from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(String(500), default="")
    content_type = Column(String(20), default="markdown")  # markdown | html
    status = Column(String(20), default="draft")  # draft | published
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
