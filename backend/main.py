from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime

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
if os.path.isabs(settings.UPLOAD_DIR):
    uploads_dir = Path(settings.UPLOAD_DIR)
else:
    uploads_dir = backend_dir.parent / settings.UPLOAD_DIR.lstrip("./")

if os.path.isabs(settings.PRODUCTS_DIR):
    products_dir = Path(settings.PRODUCTS_DIR)
else:
    products_dir = backend_dir.parent / settings.PRODUCTS_DIR.lstrip("./")

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

@app.get("/")
async def root():
    return {"message": "August.Lab API Server"}

@app.get("/health")
async def health_check():
    from app.database import check_database_health
    
    db_healthy = check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)