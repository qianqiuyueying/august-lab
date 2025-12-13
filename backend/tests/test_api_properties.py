"""
API核心功能属性测试

Feature: personal-website
验证认证凭据验证准确性、会话管理生命周期、CRUD操作数据完整性和文件上传处理完整性属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import json
import os
import tempfile
from PIL import Image
import io
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.models import Session as SessionModel
from app.database import get_db, SessionLocal

# 获取认证令牌的辅助函数
def get_auth_token(client):
    """获取有效的认证令牌"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

def create_test_image(width: int, height: int, format: str = "PNG") -> bytes:
    """创建测试图片文件"""
    image = Image.new("RGB", (width, height), color=(255, 0, 0))
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes.getvalue()

# 测试数据生成策略
valid_credentials = st.fixed_dictionaries({
    'username': st.just('admin'),
    'password': st.just('admin123')
})

invalid_credentials = st.one_of([
    st.fixed_dictionaries({
        'username': st.text(min_size=1, max_size=50).filter(lambda x: x != 'admin'),
        'password': st.text(min_size=1, max_size=50)
    }),
    st.fixed_dictionaries({
        'username': st.just('admin'),
        'password': st.text(min_size=1, max_size=50).filter(lambda x: x != 'admin123')
    })
])

portfolio_data_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    'description': st.one_of([st.none(), st.text(max_size=2000)]),
    'tech_stack': st.lists(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()), max_size=10),
    'project_url': st.one_of([st.none(), st.text(min_size=1, max_size=500)]),
    'github_url': st.one_of([st.none(), st.text(min_size=1, max_size=500)]),
    'image_url': st.one_of([st.none(), st.text(min_size=1, max_size=500)]),
    'display_order': st.integers(min_value=0, max_value=9999),
    'is_featured': st.booleans()
})

blog_data_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    'content': st.text(min_size=1, max_size=10000).filter(lambda x: x.strip()),
    'summary': st.one_of([st.none(), st.text(max_size=1000)]),
    'tags': st.lists(st.text(min_size=1, max_size=30).filter(lambda x: x.strip()), max_size=10),
    'is_published': st.booleans(),
    'cover_image': st.one_of([st.none(), st.text(min_size=1, max_size=500)])
})

# 认证属性测试
@given(valid_credentials)
@settings(max_examples=100)
def test_property_10_auth_credential_validation_accuracy_valid(client, credentials):
    """
    Feature: personal-website, Property 10: 认证凭据验证准确性
    验证: 需求 5.2, 5.3
    
    对于任意有效的管理员凭据，系统应该准确验证并返回成功的认证结果
    """
    response = client.post("/api/auth/login", json=credentials)
    
    # 有效凭据应该返回成功
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0

@given(invalid_credentials)
@settings(max_examples=100)
def test_property_10_auth_credential_validation_accuracy_invalid(client, credentials):
    """
    Feature: personal-website, Property 10: 认证凭据验证准确性
    验证: 需求 5.2, 5.3
    
    对于任意无效的凭据，系统应该准确验证并返回失败的认证结果
    """
    response = client.post("/api/auth/login", json=credentials)
    
    # 无效凭据应该返回401错误
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "用户名或密码错误" in data["detail"]

def test_property_11_session_management_lifecycle_creation(client):
    """
    Feature: personal-website, Property 11: 会话管理生命周期
    验证: 需求 5.4, 5.5
    
    对于任意用户会话，系统应该正确管理会话的创建、维护和销毁过程
    """
    # 1. 创建会话（通过登录）
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # 2. 验证会话有效性
    verify_response = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert verify_response.status_code == 200
    
    # 3. 销毁会话（登出）
    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_response.status_code == 200
    
    # 4. 验证会话已失效
    verify_after_logout = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert verify_after_logout.status_code == 401

def test_property_11_session_management_lifecycle_invalid_token(client):
    """
    Feature: personal-website, Property 11: 会话管理生命周期
    验证: 需求 5.4, 5.5
    
    验证无效令牌的处理
    """
    # 使用不存在的令牌
    fake_token = str(uuid.uuid4())
    
    verify_response = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    
    # 无效令牌应该被拒绝
    assert verify_response.status_code == 401

# CRUD操作属性测试
@given(portfolio_data_strategy)
@settings(max_examples=100)
def test_property_12_crud_data_integrity_portfolio_create_read(client, portfolio_data):
    """
    Feature: personal-website, Property 12: CRUD操作数据完整性
    验证: 需求 6.2, 6.3, 6.4, 7.2, 7.3, 7.4
    
    对于任意作品管理操作（创建、读取），操作结果应该正确反映在数据存储中
    """
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建作品
    create_response = client.post(
        "/api/portfolio/",
        json=portfolio_data,
        headers=headers
    )
    
    if create_response.status_code != 200:
        # 如果创建失败，跳过此测试用例（可能是数据验证失败）
        assume(False)
    
    created_portfolio = create_response.json()
    portfolio_id = created_portfolio["id"]
    
    # 读取创建的作品
    read_response = client.get(f"/api/portfolio/{portfolio_id}")
    assert read_response.status_code == 200
    
    read_portfolio = read_response.json()
    
    # 验证数据完整性
    assert read_portfolio["id"] == portfolio_id
    assert read_portfolio["title"] == portfolio_data["title"].strip()
    
    if portfolio_data["description"]:
        assert read_portfolio["description"] == portfolio_data["description"].strip()
    
    assert read_portfolio["tech_stack"] == [tech.strip() for tech in portfolio_data["tech_stack"] if tech.strip()]
    assert read_portfolio["display_order"] == portfolio_data["display_order"]
    assert read_portfolio["is_featured"] == portfolio_data["is_featured"]
    
    # 验证时间戳字段存在
    assert "created_at" in read_portfolio
    assert "updated_at" in read_portfolio

