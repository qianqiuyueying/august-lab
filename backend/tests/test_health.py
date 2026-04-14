"""健康检查端点测试。"""


async def test_health_check_returns_ok(client):
    """GET /api/health 应返回 200 和 {"status": "ok"}。"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
