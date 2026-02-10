from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from datetime import datetime, timezone

from app.database import engine, Base
from app import models  # 导入模型以确保它们被注册到 Base.metadata
from app.routers import auth, portfolio, blog, profile, upload, products
from app.database_init import init_database
from app.error_handlers import setup_error_handlers, request_id_middleware
from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware

# 初始化数据库（包含表创建和示例数据）
try:
    init_database()
except Exception as e:
    print(f"数据库初始化警告: {e}")
    # 如果初始化失败，至少确保表被创建
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="August.Lab API",
    description="个人网站后端API",
    version="1.0.0"
)

# 设置全局错误处理器
setup_error_handlers(app)

# 添加请求ID中间件
app.middleware("http")(request_id_middleware)

# GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 速率限制中间件
app.add_middleware(
    RateLimitMiddleware,
    requests_per_window=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
# 使用配置中的路径
from pathlib import Path
backend_dir = Path(__file__).parent  # backend 目录

# 从配置读取路径，如果是相对路径则基于backend目录
# 使用 pathlib.Path 处理路径，自动支持跨平台
upload_dir_path = Path(settings.UPLOAD_DIR)
if upload_dir_path.is_absolute():
    uploads_dir = upload_dir_path
else:
    # 处理相对路径，移除开头的 ./ 或 .\ 等（跨平台兼容）
    upload_dir_str = settings.UPLOAD_DIR.lstrip("./").lstrip(".\\").lstrip(".")
    # 如果还有路径分隔符，移除它
    if upload_dir_str.startswith(('/', '\\')):
        upload_dir_str = upload_dir_str[1:]
    uploads_dir = backend_dir.parent / upload_dir_str

products_dir_path = Path(settings.PRODUCTS_DIR)
if products_dir_path.is_absolute():
    products_dir = products_dir_path
else:
    # 处理相对路径，移除开头的 ./ 或 .\ 等（跨平台兼容）
    products_dir_str = settings.PRODUCTS_DIR.lstrip("./").lstrip(".\\").lstrip(".")
    # 如果还有路径分隔符，移除它
    if products_dir_str.startswith(('/', '\\')):
        products_dir_str = products_dir_str[1:]
    products_dir = backend_dir.parent / products_dir_str

# 确保目录存在
uploads_dir.mkdir(parents=True, exist_ok=True)
products_dir.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
app.mount("/products", StaticFiles(directory=str(products_dir)), name="products")

# 初始化扩展系统
try:
    from app.services.product_extension_service import product_extension_service
    loaded_count = product_extension_service.load_extensions_from_directory()
    print(f"扩展系统初始化完成，加载了 {loaded_count} 个扩展")
except Exception as e:
    print(f"扩展系统初始化失败: {e}")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["作品管理"])
app.include_router(blog.router, prefix="/api/blog", tags=["博客管理"])
app.include_router(profile.router, prefix="/api/profile", tags=["个人信息"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(products.router, prefix="/api/products", tags=["产品管理"])

@app.get("/health")
async def health_check():
    from app.database import check_database_health
    db_healthy = check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# 前端 SPA 目录：Docker 内为 /app/frontend/dist，本地/其他环境用项目下的 frontend/dist
_spa_candidates = [
    Path("/app/frontend/dist"),
    backend_dir.parent / "frontend" / "dist",
]
spa_dir = next((d for d in _spa_candidates if d.exists()), None)


def _spa_file_path(relative_path: str) -> Path | None:
    """解析 SPA 静态文件路径，防止路径穿越；不存在或非法则返回 None。"""
    if not spa_dir or not relative_path:
        return None
    # 规范路径，禁止 ..
    parts = Path(relative_path).parts
    if ".." in parts or relative_path.startswith("/"):
        return None
    full = (spa_dir / relative_path).resolve()
    try:
        full.resolve().relative_to(spa_dir.resolve())
    except ValueError:
        return None
    return full if full.is_file() else None


# 前端 SPA 回退：必须放在最后注册，保证 /api、/health、/uploads、/products 先匹配
if spa_dir and (spa_dir / "index.html").exists():
    @app.get("/{path:path}", response_class=FileResponse, include_in_schema=False)
    async def spa_fallback(path: str):
        # 先尝试作为静态文件（如 /assets/xxx.js）
        if path:
            file_path = _spa_file_path(path)
            if file_path:
                return FileResponse(str(file_path))
        # 否则返回 index.html（Vue Router 前端路由）
        index_path = spa_dir / "index.html"
        if not index_path.exists():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="SPA index not found")
        return FileResponse(str(index_path))
else:
    @app.get("/")
    async def root():
        return {"message": "August.Lab API Server"}


@app.on_event("startup")
async def _log_routes():
    """启动时输出 SPA 目录与路由情况，便于排查 404。"""
    import logging
    log = logging.getLogger("uvicorn.error")
    log.info(f"SPA directory: {spa_dir} (exists={spa_dir is not None and spa_dir.exists() if spa_dir else False})")
    if spa_dir:
        log.info(f"SPA index.html exists: {(spa_dir / 'index.html').exists()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)