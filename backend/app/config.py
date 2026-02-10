"""
应用配置模块
从环境变量读取配置，提供默认值
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 如果项目根目录没有.env，尝试从当前目录加载
    load_dotenv()

class Settings:
    """应用配置类"""
    
    # ==================== 安全配置 ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production-please")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # ==================== 管理员凭据 ====================
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # ==================== 数据库配置 ====================
    # 注意：项目使用 SQLite，DATABASE_URL 主要用于兼容性，实际路径在 database.py 中处理
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./august_lab.db")
    
    # ==================== 文件存储配置 ====================
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./backend/uploads")
    PRODUCTS_DIR: str = os.getenv("PRODUCTS_DIR", "./backend/products")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
    ALLOWED_EXTENSIONS: set = {".zip", ".jpg", ".png", ".gif", ".svg", ".webp"}
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # ==================== 域名配置 ====================
    DOMAIN: str = os.getenv("DOMAIN", "localhost")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_URL: str = os.getenv("API_URL", "http://localhost:8001")
    
    # ==================== CORS 配置 ====================
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:3001"
    ).split(",")
    
    # ==================== 速率限制配置 ====================
    # 默认 300 次/小时，避免产品监控页轮询过快占满配额导致整站 429
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "300"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1小时
    
    # ==================== 邮件配置 ====================
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    
    # ==================== 监控配置 ====================
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # ==================== 会话配置 ====================
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
    
    # ==================== 环境判断 ====================
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return not self.is_production
    
    def validate(self):
        """验证配置的有效性"""
        errors = []
        
        # 检查生产环境必须配置项
        if self.is_production:
            if self.SECRET_KEY == "change-this-in-production-please":
                errors.append("生产环境必须设置 SECRET_KEY")
            
            if self.ADMIN_PASSWORD == "admin123":
                errors.append("生产环境必须修改默认管理员密码")
            
            if "localhost" in self.ALLOWED_ORIGINS:
                errors.append("生产环境 CORS 配置不应包含 localhost")
        
        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors))

# 创建全局配置实例
settings = Settings()

# 在导入时验证配置（仅在非开发环境）
if settings.is_production:
    try:
        settings.validate()
    except ValueError as e:
        import warnings
        warnings.warn(str(e))
