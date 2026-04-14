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

## 编码规范

### 后端

- **路由直接写在 router 文件顶层**，不要用类封装。每个端点是一个 async 函数。
- **数据库查询统一用 `select()` + `scalar_one_or_none()` 模式**。关联数据用 `selectinload()` 预加载。
- **commit 后必须 `db.refresh(entity)`**，确保返回对象包含最新 DB 数据。
- **错误处理**：统一用 `HTTPException(status_code=..., detail="...")`，不要在 router 里 try/except 吞异常。
- **认证**：需要登录的端点加 `current_user: User = Depends(get_current_user)` 参数，公开端点不加。
- **环境变量**：全部通过 `app.config.settings` 读取，前缀为 `BLOG_`。不要直接 `os.environ`。
- **slug 生成**：用 `app.utils.slug.slugify()`，创建文章时自动去重（加 `-1`、`-2` 后缀）。

### 编码规范：前端

- **API 调用必须走 `api/client.ts` 的 axios 实例**，不要直接用 `fetch` 或新建 axios 实例。该实例自带 JWT 拦截器和 401 处理。
- **数据获取封装为 `useXxx` custom hooks**，统一三态模式：`{ data, loading, error }`。
- **变更操作不封装到 hooks 中**，直接导出 API 函数，通过 `useXxxMutations()` 返回（参考 `useArticleMutations`）。
- **组件 default export**（如 `export default function HomePage`），**hooks 用 named export**（如 `export function useArticles`）。
- **类型定义集中在 `types/index.ts`**，不要在各处重复定义接口。
- **样式用 Tailwind CSS 类**，不要写单独的 CSS 文件。
- **Markdown 渲染**：必须用 `react-markdown` + `remark-gfm`（GFM 扩展）+ `rehype-highlight`（代码高亮）。

## 提交流程

完成代码修改后，按以下步骤操作：

### 1. 代码审查 (`/simplify`)

写完代码后先运行 `/simplify` 技能，让 Claude 检查代码质量、复用性和潜在问题。

### 2. 本地模拟 CI

推送前在本地跑 CI 的检查项，确保能通过 GitHub Actions：

```bash
# 后端：验证所有导入正确
cd backend && uv run python -c "from app.main import app; print('OK')"

# 前端：类型检查 + 构建
cd frontend && npm run build

# 前端：lint 检查
cd frontend && npm run lint
```

以上全部通过后再提交。

### 2.5 e2e 测试（可选）

**后端单元测试和集成测试、前端组件测试全部通过之后**，Claude 应主动发起 e2e 测试流程：

1. **设计测试路径**：根据本次改动的范围，Claude 自动分析需要覆盖的用户操作路径，并向用户提出 e2e 测试方案
2. **用户确认**：用户审阅测试路径，可以讨论、调整、跳过或直接通过
3. **执行测试**：用户使用 browser skill 在本地浏览器中自动执行测试步骤，截图记录关键节点
4. **报告结果**：生成简短测试报告（通过/失败，附带截图和问题描述）

e2e 测试聚焦**新增或修改的功能路径**，不需要每次都跑全量 e2e。典型测试路径示例：

- "打开首页 → 确认文章列表渲染 → 点击首篇文章 → 确认详情页加载"
- "登录 → 创建文章 → 发布 → 验证文章出现在列表"

如果用户确认跳过 e2e 测试，直接进入步骤 3。

### 3. 提交 + 推送

```bash
# 暂存变更
git add <files>

# 提交（遵循约定式提交）
git commit -m "type: description"
# type: feat / fix / docs / refactor / ci / chore

# 推送到 main（触发 CI + 自动部署）
git push origin main
```

### 4. 监控 GitHub Actions

推送后用 `gh` CLI 查看 CI 状态：

```bash
# 查看最近一次 workflow 运行
gh run list --limit 3

# 查看具体运行详情
gh run view          # 交互式选择

# 实时跟踪日志
gh run watch
```

如果 CI 失败，根据失败的 job（后端测试 / 前端构建）定位问题，修复后重新提交推送。

## 测试

### 后端 (`pytest` + `pytest-asyncio`)

```bash
cd backend
uv run pytest tests/ -v          # 运行所有测试
uv run pytest tests/ -v -k auth  # 只运行匹配 "auth" 的测试
```

- 测试使用**内存 SQLite**，每个测试自动创建/清理表，完全隔离
- `conftest.py` 提供 fixtures：`client`（AsyncClient）、`auth_client`（已认证）、`test_user`、`auth_token`
- 测试覆盖：健康检查、认证（注册/登录/me）、文章 CRUD、评论、搜索、分页
- 使用 `httpx.AsyncClient` + `ASGITransport` 直接调用 FastAPI app，无需启动服务器

### 前端（Vitest + React Testing Library）

```bash
cd frontend
npm run test          # 运行所有测试
npm run test:watch    # 监视模式
```

- 测试环境为 `jsdom`，setup 文件位于 `src/test/setup.ts`
- 组件测试使用 `MemoryRouter` 包裹，确保 react-router 正常工作
- 测试覆盖：ArticleCard、TagList、SearchBar

### CI 测试

GitHub Actions 在每次 push/PR 时自动运行：

- 后端：`uv run pytest tests/ -v`
- 前端：`npm run test`

任一测试失败将阻止部署。

## 部署

CI 的 `deploy` job 在 push 到 main 分支时自动触发，依次执行：

1. 后端测试（pytest 集成测试）
2. 前端测试 + 构建（Node 22，npm ci + npm test + npm run build）
3. SCP 上传文件到服务器（192.144.154.17）
4. SSH 执行远程脚本（配置 BT-Panel Nginx、docker compose up）

部署配置详见 [.github/workflows/deploy.yml](.github/workflows/deploy.yml)。
