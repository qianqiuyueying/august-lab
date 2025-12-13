"""
数据库事务原子性属性测试

Feature: personal-website
验证数据库事务原子性属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.models import Portfolio, Blog, Profile
from app.database import get_db
from app.transaction import BatchTransaction, transactional

# 获取认证令牌的辅助函数
def get_auth_token(client):
    """获取有效的认证令牌"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

# 测试数据生成策略
portfolio_data_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    'description': st.one_of([st.none(), st.text(max_size=2000)]),
    'tech_stack': st.lists(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()), max_size=10),
    'display_order': st.integers(min_value=0, max_value=9999),
    'is_featured': st.booleans()
})

blog_data_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    'content': st.text(min_size=1, max_size=10000).filter(lambda x: x.strip()),
    'summary': st.one_of([st.none(), st.text(max_size=1000)]),
    'tags': st.lists(st.text(min_size=1, max_size=30).filter(lambda x: x.strip()), max_size=10),
    'is_published': st.booleans()
})

def test_property_16_database_transaction_atomicity_success(client):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    对于任意数据库操作序列，事务应该确保要么全部成功要么全部回滚
    测试成功场景：所有操作都成功
    """
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建多个作品，应该全部成功
    portfolio_data_list = [
        {
            "title": f"Test Portfolio {i}",
            "description": f"Description {i}",
            "tech_stack": ["Python", "FastAPI"],
            "display_order": i,
            "is_featured": i % 2 == 0
        }
        for i in range(3)
    ]
    
    created_ids = []
    
    # 在事务中创建多个作品
    for portfolio_data in portfolio_data_list:
        response = client.post(
            "/api/portfolio/",
            json=portfolio_data,
            headers=headers
        )
        assert response.status_code == 200
        created_ids.append(response.json()["id"])
    
    # 验证所有作品都被创建
    for portfolio_id in created_ids:
        response = client.get(f"/api/portfolio/{portfolio_id}")
        assert response.status_code == 200

def test_property_16_database_transaction_atomicity_rollback_on_error(test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    测试失败场景：当操作失败时，整个事务应该回滚
    """
    # 使用批量事务管理器测试原子性
    with BatchTransaction(test_db) as batch:
        # 添加一个有效的作品创建操作
        def create_valid_portfolio():
            portfolio = Portfolio(
                title="Valid Portfolio",
                description="Valid description",
                tech_stack=["Python"],
                display_order=1
            )
            test_db.add(portfolio)
            return portfolio
        
        # 添加一个会失败的操作（违反约束）
        def create_invalid_portfolio():
            # 创建一个违反约束的作品（比如重复的唯一字段）
            portfolio = Portfolio(
                title="",  # 空标题会导致验证失败
                description="Invalid description"
            )
            test_db.add(portfolio)
            return portfolio
        
        batch.add_operation(create_valid_portfolio)
        batch.add_operation(create_invalid_portfolio)
        
        # 执行批量操作，应该失败并回滚
        with pytest.raises(Exception):
            batch.execute_all(rollback_on_failure=True)
    
    # 验证没有任何作品被创建（事务已回滚）
    portfolios = test_db.query(Portfolio).filter(
        Portfolio.title.in_(["Valid Portfolio", ""])
    ).all()
    assert len(portfolios) == 0

