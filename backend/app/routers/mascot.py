from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI

from app.database import get_db
from app.dependencies import get_current_user
from app.models.mascot_settings import MascotSettings
from app.schemas.mascot import (
    ChatRequest,
    ChatResponse,
    MascotSettingsPublic,
    MascotSettingsUpdate,
    MascotSettingsOut,
)

router = APIRouter()


async def _get_settings(db: AsyncSession) -> MascotSettings:
    result = await db.execute(select(MascotSettings).where(MascotSettings.id == 1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = MascotSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("/settings", response_model=MascotSettingsPublic)
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    return settings


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    if not settings.enabled or not settings.api_key:
        raise HTTPException(status_code=503, detail="AI chat is not enabled")

    system_prompt = settings.persona
    if settings.context_aware and req.context:
        system_prompt += f"\n当前用户正在浏览的页面内容：{req.context}"

    client = OpenAI(
        base_url=settings.api_base_url,
        api_key=settings.api_key,
    )

    try:
        response = client.chat.completions.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message},
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            stream=False,
        )
        reply = response.choices[0].message.content or ""
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI API error: {str(e)}")


@router.get("/admin/settings", response_model=MascotSettingsOut)
async def get_admin_settings(
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return await _get_settings(db)


@router.put("/admin/settings", response_model=MascotSettingsOut)
async def update_admin_settings(
    data: MascotSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    settings = await _get_settings(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings
