from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500), default="")
    cover_image = Column(String(500), nullable=True)
    runtime_url = Column(String(500), nullable=True)
    status = Column(String(20), default="draft")  # draft | published
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
