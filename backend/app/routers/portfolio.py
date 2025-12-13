from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Portfolio as PortfolioModel
from ..schemas import Portfolio, PortfolioCreate, PortfolioUpdate, MessageResponse
from ..transaction import transactional, with_db_error_handling
from ..security import create_safe_query_executor, sql_injection_protection, validate_and_sanitize_input
from ..error_handlers import (
    ResourceNotFoundAPIError, ValidationAPIError, create_success_response, 
    create_paginated_response
)
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Portfolio])
@sql_injection_protection
def get_portfolios(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取作品列表（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    if search:
        # 使用安全搜索
        portfolios = safe_executor.safe_search_query(
            PortfolioModel, 
            ['title', 'description'], 
            search, 
            limit=min(limit, 100)
        )
    else:
        # 使用安全过滤查询
        portfolios = safe_executor.safe_filter_query(
            PortfolioModel,
            {},
            limit=min(limit, 100),
            offset=max(skip, 0),
            order_by='created_at'
        )
    
    return portfolios

@router.get("/{portfolio_id}", response_model=Portfolio)
@sql_injection_protection
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """获取单个作品详情（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    portfolio = safe_executor.safe_get_by_id(PortfolioModel, portfolio_id)
    
    if not portfolio:
        raise ResourceNotFoundAPIError("作品", portfolio_id)
    
    return portfolio

@router.post("/", response_model=Portfolio)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建新作品（需要认证）"""
    # 验证和清理输入数据
    safe_data = validate_and_sanitize_input(portfolio_data.dict())
    
    portfolio = PortfolioModel(**safe_data)
    db.add(portfolio)
    db.flush()  # 刷新以获取ID，但不提交
    db.refresh(portfolio)
    return portfolio

@router.put("/{portfolio_id}", response_model=Portfolio)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新作品（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    portfolio = safe_executor.safe_get_by_id(PortfolioModel, portfolio_id)
    
    if not portfolio:
        raise ResourceNotFoundAPIError("作品", portfolio_id)
    
    # 验证和清理更新数据
    update_data = validate_and_sanitize_input(portfolio_data.dict(exclude_unset=True))
    
    for field, value in update_data.items():
        setattr(portfolio, field, value)
    
    db.flush()  # 刷新但不提交
    db.refresh(portfolio)
    return portfolio

@router.delete("/{portfolio_id}", response_model=MessageResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除作品（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    portfolio = safe_executor.safe_get_by_id(PortfolioModel, portfolio_id)
    
    if not portfolio:
        raise ResourceNotFoundAPIError("作品", portfolio_id)
    
    db.delete(portfolio)
    # 事务装饰器会处理提交
    
    return MessageResponse(message="作品删除成功")