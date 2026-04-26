# About 页面重构设计文档

**日期**: 2026-04-26
**状态**: 待审批

## 目标

将当前分散的 About 页配置（SiteConfig `about_bio` + 通用 Page 模型）合并为一个专属的数据模型，后台"页面管理"改造为 About 专属编辑器，移除三层降级渲染逻辑和通用的 Page 管理系统。

## 现状问题

1. **双数据源**：`SiteConfig(key='about_bio')` 和 `Page(slug='about')` 职责重叠，用户不知道该用哪个
2. **通用 Page 管理**：当前的 AdminPages 支持创建任意 slug 的页面，但设计初衷只应用于"关于页"
3. **三层降级逻辑**：AboutPage 组件按优先级检查 about_bio → Page → 默认模板，维护复杂
4. **管理体验差**：AdminSettings 只有一个纯 textarea，没有 Markdown 预览或结构化编辑

## 架构变更

### 后端

#### 新建模型 `backend/app/models/about_page.py`

```python
class AboutPage(Base):
    id = Integer, primary_key=True
    eyebrow = String(100), default="About"       # 标签文字
    title = String(255), nullable=False           # 主标题
    cover_image = String(500), default=""         # 封面图路径
    content = Text, default=""                    # Markdown 正文
    content_type = String(20), default="markdown" # markdown | html
    tech_stack = Text, default="[]"               # JSON 数组
    updated_at = DateTime, auto_update
```

说明：
- 只存储**一条**记录，通过 `id=1` 或首次 `SELECT` 判断是否存在
- `tech_stack` 用 Text 存 JSON，前端解析为字符串数组
- 不引入 `status` 字段（About 页始终显示，不需要草稿/发布状态）

#### 新建路由 `backend/app/routers/about.py`

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/about` | GET | 无 | 返回 AboutPage 数据（公开） |
| `/api/about` | PUT | 需要 | 更新 AboutPage（upsert，不存在则创建） |

实现要点：
- GET：`select(AboutPage).limit(1).first()`，无记录返回 404
- PUT：查到则更新，没查到则新建（upsert 模式）

#### 删除文件

- `backend/app/models/page.py`
- `backend/app/schemas/page.py`
- `backend/app/routers/pages.py`

#### 修改文件

- `backend/app/main.py`：移除 `pages` router 导入和注册，新增 `about` router

#### 数据库迁移

Alembic 迁移脚本：
1. 删除 `pages` 表
2. 新建 `about_pages` 表
3. 将 `site_configs` 中 `key='about_bio'` 的 `value` 迁移到 `about_pages.content`（如果存在）

### 前端

#### 新建 `frontend/src/api/about.ts`

```typescript
export interface AboutPageData {
  id: number;
  eyebrow: string;
  title: string;
  cover_image: string;
  content: string;
  content_type: string;
  tech_stack: string;  // JSON 字符串
  updated_at: string | null;
}

export const getAbout = async () => Promise<AboutPageData>
export const updateAbout = async (data: Partial<AboutPageData>) => Promise<AboutPageData>
```

#### 改造 `frontend/src/pages/AboutPage.tsx`

- 移除三层降级逻辑（`about_bio` / `Page(slug='about')` / 默认模板）
- 改为只调用 `getAbout()`
- 渲染逻辑：标题 + 封面图 + Markdown 内容 + 技术栈
- 加载态保持现有 Skeleton 组件
- 如果 API 返回 404，显示"关于页尚未配置"的提示

#### 改造 `frontend/src/pages/admin/AdminPages.tsx`

从通用 Page CRUD 改为 About 专属编辑器：

**表单字段**：
- Eyebrow 标签（短文本输入，默认 "About"）
- 主标题（文本输入）
- 封面图片路径（文本输入，带默认值 `/images/brand/about-workbench.webp`）
- 正文内容（Markdown textarea + 实时预览切换）
- 技术栈标签（tag 输入组件：可添加/删除标签）

**交互**：
- 页面加载时调用 `getAbout()`，有数据则填充表单
- 保存调用 `updateAbout()`
- 底部放"前台预览"按钮，点击在新标签页打开 `/about`
- 无列表、无删除按钮（About 页只有一条，不能删除）

#### 改造 `frontend/src/pages/admin/AdminSettings.tsx`

- 移除 `about_bio` 相关的所有代码（`useState`, `useEffect`, `getSetting`, `updateSetting`）
- 如果移除后 Settings 页面没有其他内容，则将其改为占位提示或移除路由入口

#### 删除文件

- `frontend/src/pages/StaticPage.tsx`
- `frontend/src/api/pages.ts`

#### 修改文件

- `frontend/src/App.tsx`：
  - 移除 `/:slug` 通配路由和 `StaticPage` 导入
  - 保留 `/about` 路由（指向改造后的 AboutPage）
  - 保留 `/admin/pages` 路由（指向改造后的 AdminPages）
- `frontend/src/types/index.ts`：
  - 移除 `Page` 接口
  - 新增 `AboutPage` 接口（与后端 Pydantic 对应）

#### 导航路由清理

- 后台侧边栏（`AdminLayout`）中"页面管理"的文案和功能描述需更新为"关于页"
- 如果 AdminSettings 移除内容后，相关侧边栏入口也需相应处理

## 数据流

```
后台 AdminPages  ──PUT──>  /api/about  ──>  about_pages 表
前台 AboutPage   ──GET──>  /api/about  <──  about_pages 表
```

不再有 SiteConfig、Page 表的参与。

## 边界情况

1. **数据库中没有 AboutPage 记录**：GET 返回 404，前台显示"尚未配置"占位；后台打开 AdminPages 显示空表单
2. **首次创建**：PUT 接口 upsert 逻辑自动新建记录
3. **tech_stack JSON 解析失败**：前端 fallback 到空数组
4. **封面图不存在**：img 标签使用默认 fallback 图片
