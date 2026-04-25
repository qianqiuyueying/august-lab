from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AssetOut(BaseModel):
    id: int
    filename: str
    original_name: str
    url: str
    mime_type: str
    size: int
    kind: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    items: list[AssetOut]
    total: int
    page: int
    page_size: int
