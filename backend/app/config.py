from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./blog.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    DEBUG: bool = True
    UPLOADS_DIR: str = "uploads"
    PRODUCTS_DIR: str = "products"

    # 管理员认证，通过环境变量 BLOG_ADMIN_USERNAME / BLOG_ADMIN_PASSWORD 设置。
    ADMIN_USERNAME: str = Field(...)
    ADMIN_PASSWORD: str = Field(...)

    model_config = {"env_prefix": "BLOG_", "extra": "ignore"}


settings = Settings()
