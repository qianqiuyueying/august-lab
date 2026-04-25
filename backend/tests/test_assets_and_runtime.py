import io
import zipfile


async def _create_article(auth_client, title: str, tags: list[str], cover_image: str | None = None):
    response = await auth_client.post(
        "/api/articles",
        json={
            "title": title,
            "content": "Article body",
            "summary": f"{title} summary",
            "status": "draft",
            "tags": tags,
            "cover_image": cover_image,
        },
    )
    assert response.status_code == 201
    return response.json()


async def _create_product(auth_client, title: str, slug: str):
    response = await auth_client.post(
        "/api/products",
        json={
            "title": title,
            "slug": slug,
            "description": f"{title} description",
            "status": "published",
        },
    )
    assert response.status_code == 201
    return response.json()


def _zip_bytes(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return buffer.getvalue()


async def test_admin_assets_require_authentication(client):
    response = await client.get("/api/admin/assets")

    assert response.status_code in (401, 403)


async def test_admin_can_upload_list_search_and_delete_image(auth_client, tmp_path, monkeypatch):
    from app.routers import assets

    monkeypatch.setattr(assets, "UPLOADS_DIR", str(tmp_path / "uploads"))

    upload = await auth_client.post(
        "/api/admin/assets/upload",
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\nimage-bytes", "image/png")},
    )
    assert upload.status_code == 201
    asset = upload.json()
    assert asset["kind"] == "image"
    assert asset["original_name"] == "cover.png"
    assert asset["url"].startswith("/uploads/images/")

    listed = await auth_client.get("/api/admin/assets?search=cover")
    assert listed.status_code == 200
    data = listed.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == asset["id"]

    deleted = await auth_client.delete(f"/api/admin/assets/{asset['id']}")
    assert deleted.status_code == 204

    listed = await auth_client.get("/api/admin/assets")
    assert listed.status_code == 200
    assert listed.json()["total"] == 0


async def test_admin_asset_upload_rejects_non_image(auth_client, tmp_path, monkeypatch):
    from app.routers import assets

    monkeypatch.setattr(assets, "UPLOADS_DIR", str(tmp_path / "uploads"))

    response = await auth_client.post(
        "/api/admin/assets/upload",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only image files are allowed"


async def test_article_cover_image_is_saved_and_admin_articles_filter_by_tag(auth_client):
    cover_url = "/uploads/images/cover.png"
    await _create_article(auth_client, "React story", ["react"], cover_url)
    await _create_article(auth_client, "FastAPI story", ["fastapi"], None)

    response = await auth_client.get("/api/admin/articles?tag=react")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "React story"
    assert data["items"][0]["cover_image"] == cover_url
    assert [tag["name"] for tag in data["items"][0]["tags"]] == ["react"]


async def test_product_zip_upload_sets_runtime_url_and_serves_public_product(auth_client, tmp_path, monkeypatch):
    from app.routers import products

    monkeypatch.setattr(products, "PRODUCTS_DIR", str(tmp_path / "products"))
    product = await _create_product(auth_client, "Runnable product", "runnable-product")

    response = await auth_client.post(
        f"/api/products/{product['id']}/upload",
        files={
            "file": (
                "product.zip",
                _zip_bytes({"dist/index.html": "<h1>Runnable</h1>", "dist/app.js": "console.log('ok')"}),
                "application/zip",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["url"] == "/product-runtime/runnable-product/"

    public_product = await auth_client.get("/api/products/runnable-product")
    assert public_product.status_code == 200
    assert public_product.json()["runtime_url"] == "/product-runtime/runnable-product/"


async def test_product_zip_upload_requires_index_html(auth_client, tmp_path, monkeypatch):
    from app.routers import products

    monkeypatch.setattr(products, "PRODUCTS_DIR", str(tmp_path / "products"))
    product = await _create_product(auth_client, "Broken product", "broken-product")

    response = await auth_client.post(
        f"/api/products/{product['id']}/upload",
        files={"file": ("broken.zip", _zip_bytes({"readme.txt": "missing index"}), "application/zip")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "ZIP must contain an index.html file"
