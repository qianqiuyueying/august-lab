import asyncio
import hashlib
import pytest
from httpx import ASGITransport, AsyncClient

from app.database import Base, async_session, get_db, engine
from app.utils.security import create_access_token

# --- 在导入 app 前 patch bcrypt 依赖 ---
# auth.py 等路由在模块导入时就绑定了 hash_password/verify_password，
# 所以必须在导入 app 之前替换 security 模块中的函数。
import app.utils.security as _sec


def _test_hash_password(password: str) -> str:
    """测试环境用 SHA256 简单哈希，不依赖 bcrypt。"""
    return hashlib.sha256(password.encode()).hexdigest()


def _test_verify_password(plain_password: str, hashed_password: str) -> bool:
    return _test_hash_password(plain_password) == hashed_password


_sec.hash_password = _test_hash_password
_sec.verify_password = _test_verify_password

# 现在导入 app（路由将使用 patch 后的函数）
from app.main import app

# --- 修复 Pydantic 前向引用 ---
# ArticleOut 通过 TYPE_CHECKING 引用了 UserOut，需要在测试中显式 rebuild
from app.schemas.article import ArticleOut, ArticleListItem
from app.schemas.tag import TagOut
from app.schemas.user import UserOut
ArticleOut.model_rebuild()
ArticleListItem.model_rebuild()


# 测试用内存 SQLite URL
TEST_DATABASE_URL = "sqlite+aiosqlite://"


async def override_get_db():
    """异步生成器依赖：返回测试用的异步 session"""
    async with async_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="function")
async def setup_database():
    """每个测试前：创建所有表；测试后：删除所有表。确保完全隔离。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """返回 AsyncClient，指向测试用 app。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user():
    """创建一个测试用户，返回 (user_id, username, password)。"""
    from app.models.user import User
    from app.database import async_session
    from sqlalchemy import select
    import app.utils.security as _sec

    username = "testuser"
    password = "testpass123"

    async with async_session() as session:
        user = User(username=username, hashed_password=_sec.hash_password(password))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id, user.username, password


@pytest.fixture
async def auth_token(test_user):
    """返回测试用户的认证 token。"""
    _, username, _ = test_user
    token = create_access_token({"sub": username})
    return token


@pytest.fixture
async def auth_client(client, auth_token):
    """返回已认证的 AsyncClient，自动携带 Authorization header。"""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
