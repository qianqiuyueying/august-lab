import secrets

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.dependencies import get_current_user
from app.schemas.user import UserLogin, TokenResponse, UserOut
from app.utils.security import create_access_token

router = APIRouter()


async def login(data: UserLogin):
    """硬编码管理员认证，不再查询数据库。"""
    if (
        not secrets.compare_digest(data.username, settings.ADMIN_USERNAME)
        or not secrets.compare_digest(data.password, settings.ADMIN_PASSWORD)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": data.username})
    return TokenResponse(access_token=token)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """返回硬编码的管理员信息。"""
    return UserOut(id=current_user["id"], username=current_user["username"])


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(data: UserLogin):
    return await login(data)
