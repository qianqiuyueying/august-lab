from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models import Blog as BlogModel
from ..schemas import Blog, BlogCreate, BlogUpdate, MessageResponse
from ..transaction import transactional, with_db_error_handling
from ..security import create_safe_query_executor, sql_injection_protection, validate_and_sanitize_input
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Blog])
@sql_injection_protection
def get_blogs(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取博客列表（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    filters = {}
    if published_only:
        filters['is_published'] = True
    
    if search:
        # 使用安全搜索
        blogs = safe_executor.safe_search_query(
            BlogModel, 
            ['title', 'content', 'summary'], 
            search, 
            limit=min(limit, 100)
        )
        # 如果需要过滤已发布状态，再次过滤
        if published_only:
            blogs = [blog for blog in blogs if blog.is_published]
    else:
        # 使用安全过滤查询
        blogs = safe_executor.safe_filter_query(
            BlogModel,
            filters,
            limit=min(limit, 100),
            offset=max(skip, 0),
            order_by='created_at'
        )
    
    return blogs

@router.get("/{blog_id}", response_model=Blog)
@sql_injection_protection
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    """获取单篇博客详情（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    blog = safe_executor.safe_get_by_id(BlogModel, blog_id)
    
    if not blog or not blog.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="博客文章不存在"
        )
    
    return blog

@router.post("/", response_model=Blog)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def create_blog(
    blog_data: BlogCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建新博客（需要认证）"""
    blog_dict = blog_data.dict()
    
    # 如果是发布状态，设置发布时间
    if blog_dict.get("is_published"):
        blog_dict["published_at"] = datetime.now(timezone.utc)
    
    blog = BlogModel(**blog_dict)
    db.add(blog)
    db.flush()  # 刷新以获取ID，但不提交
    db.refresh(blog)
    return blog

@router.put("/{blog_id}", response_model=Blog)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def update_blog(
    blog_id: int,
    blog_data: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新博客（需要认证）"""
    blog = db.query(BlogModel).filter(BlogModel.id == blog_id).first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="博客文章不存在"
        )
    
    # 更新字段
    update_data = blog_data.dict(exclude_unset=True)
    
    # 如果从未发布变为发布，设置发布时间
    if update_data.get("is_published") and not blog.is_published:
        update_data["published_at"] = datetime.now(timezone.utc)
    
    for field, value in update_data.items():
        setattr(blog, field, value)
    
    db.flush()  # 刷新但不提交
    db.refresh(blog)
    return blog

@router.delete("/{blog_id}", response_model=MessageResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除博客（需要认证）"""
    blog = db.query(BlogModel).filter(BlogModel.id == blog_id).first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="博客文章不存在"
        )
    
    db.delete(blog)
    # 事务装饰器会处理提交
    
    return MessageResponse(message="博客文章删除成功")

# 管理员专用接口：获取所有博客（包括草稿）
@router.get("/admin/all", response_model=List[Blog])
def get_all_blogs_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取所有博客列表（管理员接口，包括草稿）"""
    blogs = db.query(BlogModel).order_by(BlogModel.created_at.desc()).offset(skip).limit(limit).all()
    return blogs

@router.get("/admin/{blog_id}", response_model=Blog)
def get_blog_admin(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取单篇博客详情（管理员接口，包括草稿）"""
    blog = db.query(BlogModel).filter(BlogModel.id == blog_id).first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="博客文章不存在"
        )
    
    return blog