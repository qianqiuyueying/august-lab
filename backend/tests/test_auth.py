"""认证端点测试：登录、获取当前用户。"""

import pytest


async def test_login_success(client):
    """POST /api/auth/login 使用正确凭据应返回 access_token。"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"]


async def test_login_wrong_password(client):
    """错误密码应返回 401。"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_nonexistent_user(client):
    """不存在的用户名应返回 401。"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "ghost", "password": "secret"},
    )
    assert response.status_code == 401


async def test_get_me_with_valid_token(client, auth_token):
    """GET /api/auth/me 携带有效 token 应返回管理员信息。"""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] == 1


async def test_get_me_without_token(client):
    """GET /api/auth/me 不带 token 应返回 401（HTTPBearer 无凭证时）。"""
    response = await client.get("/api/auth/me")
    assert response.status_code in (401, 403, 422)


async def test_get_me_with_invalid_token(client):
    """GET /api/auth/me 带无效 token 应返回 401。"""
    client.headers["Authorization"] = "Bearer invalid.token.here"
    response = await client.get("/api/auth/me")
    assert response.status_code in (401, 403, 422)
