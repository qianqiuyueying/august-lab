"""Admin content listing tests."""


async def _create_article(auth_client, title: str, status: str, content: str = "Body"):
    response = await auth_client.post(
        "/api/articles",
        json={
            "title": title,
            "content": content,
            "summary": f"{title} summary",
            "status": status,
            "tags": ["ops"],
        },
    )
    assert response.status_code == 201
    return response.json()


async def _create_product(auth_client, title: str, slug: str, status: str):
    response = await auth_client.post(
        "/api/products",
        json={
            "title": title,
            "slug": slug,
            "description": f"{title} description",
            "status": status,
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_admin_articles_require_authentication(client):
    response = await client.get("/api/admin/articles")

    assert response.status_code in (401, 403)


async def test_admin_articles_include_drafts_and_filter_by_status(auth_client):
    await _create_article(auth_client, "Published admin article", "published")
    await _create_article(auth_client, "Draft admin article", "draft")

    response = await auth_client.get("/api/admin/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {item["status"] for item in data["items"]} == {"published", "draft"}

    response = await auth_client.get("/api/admin/articles?status=draft")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Draft admin article"


async def test_admin_articles_search_title_summary_and_content(auth_client):
    await _create_article(auth_client, "Release notes", "draft", content="ordinary body")
    await _create_article(auth_client, "Architecture", "published", content="contains needle term")

    response = await auth_client.get("/api/admin/articles?search=needle")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Architecture"


async def test_admin_products_require_authentication(client):
    response = await client.get("/api/admin/products")

    assert response.status_code in (401, 403)


async def test_admin_products_include_drafts_and_public_products_do_not(auth_client, client):
    await _create_product(auth_client, "Published kit", "published-kit", "published")
    await _create_product(auth_client, "Draft kit", "draft-kit", "draft")

    response = await auth_client.get("/api/admin/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {item["status"] for item in data["items"]} == {"published", "draft"}

    response = await client.get("/api/products")
    public_products = response.json()
    assert response.status_code == 200
    assert [item["title"] for item in public_products] == ["Published kit"]


async def test_admin_products_search_and_status_filter(auth_client):
    await _create_product(auth_client, "Portfolio Pack", "portfolio-pack", "published")
    await _create_product(auth_client, "Internal Template", "internal-template", "draft")

    response = await auth_client.get("/api/admin/products?status=draft&search=internal")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "internal-template"
