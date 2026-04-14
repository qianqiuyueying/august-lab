"""评论端点测试。"""

import pytest


@pytest.fixture
async def article_with_comments(auth_client):
    """创建一篇已发布的文章，返回文章 ID 和 slug。"""
    response = await auth_client.post(
        "/api/articles",
        json={
            "title": "Comment Test Article",
            "content": "Content",
            "status": "published",
        },
    )
    data = response.json()
    return data["id"], data["slug"]


async def test_list_comments_empty(client, article_with_comments):
    """新文章应没有评论。"""
    article_id, _ = article_with_comments
    response = await client.get(f"/api/articles/{article_id}/comments")
    assert response.status_code == 200
    assert response.json() == []


async def test_add_comment(client, article_with_comments):
    """POST 应能添加评论。"""
    article_id, _ = article_with_comments
    response = await client.post(
        f"/api/articles/{article_id}/comments",
        json={
            "author_name": "Test User",
            "author_email": "test@example.com",
            "content": "Nice article!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["author_name"] == "Test User"
    assert data["content"] == "Nice article!"


async def test_list_comments_after_adding(client, article_with_comments):
    """添加评论后，列表端点应返回评论。"""
    article_id, _ = article_with_comments
    # 先添加评论
    await client.post(
        f"/api/articles/{article_id}/comments",
        json={
            "author_name": "User",
            "author_email": "user@example.com",
            "content": "Great!",
        },
    )

    response = await client.get(f"/api/articles/{article_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 1
    assert comments[0]["content"] == "Great!"


async def test_comment_on_nonexistent_article(client):
    """对不存在的文章添加评论应返回 404。"""
    response = await client.post(
        "/api/articles/99999/comments",
        json={
            "author_name": "User",
            "author_email": "user@example.com",
            "content": "Hello",
        },
    )
    assert response.status_code == 404
