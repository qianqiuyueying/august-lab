"""
pytest 配置文件
提供测试所需的 fixtures 和配置
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app import models  # 导入所有模型以确保它们被注册到 Base.metadata
from main import app

# 使用临时文件数据库进行测试（避免多线程问题）
import tempfile
import os
TEST_DATABASE_URL = "sqlite:///./test_temp.db"

@pytest.fixture(scope="function")
def test_engine():
    """创建测试数据库引擎"""
    # 清理可能存在的测试数据库文件（跨平台）
    test_db_path = Path("test_temp.db")
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except:
            pass
    
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    # 确保所有模型都被导入
    from app.models import Portfolio, Blog, Profile, Session
    # 强制重新创建所有表
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # 清理（跨平台）
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    test_db_path = Path("test_temp.db")
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except:
            pass

@pytest.fixture(scope="function")
def test_db(test_engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(test_engine):
    """创建测试客户端"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """获取认证头部"""
    # 使用硬编码的管理员凭据登录
    login_data = {"username": "admin", "password": "admin123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}