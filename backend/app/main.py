import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings as app_settings
from app.routers import admin, articles, assets, auth, about, dashboard, products, settings, tags

app = FastAPI(
    title="Blog API",
    description="A technical blog platform built with FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(about.router, prefix="/api/about", tags=["about"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(assets.router, prefix="/api/admin", tags=["admin-assets"])

products_dir = app_settings.PRODUCTS_DIR
os.makedirs(products_dir, exist_ok=True)
app.mount("/product-runtime", StaticFiles(directory=products_dir, html=True), name="product-runtime")

uploads_dir = app_settings.UPLOADS_DIR
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