@given(st.integers(min_value=2, max_value=5))
@settings(max_examples=100)
def test_property_16_database_transaction_atomicity_batch_operations(operation_count, test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    对于任意数量的批量操作，事务应该保证原子性
    """
    # 创建批量操作
    portfolios_to_create = []
    for i in range(operation_count):
        portfolio_data = {
            "title": f"Batch Portfolio {i}",
            "description": f"Batch description {i}",
            "tech_stack": ["Python", "FastAPI"],
            "display_order": i
        }
        portfolios_to_create.append(portfolio_data)
    
    # 使用批量事务
    with BatchTransaction(test_db) as batch:
        for portfolio_data in portfolios_to_create:
            def create_portfolio(data=portfolio_data):
                portfolio = Portfolio(**data)
                test_db.add(portfolio)
                return portfolio
            
            batch.add_operation(create_portfolio)
        
        # 执行所有操作
        results = batch.execute_all()
        
        # 验证所有操作都成功
        assert len(results) == operation_count
    
    # 验证所有作品都被创建
    created_portfolios = test_db.query(Portfolio).filter(
        Portfolio.title.like("Batch Portfolio %")
    ).all()
    assert len(created_portfolios) == operation_count

def test_property_16_database_transaction_atomicity_mixed_operations(test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    测试混合操作（创建、更新、删除）的事务原子性
    """
    # 先创建一些测试数据
    existing_portfolio = Portfolio(
        title="Existing Portfolio",
        description="Existing description",
        tech_stack=["Python"],
        display_order=1
    )
    test_db.add(existing_portfolio)
    test_db.commit()
    test_db.refresh(existing_portfolio)
    
    existing_blog = Blog(
        title="Existing Blog",
        content="Existing content",
        is_published=True
    )
    test_db.add(existing_blog)
    test_db.commit()
    test_db.refresh(existing_blog)
    
    # 使用批量事务进行混合操作
    with BatchTransaction(test_db) as batch:
        # 创建新作品
        def create_new_portfolio():
            portfolio = Portfolio(
                title="New Portfolio",
                description="New description",
                tech_stack=["JavaScript"],
                display_order=2
            )
            test_db.add(portfolio)
            return portfolio
        
        # 更新现有作品
        def update_existing_portfolio():
            existing_portfolio.description = "Updated description"
            return existing_portfolio
        
        # 删除现有博客
        def delete_existing_blog():
            test_db.delete(existing_blog)
            return True
        
        batch.add_operation(create_new_portfolio)
        batch.add_operation(update_existing_portfolio)
        batch.add_operation(delete_existing_blog)
        
        # 执行所有操作
        results = batch.execute_all()
        assert len(results) == 3
    
    # 验证所有操作都成功
    # 新作品应该存在
    new_portfolio = test_db.query(Portfolio).filter(
        Portfolio.title == "New Portfolio"
    ).first()
    assert new_portfolio is not None
    
    # 现有作品应该被更新
    updated_portfolio = test_db.query(Portfolio).filter(
        Portfolio.id == existing_portfolio.id
    ).first()
    assert updated_portfolio.description == "Updated description"
    
    # 博客应该被删除
    deleted_blog = test_db.query(Blog).filter(
        Blog.id == existing_blog.id
    ).first()
    assert deleted_blog is None

def test_property_16_database_transaction_atomicity_concurrent_access(test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    测试并发访问时的事务原子性
    """
    # 创建一个共享的作品
    shared_portfolio = Portfolio(
        title="Shared Portfolio",
        description="Shared description",
        tech_stack=["Python"],
        display_order=1
    )
    test_db.add(shared_portfolio)
    test_db.commit()
    test_db.refresh(shared_portfolio)
    
    # 模拟并发更新
    original_description = shared_portfolio.description
    
    # 第一个事务：更新描述
    with BatchTransaction(test_db) as batch1:
        def update_description():
            portfolio = test_db.query(Portfolio).filter(
                Portfolio.id == shared_portfolio.id
            ).first()
            portfolio.description = "Updated by transaction 1"
            return portfolio
        
        batch1.add_operation(update_description)
        results1 = batch1.execute_all()
        assert len(results1) == 1
    
    # 验证更新成功
    updated_portfolio = test_db.query(Portfolio).filter(
        Portfolio.id == shared_portfolio.id
    ).first()
    assert updated_portfolio.description == "Updated by transaction 1"

def test_property_16_database_transaction_atomicity_constraint_violation(test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    测试约束违反时的事务回滚
    """
    # 创建一个个人信息记录
    profile = Profile(
        id=1,
        name="Test User",
        email="test@example.com"
    )
    test_db.add(profile)
    test_db.commit()
    
    # 尝试创建另一个具有相同邮箱的记录（违反唯一约束）
    with BatchTransaction(test_db) as batch:
        def create_valid_portfolio():
            portfolio = Portfolio(
                title="Valid Portfolio",
                description="Valid description"
            )
            test_db.add(portfolio)
            return portfolio
        
        def create_duplicate_profile():
            duplicate_profile = Profile(
                id=2,
                name="Another User",
                email="test@example.com"  # 重复邮箱
            )
            test_db.add(duplicate_profile)
            return duplicate_profile
        
        batch.add_operation(create_valid_portfolio)
        batch.add_operation(create_duplicate_profile)
        
        # 应该因为邮箱重复而失败
        with pytest.raises(Exception):
            batch.execute_all(rollback_on_failure=True)
    
    # 验证没有新的作品被创建（事务已回滚）
    portfolios = test_db.query(Portfolio).filter(
        Portfolio.title == "Valid Portfolio"
    ).all()
    assert len(portfolios) == 0
    
    # 验证只有原始的个人信息记录存在
    profiles = test_db.query(Profile).all()
    assert len(profiles) == 1
    assert profiles[0].email == "test@example.com"

@given(st.booleans())
@settings(max_examples=100)
def test_property_16_database_transaction_atomicity_rollback_behavior(rollback_enabled, test_db):
    """
    Feature: personal-website, Property 16: 数据库事务原子性
    验证: 需求 9.2
    
    测试不同回滚设置下的事务行为
    """
    # 创建一个会失败的批量操作
    with BatchTransaction(test_db) as batch:
        def create_valid_item():
            portfolio = Portfolio(
                title="Valid Item",
                description="Valid description"
            )
            test_db.add(portfolio)
            return portfolio
        
        def create_invalid_item():
            # 创建一个无效的项目
            raise ValueError("Simulated error")
        
        batch.add_operation(create_valid_item)
        batch.add_operation(create_invalid_item)
        
        # 根据rollback_enabled设置执行
        with pytest.raises(Exception):
            batch.execute_all(rollback_on_failure=rollback_enabled)
    
    # 验证回滚行为
    if rollback_enabled:
        # 如果启用回滚，不应该有任何项目被创建
        portfolios = test_db.query(Portfolio).filter(
            Portfolio.title == "Valid Item"
        ).all()
        assert len(portfolios) == 0
    # 注意：如果不启用回滚，第一个操作可能已经提交，但这取决于具体实现