from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import logging
from pathlib import Path

# 设置日志
logger = logging.getLogger(__name__)

# SQLite数据库配置
# 使用项目根目录的数据库文件，避免路径混淆
current_file = Path(__file__).resolve()  # backend/app/database.py
backend_app_dir = current_file.parent     # backend/app
backend_dir = backend_app_dir.parent      # backend
PROJECT_ROOT = backend_dir.parent         # August (项目根目录)
DEFAULT_DB_PATH = PROJECT_ROOT / "august_lab.db"

def _normalize_sqlite_url(db_url: str) -> str:
    if db_url in ("sqlite:///:memory:", "sqlite://"):
        return db_url
    if db_url.startswith("sqlite:////"):
        path_part = db_url[len("sqlite:////"):]
        db_path = (Path("/") / path_part).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:////{db_path.as_posix().lstrip('/')}"
    if db_url.startswith("sqlite:///"):
        path_part = db_url[len("sqlite:///"):]
        db_path = Path(path_part)
        if not db_path.is_absolute():
            db_path = (PROJECT_ROOT / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.as_posix()}"
    return db_url

env_database_url = os.getenv("DATABASE_URL")
if env_database_url:
    SQLALCHEMY_DATABASE_URL = _normalize_sqlite_url(env_database_url)
else:
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

# SQLite使用StaticPool
pool_class = StaticPool
connect_args = {
    "check_same_thread": False,
    "timeout": 30,  # 30秒超时
}
pool_kwargs = {}

# 创建引擎，添加连接池和错误处理配置
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    poolclass=pool_class,
    echo=False,  # 生产环境关闭SQL日志
    **pool_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 标准数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 带错误处理的数据库依赖
def get_db_with_error_handling():
    """带错误处理的数据库会话获取"""
    from .transaction import create_safe_db_dependency
    return create_safe_db_dependency(engine, SessionLocal)

# 数据库健康检查
def check_database_health() -> bool:
    """检查数据库连接健康状态"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return False

# 数据库连接重试机制
def get_db_with_retry(max_retries: int = 3):
    """获取带重试机制的数据库会话"""
    from .transaction import DatabaseConnectionManager
    
    connection_manager = DatabaseConnectionManager(engine, max_retries=max_retries)
    
    def _get_db_with_retry():
        db = None
        try:
            db = connection_manager.get_session_with_retry(SessionLocal)
            yield db
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"关闭数据库会话时出错: {str(e)}")
    
    return _get_db_with_retry