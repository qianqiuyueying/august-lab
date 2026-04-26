import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_about_not_configured(client: AsyncClient):
    """未配置时返回 404。"""
    resp = await client.get("/api/about")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_about(auth_client: AsyncClient, client: AsyncClient):
    """创建后能获取。"""
    resp = await auth_client.put("/api/about", json={
        "eyebrow": "About",
        "title": "关于我们",
        "cover_image": "/images/test.webp",
        "content": "# Hello",
        "content_type": "markdown",
        "tech_stack": '["Python","React"]',
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "关于我们"
    assert data["tech_stack"] == '["Python","React"]'

    # 公开接口获取
    resp = await client.get("/api/about")
    assert resp.status_code == 200
    assert resp.json()["title"] == "关于我们"


@pytest.mark.asyncio
async def test_update_about(auth_client: AsyncClient):
    """更新已存在的记录。"""
    # 先创建
    await auth_client.put("/api/about", json={"title": "初始"})
    # 再更新
    resp = await auth_client.put("/api/about", json={"title": "新标题"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "新标题"


@pytest.mark.asyncio
async def test_update_about_requires_auth(client: AsyncClient):
    """未认证返回 401。"""
    resp = await client.put("/api/about", json={"title": "test"})
    assert resp.status_code == 401
