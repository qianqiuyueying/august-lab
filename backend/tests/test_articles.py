"""文章端点测试：CRUD、列表、搜索、分页。"""

import pytest


@pytest.fixture
async def sample_article(auth_client):
    """通过 API 创建一篇测试文章，返回文章数据。"""
    response = await auth_client.post(
        "/api/articles",
        json={
            "title": "Test Article",
            "content": "This is the content of the test article.",
            "summary": "A test article summary.",
            "status": "published",
            "tags": ["test"],
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_create_article(auth_client):
    """POST /api/articles 已认证用户应能创建文章。"""
    response = await auth_client.post(
        "/api/articles",
        json={
            "title": "Hello World",
            "content": "Hello, World!",
            "status": "draft",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hello World"
    assert data["slug"]  # slug 应自动生成
    assert data["status"] == "draft"


async def test_create_article_unauthenticated(client):
    """未认证用户不能创建文章。"""
    response = await client.post(
        "/api/articles",
        json={
            "title": "Unauthorized",
            "content": "This should fail",
            "status": "draft",
        },
    )
    assert response.status_code in (401, 403)


async def test_list_published_articles(client, auth_client):
    """GET /api/articles 应只返回已发布的文章。"""
    # 创建并发布一篇文章
    await auth_client.post(
        "/api/articles",
        json={
            "title": "Published Post",
            "content": "Content here",
            "status": "published",
        },
    )
    # 创建一篇草稿
    await auth_client.post(
        "/api/articles",
        json={
            "title": "Draft Post",
            "content": "Draft content",
            "status": "draft",
        },
    )

    response = await client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Published Post"


async def test_get_article_by_slug(client, sample_article):
    """GET /api/articles/{slug} 应能通过 slug 获取文章详情。"""
    slug = sample_article["slug"]
    response = await client.get(f"/api/articles/{slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == slug
    assert data["title"] == "Test Article"
    assert "content" in data


async def test_get_nonexistent_article(client):
    """获取不存在的文章应返回 404。"""
    response = await client.get("/api/articles/nonexistent-slug")
    assert response.status_code == 404


async def test_update_article(auth_client, sample_article):
    """PUT /api/articles/{id} 应能更新文章。"""
    article_id = sample_article["id"]
    response = await auth_client.put(
        f"/api/articles/{article_id}",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


async def test_delete_article(auth_client, sample_article):
    """DELETE /api/articles/{id} 应能删除文章。"""
    article_id = sample_article["id"]
    response = await auth_client.delete(f"/api/articles/{article_id}")
    assert response.status_code == 204

    # 确认已删除
    response = await auth_client.get(f"/api/articles/{sample_article['slug']}")
    assert response.status_code == 404


async def test_article_pagination(client):
    """分页参数应正常工作。"""
    response = await client.get("/api/articles?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5


async def test_article_search(client, auth_client):
    """搜索参数应能匹配文章标题和内容。"""
    await auth_client.post(
        "/api/articles",
        json={
            "title": "Unique Searchable Title",
            "content": "Some content",
            "status": "published",
        },
    )

    response = await client.get("/api/articles?search=Unique+Searchable")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Unique Searchable Title"

    # 搜索不存在的关键词应返回空
    response = await client.get("/api/articles?search=NoSuchArticle")
    data = response.json()
    assert data["total"] == 0
