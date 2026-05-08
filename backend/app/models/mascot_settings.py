from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from app.database import Base


class MascotSettings(Base):
    __tablename__ = "mascot_settings"

    id = Column(Integer, primary_key=True, index=True, default=1)
    persona = Column(Text, nullable=False, default=(
        "你是刻晴，August's Lab 技术博客的看板娘小助手。\n"
        "性格：活泼元气、略傲娇、喜欢用颜文字和拟声词。\n"
        "说话风格：轻松可爱、偶尔吐槽，对技术保持好奇心。\n"
        "知识范围：前端开发、React、Python、开源技术。\n"
        "规则：回复简洁（1-3 句），不要长篇大论，保持角色感。"
    ))
    api_key = Column(String(255), nullable=False, default="")
    api_base_url = Column(String(500), nullable=False, default="https://api.deepseek.com")
    model = Column(String(100), nullable=False, default="deepseek-chat")
    temperature = Column(Float, nullable=False, default=0.8)
    max_tokens = Column(Integer, nullable=False, default=512)
    enabled = Column(Boolean, nullable=False, default=False)
    mascot_visible = Column(Boolean, nullable=False, default=True)
    mascot_scale = Column(Float, nullable=False, default=1.2)
    mascot_position_x = Column(Integer, nullable=True)
    mascot_position_y = Column(Integer, nullable=True)
    show_on_mobile = Column(Boolean, nullable=False, default=False)
    greeting_enabled = Column(Boolean, nullable=False, default=True)
    greeting_delay_seconds = Column(Integer, nullable=False, default=8)
    random_action_interval = Column(Integer, nullable=False, default=15)
    context_aware = Column(Boolean, nullable=False, default=False)
    drag_enabled = Column(Boolean, nullable=False, default=True)
