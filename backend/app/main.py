import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import articles, tags, comments, auth, pages, settings, products

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
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(pages.router, prefix="/api/pages", tags=["pages"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(products.router, prefix="/api/products", tags=["products"])

# 挂载产品静态文件目录
products_dir = "/app/products"
if os.path.isdir(products_dir):
    app.mount("/products", StaticFiles(directory=products_dir, html=True), name="products")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
