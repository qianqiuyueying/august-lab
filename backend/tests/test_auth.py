"""认证端点测试：注册、登录、获取当前用户。"""

import pytest


async def test_register_new_user(client):
    """POST /api/auth/register 应成功创建用户并返回。"""
    response = await client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"


async def test_register_duplicate_user(client):
    """重复注册同一用户名应返回 400。"""
    payload = {"username": "duplicate", "password": "secret123"}
    response1 = await client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = await client.post("/api/auth/register", json=payload)
    assert response2.status_code == 400


async def test_login_success(client, test_user):
    """POST /api/auth/login 使用正确凭据应返回 access_token。"""
    _, username, password = test_user
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"]


async def test_login_wrong_password(client, test_user):
    """错误密码应返回 401。"""
    _, username, _ = test_user
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": "wrongpassword"},
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
    """GET /api/auth/me 携带有效 token 应返回用户信息。"""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


async def test_get_me_without_token(client):
    """GET /api/auth/me 不带 token 应返回 401（HTTPBearer 无凭证时）。"""
    response = await client.get("/api/auth/me")
    assert response.status_code in (401, 403)


async def test_get_me_with_invalid_token(client):
    """GET /api/auth/me 带无效 token 应返回 401。"""
    client.headers["Authorization"] = "Bearer invalid.token.here"
    response = await client.get("/api/auth/me")
    assert response.status_code in (401, 403)