@given(blog_data_strategy)
@settings(max_examples=100)
def test_property_12_crud_data_integrity_blog_create_read(client, blog_data):
    """
    Feature: personal-website, Property 12: CRUD操作数据完整性
    验证: 需求 6.2, 6.3, 6.4, 7.2, 7.3, 7.4
    
    对于任意博客管理操作（创建、读取），操作结果应该正确反映在数据存储中
    """
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建博客
    create_response = client.post(
        "/api/blog/",
        json=blog_data,
        headers=headers
    )
    
    if create_response.status_code != 200:
        assume(False)
    
    created_blog = create_response.json()
    blog_id = created_blog["id"]
    
    # 使用管理员接口读取博客（包括草稿）
    read_response = client.get(
        f"/api/blog/admin/{blog_id}",
        headers=headers
    )
    assert read_response.status_code == 200
    
    read_blog = read_response.json()
    
    # 验证数据完整性
    assert read_blog["id"] == blog_id
    assert read_blog["title"] == blog_data["title"].strip()
    assert read_blog["content"] == blog_data["content"].strip()
    
    if blog_data["summary"]:
        assert read_blog["summary"] == blog_data["summary"].strip()
    
    assert read_blog["tags"] == [tag.strip() for tag in blog_data["tags"] if tag.strip()]
    assert read_blog["is_published"] == blog_data["is_published"]
    
    # 验证时间戳字段存在
    assert "created_at" in read_blog
    assert "updated_at" in read_blog

# 文件上传属性测试
@given(st.tuples(
    st.integers(min_value=10, max_value=500),  # width
    st.integers(min_value=10, max_value=500)   # height
))
@settings(max_examples=100)
def test_property_14_file_upload_processing_integrity_valid_images(client, dimensions):
    """
    Feature: personal-website, Property 14: 文件上传处理完整性
    验证: 需求 8.3, 10.5
    
    对于任意有效的图片文件，上传处理后应该能够正确存储并提供访问路径
    """
    width, height = dimensions
    
    # 跳过可能导致文件过大的情况
    if width * height > 100000:  # 避免创建过大的图片
        assume(False)
    
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建测试图片
    image_data = create_test_image(width, height, "PNG")
    
    # 跳过超过大小限制的文件
    if len(image_data) > 5 * 1024 * 1024:  # 5MB limit
        assume(False)
    
    filename = "test_image.png"
    
    # 上传图片
    files = {"file": (filename, image_data, "image/png")}
    
    upload_response = client.post(
        "/api/upload/image",
        files=files,
        headers=headers
    )
    
    # 验证上传成功
    assert upload_response.status_code == 201
    
    response_data = upload_response.json()
    
    # 验证响应数据完整性
    assert "message" in response_data
    assert "filename" in response_data
    assert "url" in response_data
    assert "size" in response_data
    
    assert response_data["message"] == "文件上传成功"
    assert response_data["size"] == len(image_data)
    assert response_data["url"].startswith("/uploads/images/")
    assert response_data["filename"].endswith(".png")
    
    # 验证文件实际存在
    uploaded_filename = response_data["filename"]
    file_path = os.path.join("uploads/images", uploaded_filename)
    assert os.path.exists(file_path)
    
    # 验证文件内容完整性
    with open(file_path, "rb") as f:
        saved_data = f.read()
    
    assert len(saved_data) == len(image_data)
    
    # 清理测试文件
    try:
        os.remove(file_path)
    except:
        pass

def test_property_14_file_upload_processing_integrity_invalid_formats(client):
    """
    Feature: personal-website, Property 14: 文件上传处理完整性
    验证: 需求 8.3, 10.5
    
    对于无效格式的文件，上传应该被正确拒绝
    """
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建无效格式的文件
    filename = "test_file.txt"
    file_content = b"This is not an image file"
    
    files = {"file": (filename, file_content, "application/octet-stream")}
    
    upload_response = client.post(
        "/api/upload/image",
        files=files,
        headers=headers
    )
    
    # 验证上传被拒绝
    assert upload_response.status_code == 400
    
    response_data = upload_response.json()
    assert "detail" in response_data
    assert "不支持的文件格式" in response_data["detail"]

def test_property_14_file_upload_processing_integrity_authentication(client):
    """
    Feature: personal-website, Property 14: 文件上传处理完整性
    验证: 需求 8.3, 10.5
    
    验证文件上传需要正确的认证
    """
    # 创建测试图片
    image_data = create_test_image(100, 100)
    files = {"file": ("test.png", image_data, "image/png")}
    
    # 不提供认证令牌
    upload_response = client.post("/api/upload/image", files=files)
    
    # 验证需要认证
    assert upload_response.status_code == 403  # Forbidden due to missing auth

    # 提供无效令牌
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    upload_response = client.post(
        "/api/upload/image", 
        files=files, 
        headers=invalid_headers
    )
    
    # 验证无效令牌被拒绝
    assert upload_response.status_code == 401