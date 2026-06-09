# Atelier · 光影几何 — 设计规格

> 日期：2026-06-09  
> 状态：已确认，待实现

---

## 1. 项目概述

**Atelier** 是个人博客/作品集网站。深色主题"光影几何"设计系统 — 不使用彩色，依靠对比、空间和结构建立视觉层次。

**用户模型：** 单用户（站长 August），无需注册系统，后台登录写死密码。

**原型文件：** `atelier/` 目录下 13 个 HTML 页面 + 1 个设计令牌 CSS。

---

## 2. 技术选型

| 层 | 选型 | 理由 |
|---|------|------|
| 前端框架 | Next.js (React) App Router | 内容驱动站点，SSR/SSG 支持好 |
| 后端 | Next.js API Routes | 前后端一个项目，类型共享 |
| 数据库 | PostgreSQL | 成熟稳定，运维经验丰富 |
| ORM | Prisma | 自动生成类型，迁移管理 |
| 认证 | 密码写死 .env + session cookie（jose） | 单用户，不需要用户系统 |
| 样式 | CSS Modules / Tailwind | 复刻 design-tokens.css |
| 部署 | 自建服务器 | Docker / PM2 |

---

## 3. 数据实体

### 3.1 文章（Article）
**来源原型：** blog.html（列表）、article.html（详情）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | 自增主键 | — |
| slug | 字符串，唯一 | URL 标识 |
| title | 字符串 | 标题 |
| excerpt | 字符串 | 摘要，列表展示用 |
| content | 文本 | Markdown 正文 |
| coverImage | 字符串 | 封面图 URL |
| images | 字符串数组 | 文中插图 |
| tags | 字符串数组 | 标签 |
| readingTime | 整数 | 阅读时长（分钟） |
| featured | 布尔 | 是否精选 |
| published | 布尔 | 是否发布 |
| publishedAt | 日期时间 | 发布时间 |
| createdAt | 日期时间 | 创建时间 |
| updatedAt | 日期时间 | 更新时间 |

### 3.2 作品（Product）
**来源原型：** products.html（画廊）、product-detail.html（详情）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | 自增主键 | — |
| slug | 字符串，唯一 | URL 标识 |
| title | 字符串 | 作品名 |
| description | 字符串 | 简介 |
| content | 文本 | Markdown 详情 |
| coverImage | 字符串 | 封面图 URL |
| images | 字符串数组 | 展示图片 |
| tags | 字符串数组 | 标签 |
| status | 枚举 | 在线 / 开发中 / 已下线 |
| url | 字符串 | 外部链接 |
| featured | 布尔 | 是否精选 |
| published | 布尔 | 是否发布 |
| publishedAt | 日期时间 | 发布时间 |
| createdAt | 日期时间 | 创建时间 |
| updatedAt | 日期时间 | 更新时间 |

### 3.3 媒体（Media）
**来源原型：** 设计系统图片库、文章/作品封面图

| 字段 | 类型 | 说明 |
|------|------|------|
| id | 自增主键 | — |
| filename | 字符串 | 原始文件名 |
| url | 字符串 | 访问路径 |
| alt | 字符串 | 替代文本 |
| width | 整数 | 宽度 |
| height | 整数 | 高度 |
| uploadedAt | 日期时间 | 上传时间 |

### 3.4 站点信息（SiteInfo）
**来源原型：** about.html（关于页）、admin-about.html（编辑）

单例表，只有一条记录。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | 主键 | 固定为 1 |
| aboutBio | 文本 | 个人简介 |
| aboutLinks | JSON 数组 | 链接列表 |
| siteTitle | 字符串 | 网站标题 |
| siteDescription | 字符串 | 网站描述 |
| socialLinks | JSON 数组 | 社交媒体链接 |

---

## 4. 路由架构

```
/                          首页（4屏视差滚动）
/blog                      笔记列表
/blog/[slug]               文章详情
/products                  作品画廊
/products/[slug]           作品详情
/about                     关于
/login                     登录

/admin                     仪表盘
/admin/articles            文章管理（列表/创建/编辑）
/admin/products            作品管理（列表/创建/编辑）
/admin/mascot              吉祥物管理
/admin/about               关于页编辑

/api/auth                  登录/登出
/api/articles              文章 CRUD
/api/products              作品 CRUD
/api/upload                图片上传
/api/site-info             站点信息读写
```

**访问控制：**
- 前台页面（`/` `/blog` `/products` `/about`）：公开
- `/login`：公开
- 后台页面（`/admin/*`）：必须登录
- API 读操作：公开；写操作：必须登录

---

## 5. 认证方案

- 密码存入 `.env`（`ADMIN_PASSWORD=xxxxx`）
- 登录页（原型 login.html）提交密码
- 服务端校验通过 → 签发加密 session cookie（`jose` 库）
- 中间件检查后台路由和 API 写操作的 cookie
- 未登录重定向到 `/login`
- Cookie 有效期 7 天

---

## 6. 设计系统迁移

原型 `design-tokens.css` 包含：
- **色彩：** OKLCH 深色系统（--c-bg, --c-surf, --c-fg, --c-fg-dim, --c-muted, --c-border, --c-light, --c-glow）
- **字体：** Prata（展示）、Noto Sans SC（正文）、JetBrains Mono（等宽）
- **排版刻度：** --fs-hero ~ --fs-meta，clamp() 响应式
- **间距：** --sp-2xs ~ --sp-3xl
- **动画：** --ease-expo, --ease-io, 页面入场、滚动渐入、交错延迟
- **导航：** 固定玻璃态导航栏、滚动进度点
- **状态系统：** loading / error / empty 三种覆盖
- **特效：** 胶片颗粒纹理、全屏 Section 系统

迁移策略：CSS 自定义属性直接保留，用 Tailwind 主题扩展或 CSS Module 复刻组件样式。

---

## 7. 实现阶段

### 阶段 0：项目脚手架
- `create-next-app` + TypeScript + Prisma + PostgreSQL
- design-tokens.css 全局引入
- 导航组件 + 根布局
- **验证：** 项目启动，深色背景 + 导航可见

### 阶段 1：数据层
- Prisma Schema → 数据库迁移
- 种子脚本写入示例数据
- **验证：** Prisma Studio 可浏览数据

### 阶段 2：前台页面
- 首页（视差滚动、叠化过渡）→ 笔记列表 → 文章详情
- 作品列表 → 作品详情 → 关于
- 每页完成 loading / error / empty 三个状态
- 动画系统复刻
- **验证：** 所有前台页面可访问，状态切换正常

### 阶段 3：认证 + 后台
- 登录页 + API → 后台布局
- 仪表盘 → 文章管理 → 作品管理
- 图片上传 → 关于页编辑 → 吉祥物管理
- **验证：** 登录后可管理全部内容

### 阶段 4：打磨 & 部署
- SEO 元数据（Open Graph、Twitter Card）
- 响应式最终检查
- 性能优化
- 部署到自建服务器
- **验证：** 线上可访问，功能完整

---

## 8. 约束与边界

- **不上云：** 部署在自己的服务器上，不依赖 Vercel/Netlify 等平台
- **单用户：** 没有注册、角色、权限系统
- **中文优先：** 内容以中文为主
- **原型驱动：** 视觉和交互以 `atelier/` 下的 HTML 文件为准
