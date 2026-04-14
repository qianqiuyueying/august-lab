# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供在本代码库中工作的指引。

## 项目概述

技术博客平台，后端采用 FastAPI + SQLite，前端采用 React + TypeScript + Vite。

## 常用命令

### 后端（使用 `uv` 管理 Python 环境）

```bash
cd backend

# 启动开发服务器（热重载）
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 安装依赖
uv pip install -r requirements.txt

# 数据库迁移
uv run alembic revision --autogenerate -m "描述"
uv run alembic upgrade head
uv run alembic downgrade -1
```

### 前端

```bash
cd frontend

# 开发服务器
npm run dev

# 构建 + 类型检查
npm run build

# 代码检查
npm run lint

# 预览生产构建
npm run preview
```

### 根目录（同时启动前后端）

```bash
npm install              # 安装 concurrently
npm run dev              # 同时启动后端和前端
```

## 架构说明

### 后端 (`backend/app/`)

- **`main.py`** — FastAPI 应用入口。挂载各路由，路径前缀为 `/api/*`。跨域配置针对 `localhost:5173`。
- **`config.py`** — Pydantic 设置，环境变量前缀为 `BLOG_`。关键配置：`DATABASE_URL`、`SECRET_KEY`、`ACCESS_TOKEN_EXPIRE_MINUTES`。
- **`database.py`** — SQLAlchemy 异步引擎 + 会话工厂。`Base` 类供 ORM 模型继承。`get_db()` 异步生成器依赖。
- **`dependencies.py`** — `get_current_user` 依赖，用于 JWT 认证（读取 `Authorization: Bearer <token>` 请求头）。
- **`models/`** — ORM 模型：`user`、`article`、`tag`、`comment`、`page`、`article_tag`（多对多关联表）。
- **`schemas/`** — Pydantic 请求/响应模式。`article.py` 中同时定义了 `TagOut`（避免循环导入）。
- **`routers/`** — API 端点：`auth`（注册/登录/获取当前用户）、`articles`（增删改查 + 搜索 + 分页）、`tags`、`comments`、`pages`（静态页面管理）。
- **`utils/`** — `security.py`（JWT + bcrypt）、`slug.py`（URL 友好路径生成）。

需要认证的端点使用 `Depends(get_current_user)`。公开端点（文章列表、文章详情、评论、页面）无需认证。

### 前端 (`frontend/src/`)

- **`App.tsx`** — React Router 配置。`:slug` 通配路由映射到 `StaticPage`，具体路由必须置于其前。
- **`api/client.ts`** — Axios 实例，`/api` 基础路径，JWT 拦截器，401 自动跳转 `/login`。
- **`contexts/AuthContext.tsx`** — 全局认证状态（`user`、`token`、`login`、`logout`）。
- **`hooks/`** — `useArticles`（列表 + 单篇 + 变更操作）、`useTags`、`useComments`（列表 + 添加）。
- **`components/`** — Markdown 渲染使用 `react-markdown` + `remark-gfm` + `rehype-highlight`。编辑器带实时预览切换。
- **`types/index.ts`** — 共享 TypeScript 接口，与后端 Pydantic 模式对应。
- **`vite.config.ts`** — Vite 代理将 `/api` 转发至 `localhost:8000`（开发环境无需 CORS）。

### 数据库

SQLite + SQLAlchemy 异步。Alembic 管理迁移。数据表：`users`、`articles`、`tags`、`article_tags`、`comments`、`pages`。数据库文件位于 `backend/blog.db`。
