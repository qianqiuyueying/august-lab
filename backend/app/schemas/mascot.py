from typing import Optional

from pydantic import BaseModel


class MascotSettingsUpdate(BaseModel):
    persona: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    enabled: Optional[bool] = None
    mascot_visible: Optional[bool] = None
    mascot_scale: Optional[float] = None
    mascot_position_x: Optional[int] = None
    mascot_position_y: Optional[int] = None
    show_on_mobile: Optional[bool] = None
    greeting_enabled: Optional[bool] = None
    greeting_delay_seconds: Optional[int] = None
    random_action_interval: Optional[int] = None
    context_aware: Optional[bool] = None
    drag_enabled: Optional[bool] = None


class MascotSettingsPublic(BaseModel):
    """Public settings — api_key excluded"""
    persona: str
    api_base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 0.8
    max_tokens: int = 512
    enabled: bool = False
    mascot_visible: bool = True
    mascot_scale: float = 1.2
    mascot_position_x: Optional[int] = None
    mascot_position_y: Optional[int] = None
    show_on_mobile: bool = False
    greeting_enabled: bool = True
    greeting_delay_seconds: int = 8
    random_action_interval: int = 15
    context_aware: bool = False
    drag_enabled: bool = True

    model_config = {"from_attributes": True}


class MascotSettingsOut(MascotSettingsPublic):
    """Admin output — includes api_key"""
    id: int
    api_key: str = ""


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
