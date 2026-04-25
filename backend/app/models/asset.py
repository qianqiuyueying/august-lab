from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, unique=True, index=True)
    original_name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    kind = Column(String(50), nullable=False, default="image")
    created_at = Column(DateTime, server_default=func.now())
