from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid

from ..database import get_db
from ..models import Session as SessionModel
from ..schemas import LoginRequest, LoginResponse, MessageResponse
from ..transaction import transactional, with_db_error_handling
from ..config import settings
import time
import json

router = APIRouter()
security = HTTPBearer()

#region agent log
def _agent_log(payload: dict) -> None:
    """Debug-mode NDJSON logger (no secrets)."""
    try:
        payload.setdefault("timestamp", int(time.time() * 1000))
        with open(r"g:\vscode\projects\August\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
#endregion

@router.post("/login", response_model=LoginResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    # 从环境变量验证用户名和密码
    #region agent log
    _agent_log({
        "sessionId": "debug-session",
        "runId": "pre-fix",
        "hypothesisId": "H1",
        "location": "backend/app/routers/auth.py:login:entry",
        "message": "login attempt received",
        "data": {
            "username_len": len(login_data.username or ""),
            "username_matches": login_data.username == settings.ADMIN_USERNAME,
            "password_matches": login_data.password == settings.ADMIN_PASSWORD,
        },
    })
    #endregion
    if login_data.username != settings.ADMIN_USERNAME or login_data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建会话
    session_id = str(uuid.uuid4())
    current_time = datetime.now(timezone.utc)
    expires_at = current_time + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
    
    session = SessionModel(
        id=session_id,
        user_id="admin",
        created_at=current_time,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(session)
    db.flush()  # 刷新但不提交
    
    return LoginResponse(access_token=session_id)

@router.post("/logout", response_model=MessageResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """管理员登出"""
    session = db.query(SessionModel).filter(
        SessionModel.id == credentials.credentials,
        SessionModel.is_active == True
    ).first()
    
    if session:
        session.is_active = False
        db.flush()  # 刷新但不提交
    
    return MessageResponse(message="登出成功")

@router.get("/verify", response_model=MessageResponse)
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """验证登录状态"""
    session = db.query(SessionModel).filter(
        SessionModel.id == credentials.credentials,
        SessionModel.is_active == True,
        SessionModel.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    return MessageResponse(message="令牌有效")

# 认证依赖
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前用户（认证中间件）"""
    session = db.query(SessionModel).filter(
        SessionModel.id == credentials.credentials,
        SessionModel.is_active == True,
        SessionModel.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    return session.user_id