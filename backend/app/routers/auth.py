from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from ..database import get_db
from ..models import Session as SessionModel
from ..schemas import LoginRequest, LoginResponse, MessageResponse
from ..transaction import transactional, with_db_error_handling
from ..config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    # 从环境变量验证用户名和密码
    if login_data.username != settings.ADMIN_USERNAME or login_data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建会话
    session_id = str(uuid.uuid4())
    current_time = datetime.utcnow()
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
        SessionModel.expires_at > datetime.utcnow()
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
        SessionModel.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    return session.user_id