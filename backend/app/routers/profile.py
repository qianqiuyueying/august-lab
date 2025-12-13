from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Profile as ProfileModel
from ..schemas import Profile, ProfileUpdate, MessageResponse
from ..transaction import transactional, with_db_error_handling
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=Profile)
def get_profile(db: Session = Depends(get_db)):
    """获取个人信息（公开接口）"""
    profile = db.query(ProfileModel).filter(ProfileModel.id == 1).first()
    
    if not profile:
        # 如果没有个人信息，返回默认信息
        default_profile = ProfileModel(
            id=1,
            name="August",
            title="全栈开发者",
            bio="我是一名热爱技术的开发者，专注于前端和后端开发。",
            email="august@example.com",
            skills=[]
        )
        db.add(default_profile)
        db.commit()
        db.refresh(default_profile)
        return default_profile
    
    return profile

@router.put("/", response_model=Profile)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新个人信息（需要认证）"""
    profile = db.query(ProfileModel).filter(ProfileModel.id == 1).first()
    
    if not profile:
        # 如果没有个人信息记录，创建一个新的
        profile_dict = profile_data.dict(exclude_unset=True)
        profile_dict["id"] = 1
        profile = ProfileModel(**profile_dict)
        db.add(profile)
    else:
        # 更新现有记录
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
    
    db.flush()  # 刷新但不提交
    db.refresh(profile)
    return profile