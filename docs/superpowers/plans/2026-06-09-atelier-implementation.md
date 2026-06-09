# Atelier · 光影几何 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Atelier 原型（13 个 HTML 页面）实现为基于 Next.js + Prisma + PostgreSQL 的全栈博客/作品集网站。

**Architecture:** Next.js App Router 项目，Server Components 负责数据查询，Client Components 负责交互和动画。设计令牌从 `atelier/design-tokens.css` 迁移到 Tailwind 主题配置。后台管理通过 API Routes + session cookie 认证。

**Tech Stack:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, Prisma, PostgreSQL, jose (JWT), react-markdown + rehype-highlight

---

## 文件结构一览

```
atelier/                              # 项目根目录
├── .env                              # 环境变量 (ADMIN_PASSWORD, DATABASE_URL)
├── .env.example                      # 环境变量模板
├── next.config.ts                    # Next.js 配置
├── tailwind.config.ts                # Tailwind + 设计令牌
├── tsconfig.json                     # TypeScript 配置
├── package.json                      # 依赖
│
├── prisma/
│   ├── schema.prisma                 # 数据库 Schema
│   └── seed.ts                       # 种子数据
│
├── lib/
│   ├── db.ts                         # Prisma 客户端单例
│   ├── auth.ts                       # session 加密/解密/校验
│   ├── markdown.ts                   # Markdown 渲染工具
│   └── constants.ts                  # 品牌名等常量
│
├── components/
│   ├── nav.tsx                       # 全局固定导航栏
│   ├── footer.tsx                    # 页脚
│   ├── state-card.tsx                # loading / error / empty 状态卡片
│   ├── tags.tsx                      # 标签列表
│   ├── section-nav.tsx               # 右侧滚动进度导航点
│   ├── parallax-hero.tsx             # 通用视差 Hero 区块
│   ├── markdown-body.tsx             # Markdown 渲染正文
│   └── admin/
│       ├── sidebar.tsx               # 后台侧边栏导航
│       ├── article-form.tsx          # 文章编辑表单
│       ├── product-form.tsx          # 作品编辑表单
│       ├── image-upload.tsx          # 图片上传组件
│       └── skeleton.tsx              # 骨架屏
│
├── app/
│   ├── globals.css                   # 全局样式 (design-tokens.css 迁移)
│   ├── layout.tsx                    # 根布局
│   ├── page.tsx                      # 首页 (4屏视差滚动)
│   │
│   ├── blog/
│   │   ├── page.tsx                  # 笔记列表
│   │   └── [slug]/page.tsx           # 文章详情
│   │
│   ├── products/
│   │   ├── page.tsx                  # 作品画廊
│   │   └── [slug]/page.tsx           # 作品详情 (iframe + 信息面板)
│   │
│   ├── about/page.tsx                # 关于页
│   ├── login/page.tsx                # 登录页
│   │
│   ├── admin/
│   │   ├── layout.tsx                # 后台布局 (侧边栏 + 内容区)
│   │   ├── page.tsx                  # 仪表盘
│   │   ├── articles/
│   │   │   ├── page.tsx              # 文章列表
│   │   │   ├── new/page.tsx          # 新建文章
│   │   │   └── [id]/edit/page.tsx    # 编辑文章
│   │   ├── products/
│   │   │   ├── page.tsx              # 作品列表
│   │   │   ├── new/page.tsx          # 新建作品
│   │   │   └── [id]/edit/page.tsx    # 编辑作品
│   │   ├── mascot/page.tsx           # 吉祥物管理
│   │   └── about/page.tsx            # 关于页编辑
│   │
│   └── api/
│       ├── auth/
│       │   ├── login/route.ts        # POST 登录
│       │   ├── logout/route.ts       # POST 登出
│       │   └── check/route.ts        # GET 检查登录状态
│       ├── articles/
│       │   ├── route.ts              # GET 列表 / POST 创建
│       │   └── [id]/route.ts         # GET/PUT/DELETE 单篇
│       ├── products/
│       │   ├── route.ts              # GET 列表 / POST 创建
│       │   └── [id]/route.ts         # GET/PUT/DELETE 单个
│       ├── upload/route.ts           # POST 图片上传
│       └── site-info/route.ts        # GET/PUT 站点信息
│
├── middleware.ts                     # 路由保护 (后台 + API写操作)
└── public/
    └── uploads/                      # 上传图片存放目录
```

---

## 阶段 0：项目脚手架

### Task 0.1：初始化 Next.js 项目

**Files:**
- Create: `package.json`, `tsconfig.json`, `next.config.ts`, `tailwind.config.ts`, `postcss.config.mjs`, `.env.example`

- [ ] **Step 1: 用 create-next-app 初始化**

Run:
```bash
cd g:/vscode/projects/blogsite2.0
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --no-turbopack --use-npm
```

Expected: 项目文件生成，`package.json` 含 next, react, tailwindcss 等依赖。

- [ ] **Step 2: 安装额外依赖**

Run:
```bash
npm install prisma @prisma/client jose react-markdown rehype-highlight remark-gfm
npm install -D @types/node tsx
```

- [ ] **Step 3: 创建 .env.example**

```bash
# .env.example
DATABASE_URL="postgresql://user:password@localhost:5432/atelier"
ADMIN_PASSWORD="your-password-here"
```

- [ ] **Step 4: 生成 Prisma 客户端骨架**

Run:
```bash
npx prisma init
```

Expected: 生成 `prisma/schema.prisma` 和 `.env`。

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: init Next.js + TypeScript + Tailwind + Prisma project"
```

---

### Task 0.2：迁移设计系统 — 全局 CSS

**Files:**
- Modify: `app/globals.css`

- [ ] **Step 1: 用原型 design-tokens.css 替换 globals.css**

将 `atelier/design-tokens.css` 的全部内容复制到 `app/globals.css`，然后从 `atelier/design-tokens.css` 中移除所有页面专属样式（只保留 `:root` 自定义属性、全局重置、排版类、实用类、导航、状态卡片、按钮、标签），把页面专属的 section 样式留给各自的 CSS Module。

```css
/* app/globals.css */

/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=Prata&family=JetBrains+Mono:wght@400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ==========================================
   CSS Custom Properties (design-tokens.css 完整迁移)
   ========================================== */
:root {
  --c-bg:       oklch(0.035 0.008 275);
  --c-surf:     oklch(0.085 0.012 270);
  --c-surf-2:   oklch(0.11  0.014 268);
  --c-fg:       oklch(0.93  0.005 270);
  --c-fg-dim:   oklch(0.45  0.012 270);
  --c-muted:    oklch(0.35  0.010 270);
  --c-border:   oklch(0.15  0.010 270);
  --c-border-l: oklch(0.20  0.010 270);
  --c-light:    oklch(0.78  0.015 270);
  --c-glow:     oklch(0.72  0.015 270 / 0.06);

  --c-accent:   oklch(0.55  0.06  90);
  --c-link:     oklch(0.65  0.08  260);

  --ff-display: 'Prata', 'Noto Serif SC', 'Source Han Serif SC', Georgia, serif;
  --ff-body:    'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --ff-mono:    'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;

  --fs-hero:    clamp(2.5rem, 6vw, 6.5rem);
  --fs-display: clamp(1.75rem, 3.5vw, 3.25rem);
  --fs-h2:      clamp(1.35rem, 2.2vw, 2.25rem);
  --fs-h3:      clamp(1.1rem, 1.6vw, 1.6rem);
  --fs-body:    clamp(0.95rem, 1.1vw, 1.1rem);
  --fs-small:   clamp(0.8rem, 0.85vw, 0.9rem);
  --fs-meta:    clamp(0.7rem, 0.7vw, 0.8rem);

  --lh-tight:   1.05;
  --lh-heading: 1.3;
  --lh-body:    1.75;
  --ls-wide:    0.12em;

  --sp-2xs: 0.25rem;
  --sp-xs:  0.5rem;
  --sp-sm:  0.75rem;
  --sp-md:  1.25rem;
  --sp-lg:  2.25rem;
  --sp-xl:  4rem;
  --sp-2xl: 7rem;
  --sp-3xl: 10rem;

  --ease-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-io:   cubic-bezier(0.76, 0, 0.24, 1);
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;
  --grain:     0.03;
}

/* ==========================================
   全局重置 & 基础 (原样复制)
   ========================================== */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--ff-body);
  font-size: var(--fs-body);
  line-height: var(--lh-body);
  color: var(--c-fg);
  background: var(--c-bg);

  &::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: var(--grain);
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
  }
}

img { display: block; max-width: 100%; height: auto; }
a { color: inherit; text-decoration: none; }
ul { list-style: none; }

::selection { background: var(--c-light); color: var(--c-bg); }

/* 排版工具类 */
.font-display { font-family: var(--ff-display); }
.font-body    { font-family: var(--ff-body); }
.font-mono    { font-family: var(--ff-mono); }

.sr-only {
  position: absolute;
  width: 1px; height: 1px;
  margin: -1px; padding: 0;
  overflow: hidden;
  clip: rect(0,0,0,0);
  border: 0;
}

.container {
  width: min(92%, 1280px);
  margin-inline: auto;
}

.container--narrow {
  width: min(88%, 800px);
  margin-inline: auto;
}

/* 页面入场动画 */
.page-enter {
  opacity: 0;
  transform: translateY(16px);
  animation: pageIn 0.8s var(--ease-expo) forwards;
}

@keyframes pageIn {
  to { opacity: 1; transform: translateY(0); }
}

/* 滚动渐入 */
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.8s var(--ease-expo), transform 0.8s var(--ease-expo);
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

.stagger > * {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.6s var(--ease-expo), transform 0.6s var(--ease-expo);
}
.stagger.visible > * {
  opacity: 1;
  transform: translateY(0);
}
.stagger.visible > *:nth-child(1) { transition-delay: 0.05s; }
.stagger.visible > *:nth-child(2) { transition-delay: 0.12s; }
.stagger.visible > *:nth-child(3) { transition-delay: 0.19s; }
.stagger.visible > *:nth-child(4) { transition-delay: 0.26s; }
.stagger.visible > *:nth-child(5) { transition-delay: 0.33s; }
.stagger.visible > *:nth-child(6) { transition-delay: 0.40s; }

/* 导航系统 */
.nav-v2 {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-lg) var(--sp-xl);
  transition: background 0.4s var(--ease-expo), box-shadow 0.4s var(--ease-expo);
  pointer-events: none;
}

.nav-v2 * { pointer-events: auto; }

.nav-v2--solid {
  background: oklch(0.04 0.008 275 / 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 1px 0 var(--c-border);
}

.nav-v2__brand {
  font-family: var(--ff-body);
  font-size: var(--fs-small);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--c-fg);
}

.nav-v2__links {
  display: flex;
  gap: var(--sp-xl);
}

.nav-v2__link {
  font-family: var(--ff-body);
  font-size: var(--fs-meta);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--c-fg-dim);
  transition: color 0.3s var(--ease-expo);
  position: relative;
}

.nav-v2__link:hover { color: var(--c-fg); }

/* 右侧滚动导航点 */
.section-nav {
  position: fixed;
  right: var(--sp-lg);
  top: 50%;
  transform: translateY(-50%);
  z-index: 90;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-nav__dot {
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: var(--c-muted);
  transition: all 0.5s var(--ease-expo);
  cursor: pointer;
}

.section-nav__dot.active {
  width: 28px;
  height: 2px;
  border-radius: 1px;
  background: var(--c-fg);
}

/* 状态卡片 (全局复用) */
.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--sp-3xl) var(--sp-lg);
  min-height: 300px;
}

.state-card__icon {
  font-family: var(--ff-body);
  font-size: var(--fs-h3);
  margin-bottom: var(--sp-md);
  opacity: 0.3;
}

.state-card__title {
  font-family: var(--ff-body);
  font-size: var(--fs-h3);
  letter-spacing: var(--ls-wide);
  text-transform: uppercase;
  margin-bottom: var(--sp-sm);
}

.state-card__desc {
  color: var(--c-fg-dim);
  max-width: 380px;
}

/* 按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-sm);
  padding: var(--sp-sm) var(--sp-lg);
  font-family: var(--ff-body);
  font-size: var(--fs-small);
  letter-spacing: var(--ls-wide);
  text-transform: uppercase;
  border: 1px solid var(--c-border-l);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--c-fg);
  cursor: pointer;
  transition: all 0.3s var(--ease-expo);
}

.btn:hover {
  border-color: var(--c-fg);
  background: var(--c-fg);
  color: var(--c-bg);
}

/* 标签/徽标 */
.tag {
  display: inline-block;
  padding: 0.15em 0.6em;
  font-family: var(--ff-mono);
  font-size: var(--fs-meta);
  border: 1px solid var(--c-border);
  color: var(--c-fg-dim);
  transition: all 0.3s var(--ease-expo);
}

.tag:hover {
  border-color: var(--c-light);
  color: var(--c-fg);
}

.tag--active {
  border-color: var(--c-light);
  color: var(--c-fg);
}

/* 响应式导航 */
@media (max-width: 768px) {
  .nav-v2 { padding: var(--sp-md) var(--sp-lg); }
  .nav-v2__links { display: none; }
  .section-nav { display: none; }
}
```

- [ ] **Step 2: 映射设计令牌到 Tailwind 配置**

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--c-bg)",
        surf: "var(--c-surf)",
        "surf-2": "var(--c-surf-2)",
        fg: "var(--c-fg)",
        "fg-dim": "var(--c-fg-dim)",
        muted: "var(--c-muted)",
        border: "var(--c-border)",
        "border-l": "var(--c-border-l)",
        light: "var(--c-light)",
        glow: "var(--c-glow)",
        accent: "var(--c-accent)",
        link: "var(--c-link)",
      },
      fontFamily: {
        display: "var(--ff-display)",
        body: "var(--ff-body)",
        mono: "var(--ff-mono)",
      },
      fontSize: {
        hero: "var(--fs-hero)",
        display: "var(--fs-display)",
        h2: "var(--fs-h2)",
        h3: "var(--fs-h3)",
        body: "var(--fs-body)",
        small: "var(--fs-small)",
        meta: "var(--fs-meta)",
      },
      spacing: {
        "2xs": "var(--sp-2xs)",
        xs: "var(--sp-xs)",
        sm: "var(--sp-sm)",
        md: "var(--sp-md)",
        lg: "var(--sp-lg)",
        xl: "var(--sp-xl)",
        "2xl": "var(--sp-2xl)",
        "3xl": "var(--sp-3xl)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
      transitionTimingFunction: {
        expo: "var(--ease-expo)",
        io: "var(--ease-io)",
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 3: 验证**

Run: `npm run dev` → 访问 `http://localhost:3000` → 看到深色背景 + 胶片颗粒纹理。

- [ ] **Step 4: Commit**

```bash
git add app/globals.css tailwind.config.ts
git commit -m "style: migrate design-tokens.css and Tailwind config"
```

---

### Task 0.3：导航组件 + 根布局

**Files:**
- Create: `components/nav.tsx`, `components/footer.tsx`
- Modify: `app/layout.tsx`

- [ ] **Step 1: 创建全局导航组件**

```tsx
// components/nav.tsx
import Link from "next/link";

const NAV_LINKS = [
  { href: "/", label: "首页" },
  { href: "/blog", label: "笔记" },
  { href: "/products", label: "作品" },
  { href: "/about", label: "关于" },
];

export function Nav() {
  return (
    <nav className="nav-v2 nav-v2--solid">
      <Link href="/" className="nav-v2__brand">Atelier</Link>
      <div className="nav-v2__links">
        {NAV_LINKS.map(({ href, label }) => (
          <Link key={href} href={href} className="nav-v2__link">
            {label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
```

- [ ] **Step 2: 创建页脚组件**

```tsx
// components/footer.tsx
export function Footer() {
  return (
    <footer style={{
      padding: "var(--sp-2xl) 0",
      textAlign: "center",
      color: "var(--c-muted)",
      fontFamily: "var(--ff-mono)",
      fontSize: "var(--fs-meta)",
      borderTop: "1px solid var(--c-border)",
    }}>
      <p>Atelier · 光影几何 · 2026</p>
    </footer>
  );
}
```

- [ ] **Step 3: 更新根布局**

```tsx
// app/layout.tsx
import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "Atelier · 光影几何",
  description: "一个以光影和几何为核心的深色设计系统。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 4: 验证**

Run: `npm run dev` → 看到页面顶部有固定导航栏，"Atelier" 品牌名 + 四个链接。

- [ ] **Step 5: Commit**

```bash
git add components/nav.tsx components/footer.tsx app/layout.tsx
git commit -m "feat: add global nav, footer, and root layout"
```

---

## 阶段 1：数据层

### Task 1.1：Prisma Schema + 数据库迁移

**Files:**
- Modify: `prisma/schema.prisma`
- Create: `lib/db.ts`

- [ ] **Step 1: 编写 Prisma Schema**

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Article {
  id          Int       @id @default(autoincrement())
  slug        String    @unique
  title       String
  excerpt     String    @default("")
  content     String    @default("")
  coverImage  String    @default("")
  images      String[]  @default([])
  tags        String[]  @default([])
  readingTime Int       @default(3)
  featured    Boolean   @default(false)
  published   Boolean   @default(false)
  publishedAt DateTime?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
}

model Product {
  id          Int       @id @default(autoincrement())
  slug        String    @unique
  title       String
  description String    @default("")
  content     String    @default("")
  coverImage  String    @default("")
  images      String[]  @default([])
  tags        String[]  @default([])
  status      String    @default("draft") // "online" | "developing" | "offline"
  url         String    @default("")
  featured    Boolean   @default(false)
  published   Boolean   @default(false)
  publishedAt DateTime?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
}

model Media {
  id         Int      @id @default(autoincrement())
  filename   String
  url        String
  alt        String   @default("")
  width      Int      @default(0)
  height     Int      @default(0)
  uploadedAt DateTime @default(now())
}

model SiteInfo {
  id              Int    @id @default(1)
  aboutBio        String @default("")
  aboutLinks      Json   @default("[]")
  siteTitle       String @default("Atelier")
  siteDescription String @default("")
  socialLinks     Json   @default("[]")
}
```

- [ ] **Step 2: 创建 Prisma 客户端单例**

```typescript
// lib/db.ts
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
```

- [ ] **Step 3: 配置 .env 中的 DATABASE_URL，确保 PostgreSQL 运行**

Edit `.env`:
```
DATABASE_URL="postgresql://postgres:password@localhost:5432/atelier"
ADMIN_PASSWORD="atelier2026"
```

- [ ] **Step 4: 运行数据库迁移**

```bash
npx prisma migrate dev --name init
```

Expected: 数据库中生成 Article, Product, Media, SiteInfo 四张表。

- [ ] **Step 5: Commit**

```bash
git add prisma/schema.prisma lib/db.ts .env.example
git commit -m "feat: add Prisma schema and DB client singleton"
```

---

### Task 1.2：种子数据

**Files:**
- Create: `prisma/seed.ts`
- Modify: `package.json` (prisma.seed 配置)

- [ ] **Step 1: 编写种子脚本**

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // 清理旧数据
  await prisma.article.deleteMany();
  await prisma.product.deleteMany();
  await prisma.media.deleteMany();
  await prisma.siteInfo.deleteMany();

  // 种子文章
  await prisma.article.createMany({
    data: [
      {
        slug: "building-space-with-light",
        title: "用光影构建空间感",
        excerpt: "关于如何在数字界面中通过光影对比建立视觉层次，而不是依赖颜色。",
        content: `## 光影即空间\n\n在设计数字界面时，我们常常过度依赖颜色来区分层级。但真正有深度的设计，依靠的是光影对比。\n\n### 从摄影中学习\n\n摄影中最基本的原则之一：光影定义形体。高光让元素浮现，阴影让元素后退。`,
        coverImage: "/uploads/venetian-blind-shadow.png",
        tags: ["设计", "思考"],
        readingTime: 6,
        featured: true,
        published: true,
        publishedAt: new Date("2026-06-09"),
      },
      {
        slug: "comfyui-workflow",
        title: "ComfyUI 本地生图工作流",
        excerpt: "搭建了一套本地化的图像生成管线，从快速出图到高清超分的完整记录。",
        content: `## 本地生图管线\n\n记录搭建 ComfyUI + RTX 4060 的工作流。`,
        coverImage: "/uploads/perforated-metal-shadow.png",
        tags: ["技术", "AI"],
        readingTime: 4,
        featured: false,
        published: true,
        publishedAt: new Date("2026-06-05"),
      },
    ],
  });

  // 种子作品
  await prisma.product.createMany({
    data: [
      {
        slug: "tools-2026",
        title: "工具集 · 2026",
        description: "一组日常开发工具的摄影记录。",
        content: "通过俯拍和均匀打光，呈现工具本身的几何美感和材质细节。",
        coverImage: "/uploads/metal-ruler.png",
        tags: ["摄影", "工具"],
        status: "online",
        featured: true,
        published: true,
        publishedAt: new Date("2026-06-01"),
      },
    ],
  });

  // 种子站点信息
  await prisma.siteInfo.create({
    data: {
      id: 1,
      aboutBio: "光影之间的创作者。用摄影和代码构建数字空间。",
      siteTitle: "Atelier · 光影几何",
      siteDescription: "一个以光影和几何为核心的深色设计系统。",
      aboutLinks: [
        { label: "GitHub", url: "https://github.com/august" },
      ],
      socialLinks: [
        { label: "GitHub", url: "https://github.com/august" },
      ],
    },
  });

  console.log("✅ Seed data inserted successfully");
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
```

- [ ] **Step 2: 在 package.json 中添加 seed 配置**

确认 `package.json` 包含:
```json
"prisma": {
  "seed": "tsx prisma/seed.ts"
}
```

- [ ] **Step 3: 运行种子**

```bash
npx prisma db seed
```

Expected: 输出 "✅ Seed data inserted successfully"，Prisma Studio 可见数据。

- [ ] **Step 4: Commit**

```bash
git add prisma/seed.ts package.json
git commit -m "feat: add seed data for articles, products, and site info"
```

---

## 阶段 2：前台页面

### Task 2.1：Lib 工具函数

**Files:**
- Create: `lib/markdown.ts`, `lib/constants.ts`

- [ ] **Step 1: Markdown 渲染工具**

```typescript
// lib/markdown.ts
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
```

- [ ] **Step 2: 常量文件**

```typescript
// lib/constants.ts
export const SITE_NAME = "Atelier";
export const SITE_TAGLINE = "光影几何";
export const DEFAULT_COVER = "/uploads/venetian-blind-shadow.png";
```

- [ ] **Step 3: Commit**

```bash
git add lib/markdown.ts lib/constants.ts
git commit -m "feat: add markdown renderer and constants"
```

---

### Task 2.2：共享 UI 组件

**Files:**
- Create: `components/state-card.tsx`, `components/tags.tsx`, `components/parallax-hero.tsx`, `components/markdown-body.tsx`

- [ ] **Step 1: StateCard 组件 (loading/error/empty)**

```tsx
// components/state-card.tsx
import Link from "next/link";

interface StateCardProps {
  type: "loading" | "error" | "empty";
  title?: string;
  desc?: string;
  retryHref?: string;
  retryLabel?: string;
  minHeight?: string;
}

export function StateCard({ type, title, desc, retryHref, retryLabel, minHeight = "100vh" }: StateCardProps) {
  const defaults = {
    loading: { icon: "⟳", title: "加载中", desc: "正在获取内容…" },
    error:   { icon: "!", title: "加载失败", desc: "无法连接到服务器，请稍后重试。" },
    empty:   { icon: "—", title: "暂无内容", desc: "还没有发布任何内容，敬请期待。" },
  };

  const d = defaults[type];

  return (
    <div className="state-card" style={{ minHeight }}>
      <div className="state-card__icon" style={type === "loading" ? { animation: "pulse 1.5s ease-in-out infinite" } : undefined}>
        {d.icon}
      </div>
      <div className="state-card__title">{title ?? d.title}</div>
      <p className="state-card__desc">{desc ?? d.desc}</p>
      {retryHref && (
        <Link href={retryHref} className="btn" style={{ marginTop: "var(--sp-lg)" }}>
          {retryLabel ?? "重试"}
        </Link>
      )}
      <style>{`@keyframes pulse { 0%,100% { opacity: 0.3; } 50% { opacity: 0.8; } }`}</style>
    </div>
  );
}
```

- [ ] **Step 2: Tags 组件**

```tsx
// components/tags.tsx
export function Tags({ tags, active }: { tags: string[]; active?: string }) {
  return (
    <div style={{ display: "flex", gap: "var(--sp-xs)", flexWrap: "wrap" }}>
      {tags.map((tag) => (
        <span key={tag} className={`tag${active === tag ? " tag--active" : ""}`}>
          {tag}
        </span>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: ParallaxHero 组件（通用视差 Header）**

```tsx
// components/parallax-hero.tsx
"use client";
import { useEffect, useRef } from "react";

interface ParallaxHeroProps {
  image: string;
  label: string;
  title: string;
  description?: string;
  height?: string;
}

export function ParallaxHero({ image, label, title, description, height = "55vh" }: ParallaxHeroProps) {
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!bgRef.current) return;
      const scrollY = window.scrollY;
      bgRef.current.style.transform = `translateY(${scrollY * 0.3}px)`;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      style={{
        position: "relative",
        width: "100%",
        height,
        minHeight: "420px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <div
        ref={bgRef}
        style={{
          position: "absolute",
          inset: "-10%",
          willChange: "transform",
        }}
      >
        <img src={image} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.25) 50%, var(--c-bg) 100%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse 70% 60% at 50% 50%, transparent 0%, oklch(0 0 0 / 0.3) 100%)",
          pointerEvents: "none",
          zIndex: 1,
        }}
      />

      <div style={{ position: "relative", zIndex: 2, textAlign: "center" }}>
        <p style={{
          fontFamily: "var(--ff-mono)",
          fontSize: "var(--fs-meta)",
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          color: "oklch(0.7 0.01 270 / 0.45)",
          marginBottom: "var(--sp-md)",
        }}>
          {label}
        </p>
        <h1 style={{
          fontFamily: "var(--ff-display)",
          fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
          fontWeight: 400,
          color: "#fff",
          lineHeight: 1.1,
          textShadow: "0 2px 40px oklch(0 0 0 / 0.5)",
          marginBottom: "var(--sp-sm)",
        }}>
          {title}
        </h1>
        {description && (
          <p style={{
            color: "oklch(0.7 0.01 270 / 0.65)",
            fontWeight: 300,
            fontSize: "var(--fs-body)",
          }}>
            {description}
          </p>
        )}
      </div>
    </header>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add components/state-card.tsx components/tags.tsx components/parallax-hero.tsx
git commit -m "feat: add StateCard, Tags, and ParallaxHero shared components"
```

---

### Task 2.3：首页（4 屏视差滚动）

**Files:**
- Create: `app/page.tsx`

- [ ] **Step 1: 实现首页**

```tsx
// app/page.tsx
import Link from "next/link";
import { prisma } from "@/lib/db";
import { Tags } from "@/components/tags";
import { HomeClient } from "./home-client";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [articles, products] = await Promise.all([
    prisma.article.findMany({
      where: { published: true, featured: true },
      orderBy: { publishedAt: "desc" },
      take: 3,
      select: { id: true, slug: true, title: true, excerpt: true, tags: true, readingTime: true, publishedAt: true },
    }),
    prisma.product.findMany({
      where: { published: true, featured: true },
      orderBy: { publishedAt: "desc" },
      take: 3,
      select: { id: true, slug: true, title: true, description: true, coverImage: true, status: true },
    }),
  ]);

  return <HomeClient articles={articles} products={products} />;
}
```

- [ ] **Step 2: 创建客户端交互组件（视差滚动核心）**

```tsx
// app/home-client.tsx
"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { Tags } from "@/components/tags";
import { StateCard } from "@/components/state-card";

// 复用原型 home.html 的视差 + 叠化 JS 逻辑
export function HomeClient({ articles, products }: { articles: any[]; products: any[] }) {
  const [activeSection, setActiveSection] = useState(0);
  const sectionsRef = useRef<(HTMLElement | null)[]>([]);

  const updateScene = useCallback(() => {
    const winH = window.innerHeight;
    let maxVis = 0;
    let newIdx = 0;

    sectionsRef.current.forEach((sec, i) => {
      if (!sec) return;
      const r = sec.getBoundingClientRect();
      const secH = sec.offsetHeight;
      const visibleInView = Math.min(r.bottom, winH) - Math.max(r.top, 0);
      const visibility = Math.max(0, Math.min(1, visibleInView / secH));
      if (visibility > maxVis) { maxVis = visibility; newIdx = i; }

      const content = sec.querySelector(".anim-content") as HTMLElement;
      if (content) {
        const raw = Math.max(0, Math.min(1, (visibility - 0.05) / 0.65));
        const eased = raw === 1 ? 1 : 1 - Math.pow(2, -10 * raw);
        content.style.opacity = String(eased);
        content.style.transform = `translateY(${(1 - eased) * 100}px) scale(${0.82 + 0.18 * eased})`;
        content.style.filter = `blur(${14 * (1 - eased)}px)`;
      }

      const bg = sec.querySelector(".section__bg") as HTMLElement;
      if (bg) {
        const parallaxSpeed = parseFloat(bg.dataset.parallax || "0.25");
        const offset = r.top * Math.max(parallaxSpeed * 1.6, 0.35);
        const scale = 1.0 + 0.08 * Math.max(0, Math.sin(visibility * Math.PI - 0.3));
        bg.style.transform = `translateY(${offset}px) scale(${scale})`;
      }

      const scrim = sec.querySelector(".section__scrim") as HTMLElement;
      if (scrim) {
        const leaving = Math.max(0, Math.min(1, -r.top / secH));
        const entering = Math.max(0, Math.min(1, (r.bottom - winH) / secH));
        scrim.style.opacity = String(Math.max(leaving * 0.92, entering * 0.72));
      }
    });

    setActiveSection(newIdx);
  }, []);

  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => { updateScene(); ticking = false; });
        ticking = true;
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [updateScene]);

  useEffect(() => { updateScene(); }, [updateScene]);

  const sectionImages = [
    "/uploads/venetian-blind-shadow.png",
    "/uploads/perforated-metal-shadow.png",
    "/uploads/plaster-geometric.png",
    "/uploads/glass-shadow.png",
  ];

  const sections = ["hero", "articles", "works", "quote"];

  return (
    <>
      <nav className="section-nav">
        {sections.map((s, i) => (
          <span
            key={s}
            className={`section-nav__dot${i === activeSection ? " active" : ""}`}
            onClick={() => document.querySelector(`[data-section="${s}"]`)?.scrollIntoView({ behavior: "smooth" })}
          />
        ))}
      </nav>

      <div>
        {/* Section 1: Hero */}
        <section
          ref={(el) => { sectionsRef.current[0] = el; }}
          className="section" data-section="hero"
          style={{ position: "relative", width: "100%", height: "100dvh", minHeight: "600px", display: "flex", alignItems: "center", overflow: "hidden" }}
        >
          <div className="section__bg" data-parallax="0.3" style={{ position: "absolute", inset: "-8%", zIndex: 0, overflow: "hidden", willChange: "transform" }}>
            <img src={sectionImages[0]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
          <div className="section__overlay" style={{ position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none", background: "linear-gradient(180deg, oklch(0 0 0 / 0.65) 0%, oklch(0 0 0 / 0.3) 35%, oklch(0 0 0 / 0.35) 50%, oklch(0 0 0 / 0.5) 75%, oklch(0 0 0 / 0.7) 100%)" }} />
          <div className="section__scrim" style={{ position: "absolute", inset: 0, zIndex: 2, background: "var(--c-bg)", opacity: 0, transition: "none", pointerEvents: "none" }} />
          <div className="section__content anim-content" style={{ position: "relative", zIndex: 3, width: "min(92%, 1280px)", marginInline: "auto", textAlign: "center", paddingTop: "5vh" }}>
            <p style={{ fontFamily: "var(--ff-mono)", fontSize: "clamp(0.6rem, 0.6vw, 0.7rem)", letterSpacing: "0.4em", textTransform: "uppercase", color: "oklch(0.7 0.01 270 / 0.45)", marginBottom: "var(--sp-lg)" }}>
              光影之间
            </p>
            <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "clamp(3rem, 8vw, 9rem)", fontWeight: 400, lineHeight: 0.92, color: "#fff", textShadow: "0 4px 48px oklch(0 0 0 / 0.6), 0 1px 0 rgb(255 255 255 / 0.08)", letterSpacing: "-0.03em" }}>
              August&apos;s<br />
              <span style={{ fontWeight: 300, fontSize: "0.55em", display: "block", opacity: 0.7, letterSpacing: "0.08em", marginTop: "var(--sp-sm)" }}>Atelier</span>
            </h1>
            <p style={{ fontSize: "clamp(1rem, 1.3vw, 1.3rem)", color: "oklch(0.72 0.01 270 / 0.7)", maxWidth: "36rem", lineHeight: 1.65, fontWeight: 300, marginTop: "var(--sp-lg)", textShadow: "0 2px 24px oklch(0 0 0 / 0.7)" }}>
              用光影与图像驱动的创作空间<br />记录灵感、实验与作品
            </p>
          </div>
        </section>

        {/* Section 2: 最新笔记 */}
        <section ref={(el) => { sectionsRef.current[1] = el; }} className="section" data-section="articles"
          style={{ position: "relative", width: "100%", height: "100dvh", minHeight: "600px", display: "flex", alignItems: "center", overflow: "hidden" }}>
          <div className="section__bg" data-parallax="0.3" style={{ position: "absolute", inset: "-8%", zIndex: 0, overflow: "hidden", willChange: "transform" }}>
            <img src={sectionImages[1]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
          <div className="section__overlay" style={{ position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none", background: "linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.2) 25%, oklch(0 0 0 / 0.2) 75%, oklch(0 0 0 / 0.55) 100%)" }} />
          <div className="section__scrim" style={{ position: "absolute", inset: 0, zIndex: 2, background: "var(--c-bg)", opacity: 0, transition: "none", pointerEvents: "none" }} />

          <div className="section__content anim-content" style={{ position: "relative", zIndex: 3, width: "min(92%, 1280px)", marginInline: "auto" }}>
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="section__number">/ 01</p>
                <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-display)", fontWeight: 400, lineHeight: 1.2, color: "#fff" }}>最新笔记</h2>
              </div>
              <Link href="/blog" className="section__link">查看全部 →</Link>
            </div>

            {articles.length === 0 ? (
              <StateCard type="empty" minHeight="200px" />
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "2px" }}>
                {articles.map((a, i) => (
                  <Link key={a.id} href={`/blog/${a.slug}`}
                    style={{ position: "relative", padding: "var(--sp-xl) var(--sp-lg)", display: "flex", flexDirection: "column", gap: "var(--sp-md)", border: "1px solid rgb(255 255 255 / 0.04)", minHeight: "260px", overflow: "hidden" }}
                    className="articles-card-hover">
                    <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", gap: "var(--sp-md)", flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "oklch(0.75 0.015 270 / 0.65)" }}>
                        <span>{String(i + 1).padStart(2, "0")}</span>
                        <span style={{ width: 2, height: 2, borderRadius: "50%", background: "oklch(0.65 0.01 270 / 0.25)" }} />
                        <span>{a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : ""}</span>
                        <span style={{ width: 2, height: 2, borderRadius: "50%", background: "oklch(0.65 0.01 270 / 0.25)" }} />
                        <span>{a.readingTime} 分钟</span>
                      </div>
                      <h3 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, lineHeight: 1.3, color: "#fff" }}>{a.title}</h3>
                      <p style={{ color: "oklch(0.82 0.015 270 / 0.78)", fontSize: "var(--fs-small)" }}>{a.excerpt}</p>
                      <div style={{ marginTop: "auto" }}>
                        <Tags tags={a.tags} />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Section 3: 精选作品 */}
        <section ref={(el) => { sectionsRef.current[2] = el; }} className="section" data-section="works"
          style={{ position: "relative", width: "100%", height: "100dvh", minHeight: "600px", display: "flex", alignItems: "center", overflow: "hidden" }}>
          <div className="section__bg" data-parallax="0.25" style={{ position: "absolute", inset: "-8%", zIndex: 0, overflow: "hidden", willChange: "transform" }}>
            <img src={sectionImages[2]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
          <div className="section__overlay" style={{ position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none", background: "linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.15) 25%, oklch(0 0 0 / 0.15) 75%, oklch(0 0 0 / 0.55) 100%)" }} />
          <div className="section__scrim" style={{ position: "absolute", inset: 0, zIndex: 2, background: "var(--c-bg)", opacity: 0, transition: "none", pointerEvents: "none" }} />

          <div className="section__content anim-content" style={{ position: "relative", zIndex: 3, width: "min(92%, 1280px)", marginInline: "auto" }}>
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="section__number">/ 02</p>
                <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-display)", fontWeight: 400, lineHeight: 1.2, color: "#fff" }}>精选作品</h2>
              </div>
              <Link href="/products" className="section__link">查看全部 →</Link>
            </div>

            {products.length === 0 ? (
              <StateCard type="empty" minHeight="200px" />
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gridTemplateRows: "1fr 1fr", gap: "2px", height: "55vh", minHeight: "360px" }}>
                {products.map((p, i) => (
                  <Link key={p.id} href={`/products/${p.slug}`}
                    style={{ position: "relative", overflow: "hidden", cursor: "pointer", ...(i === 0 ? { gridRow: "1 / -1" } : {}) }}>
                    <img src={p.coverImage || "/uploads/metal-ruler.png"} alt={p.title} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.35) contrast(1.2)" }} />
                    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: "var(--sp-lg)", background: "linear-gradient(transparent 35%, oklch(0 0 0 / 0.85))" }}>
                      <h3 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, color: "#fff" }}>{p.title}</h3>
                      <p style={{ fontSize: "var(--fs-small)", color: "oklch(0.68 0.01 270 / 0.5)" }}>{p.description}</p>
                    </div>
                    <span style={{ position: "absolute", top: "var(--sp-md)", right: "var(--sp-md)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", padding: "0.2em 0.6em", border: "1px solid rgb(255 255 255 / 0.12)", color: "oklch(0.68 0.01 270 / 0.55)", background: "oklch(0 0 0 / 0.35)", backdropFilter: "blur(4px)", zIndex: 2 }}>
                      {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Section 4: 引用 */}
        <section ref={(el) => { sectionsRef.current[3] = el; }} className="section" data-section="quote"
          style={{ position: "relative", width: "100%", height: "100dvh", minHeight: "600px", display: "flex", alignItems: "center", overflow: "hidden" }}>
          <div className="section__bg" data-parallax="0.2" style={{ position: "absolute", inset: "-8%", zIndex: 0, overflow: "hidden", willChange: "transform" }}>
            <img src={sectionImages[3]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
          <div className="section__overlay" style={{ position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none", background: "linear-gradient(180deg, oklch(0 0 0 / 0.6) 0%, oklch(0 0 0 / 0.2) 30%, oklch(0 0 0 / 0.2) 70%, oklch(0 0 0 / 0.6) 100%)" }} />
          <div className="section__scrim" style={{ position: "absolute", inset: 0, zIndex: 2, background: "var(--c-bg)", opacity: 0, transition: "none", pointerEvents: "none" }} />
          <div className="section__content section__content--center anim-content" style={{ position: "relative", zIndex: 3, width: "min(92%, 1280px)", marginInline: "auto", textAlign: "center" }}>
            <figure style={{ fontFamily: "var(--ff-display)", fontSize: "clamp(1.5rem, 3.8vw, 3.5rem)", fontWeight: 400, fontStyle: "italic", lineHeight: 1.35, color: "#fff", textShadow: "0 2px 40px oklch(0 0 0 / 0.5)", maxWidth: "680px", margin: "0 auto" }}>
              &ldquo;光影不是装饰，<br />它是空间的骨架。&rdquo;
            </figure>
            <p style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", color: "oklch(0.65 0.01 270 / 0.45)", marginTop: "var(--sp-lg)", letterSpacing: "0.25em", textTransform: "uppercase" }}>
              — 2026 · Atelier
            </p>
          </div>
        </section>
      </div>
    </>
  );
}
```

- [ ] **Step 2: 验证**

Run: `npm run dev` → 访问 `http://localhost:3000` → 4 屏全屏滚动、视差效果、叠化过渡均生效。

- [ ] **Step 3: Commit**

```bash
git add app/page.tsx app/home-client.tsx
git commit -m "feat: implement home page with 4-section parallax scrolling"
```

---

### Task 2.4：笔记列表 + 文章详情

**Files:**
- Create: `app/blog/page.tsx`, `app/blog/[slug]/page.tsx`

- [ ] **Step 1: 笔记列表页**

```tsx
// app/blog/page.tsx
import Link from "next/link";
import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { Tags } from "@/components/tags";
import { StateCard } from "@/components/state-card";

export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const articles = await prisma.article.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, coverImage: true, tags: true, readingTime: true, publishedAt: true },
  });

  return (
    <>
      <ParallaxHero
        image="/uploads/paper-folds-shadow.png"
        label="笔记"
        title="阅读 · 思考 · 记录"
        description="关于设计、技术与摄影的个人笔记"
      />

      <section style={{ padding: "var(--sp-xl) 0 var(--sp-3xl)" }}>
        <div className="container">
          {articles.length === 0 ? (
            <StateCard type="empty" />
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "2px" }}>
              {articles.map((a) => (
                <Link key={a.id} href={`/blog/${a.slug}`}
                  style={{
                    display: "block", padding: "var(--sp-xl) var(--sp-lg)",
                    border: "1px solid rgb(255 255 255 / 0.04)", transition: "border-color 0.3s var(--ease-expo)",
                  }}>
                  <article style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)" }}>
                    <div style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", display: "flex", gap: "var(--sp-sm)", alignItems: "center" }}>
                      <span>{a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : ""}</span>
                      <span style={{ width: 2, height: 2, borderRadius: "50%", background: "var(--c-muted)" }} />
                      <span>{a.readingTime} 分钟</span>
                    </div>
                    <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, lineHeight: 1.3 }}>{a.title}</h2>
                    <p style={{ color: "var(--c-fg-dim)", fontSize: "var(--fs-small)", lineHeight: 1.7 }}>{a.excerpt}</p>
                    <Tags tags={a.tags} />
                  </article>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: 文章详情页**

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { prisma } from "@/lib/db";
import { MarkdownRenderer } from "@/lib/markdown";
import { Tags } from "@/components/tags";
import { Footer } from "@/components/footer";

interface Props { params: Promise<{ slug: string }>; }

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug } });

  if (!article || !article.published) notFound();

  return (
    <>
      {/* Hero */}
      <header style={{ position: "relative", width: "100%", height: "60vh", minHeight: "400px", overflow: "hidden" }}>
        <img
          src={article.coverImage || "/uploads/venetian-blind-shadow.png"}
          alt={article.title}
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.5) contrast(1.15)" }}
        />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, transparent 30%, var(--c-bg) 100%)" }} />
      </header>

      {/* 正文 */}
      <article style={{ position: "relative", marginTop: "-80px", zIndex: 2, paddingBottom: "var(--sp-3xl)" }}>
        <div className="container--narrow">
          <Link href="/blog" style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginBottom: "var(--sp-lg)", display: "inline-flex", alignItems: "center", gap: "var(--sp-xs)" }}>
            ← 返回笔记列表
          </Link>

          <header style={{ marginBottom: "var(--sp-xl)" }}>
            <div style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", display: "flex", gap: "var(--sp-sm)", alignItems: "center", marginBottom: "var(--sp-md)" }}>
              <span>{article.publishedAt ? new Date(article.publishedAt).toISOString().slice(0, 10) : ""}</span>
              <span style={{ width: 2, height: 2, borderRadius: "50%", background: "var(--c-muted)" }} />
              <span>{article.readingTime} 分钟阅读</span>
            </div>
            <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-display)", fontWeight: 400, lineHeight: 1.15, marginBottom: "var(--sp-md)" }}>
              {article.title}
            </h1>
            <Tags tags={article.tags} />
          </header>

          <MarkdownRenderer content={article.content} />
        </div>
      </article>

      <Footer />
    </>
  );
}
```

- [ ] **Step 3: 验证**

访问 `/blog` → 笔记列表；点击文章 → `/blog/building-space-with-light` → 文章详情渲染。

- [ ] **Step 4: Commit**

```bash
git add app/blog/
git commit -m "feat: implement blog list and article detail pages"
```

---

### Task 2.5：作品画廊 + 作品详情

**Files:**
- Create: `app/products/page.tsx`, `app/products/[slug]/page.tsx`

- [ ] **Step 1: 作品画廊页**

```tsx
// app/products/page.tsx
import Link from "next/link";
import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { StateCard } from "@/components/state-card";

export const dynamic = "force-dynamic";

export default async function ProductsPage() {
  const products = await prisma.product.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, description: true, coverImage: true, status: true, tags: true },
  });

  return (
    <>
      <ParallaxHero
        image="/uploads/plaster-geometric.png"
        label="作品"
        title="创作 · 实验 · 工具"
        description="个人项目和实验性的数字作品"
      />

      <section style={{ padding: "var(--sp-xl) 0 var(--sp-3xl)" }}>
        <div className="container">
          {products.length === 0 ? (
            <StateCard type="empty" />
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1.4fr 0.7fr 1fr", gridAutoRows: "240px", gap: "2px" }}>
              {products.map((p) => (
                <Link key={p.id} href={`/products/${p.slug}`}
                  style={{ position: "relative", overflow: "hidden", background: "var(--c-bg)", cursor: "pointer" }}>
                  <img src={p.coverImage || "/uploads/metal-ruler.png"} alt={p.title}
                    style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.35) contrast(1.2)", transition: "transform 0.7s var(--ease-expo)" }} />
                  <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: "var(--sp-md)", background: "linear-gradient(transparent 40%, oklch(0 0 0 / 0.8))" }}>
                    <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, color: "#fff" }}>{p.title}</h2>
                    <p style={{ fontSize: "var(--fs-small)", color: "oklch(0.65 0.01 270 / 0.55)", marginTop: "2px" }}>{p.description}</p>
                  </div>
                  <span style={{ position: "absolute", top: "var(--sp-sm)", right: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", padding: "0.15em 0.5em", border: "1px solid rgb(255 255 255 / 0.1)", color: "oklch(0.68 0.01 270 / 0.55)", background: "oklch(0 0 0 / 0.3)", backdropFilter: "blur(4px)", zIndex: 2 }}>
                    {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: 作品详情页 (iframe + 信息面板)**

```tsx
// app/products/[slug]/page.tsx
import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { ProductDetailClient } from "./product-detail-client";

interface Props { params: Promise<{ slug: string }>; }

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await prisma.product.findUnique({ where: { slug } });
  if (!product || !product.published) notFound();

  return <ProductDetailClient product={product} />;
}
```

```tsx
// app/products/[slug]/product-detail-client.tsx
"use client";
import Link from "next/link";
import { useState } from "react";

export function ProductDetailClient({ product }: { product: any }) {
  const [panelOpen, setPanelOpen] = useState(false);

  const statusLabel = product.status === "online" ? "在线" : product.status === "developing" ? "开发中" : "已下线";

  return (
    <main style={{ height: "100%", overflow: "hidden", background: "#000" }}>
      {/* IFrame 全屏 */}
      <div style={{ position: "fixed", inset: 0, zIndex: 1 }}>
        {product.url ? (
          <iframe src={product.url} style={{ width: "100%", height: "100%", border: 0 }} sandbox="allow-scripts allow-same-origin" title={product.title} />
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--c-fg-dim)", fontFamily: "var(--ff-body)" }}>
            暂无运行文件
          </div>
        )}
      </div>

      {/* 浮动工具栏 */}
      <div style={{
        position: "fixed", top: "var(--sp-md)", left: "50%", transform: "translateX(-50%)", zIndex: 10,
        display: "flex", alignItems: "center", gap: "var(--sp-sm)", padding: "var(--sp-sm) var(--sp-md)",
        background: "oklch(0.08 0.01 270 / 0.85)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)",
        border: "1px solid var(--c-border)", borderRadius: "var(--radius-lg)",
        fontSize: "var(--fs-meta)", fontFamily: "var(--ff-body)", color: "var(--c-fg)",
      }}>
        <Link href="/products" style={{ display: "flex", alignItems: "center", gap: "var(--sp-2xs)", color: "var(--c-fg-dim)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", transition: "color 0.3s ease" }}>
          ← 返回
        </Link>
        <span style={{ width: 1, height: 16, background: "var(--c-border)" }} />
        <span style={{ fontWeight: 400, fontSize: "var(--fs-small)" }}>{product.title}</span>
        <div style={{ display: "flex", gap: "var(--sp-xs)", marginLeft: "auto" }}>
          {product.url && (
            <button onClick={() => window.open(product.url, "_blank")}
              style={{ padding: "var(--sp-2xs) var(--sp-sm)", background: "none", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", color: "var(--c-fg-dim)", cursor: "pointer", fontFamily: "var(--ff-body)", fontSize: "var(--fs-meta)", transition: "all 0.3s ease" }}>
              新窗口
            </button>
          )}
          <button onClick={() => setPanelOpen(!panelOpen)}
            style={{ padding: "var(--sp-2xs) var(--sp-sm)", background: "none", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", color: "var(--c-fg-dim)", cursor: "pointer", fontFamily: "var(--ff-body)", fontSize: "var(--fs-meta)", transition: "all 0.3s ease" }}>
            信息
          </button>
        </div>
      </div>

      {/* 信息面板 */}
      <div style={{
        position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 10,
        transform: panelOpen ? "translateY(0)" : "translateY(calc(100% - 48px))",
        transition: "transform 0.5s var(--ease-expo)",
        background: "oklch(0.06 0.008 270 / 0.92)", backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)",
        borderTop: "1px solid var(--c-border)",
      }}>
        <div onClick={() => setPanelOpen(!panelOpen)}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 48, cursor: "pointer", userSelect: "none" }}>
          <div style={{ width: 32, height: 3, borderRadius: 2, background: panelOpen ? "var(--c-fg-dim)" : "var(--c-muted)", transition: "background 0.3s ease" }} />
        </div>
        <div style={{ padding: "0 var(--sp-xl) var(--sp-xl)", maxHeight: "50vh", overflowY: "auto", display: "grid", gridTemplateColumns: "200px 1fr", gap: "var(--sp-xl)" }}>
          <img src={product.coverImage || "/uploads/metal-ruler.png"} alt={product.title}
            style={{ width: "100%", aspectRatio: "4/3", objectFit: "cover", filter: "saturate(0.5) contrast(1.15)", borderRadius: "var(--radius-sm)" }} />
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)" }}>
            <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400 }}>{product.title}</h1>
            <p style={{ color: "var(--c-fg-dim)", fontSize: "var(--fs-body)", lineHeight: 1.7 }}>{product.description}</p>
            <div style={{ display: "flex", gap: "var(--sp-lg)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)" }}>
              <div><span style={{ fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>标识</span><br />{product.slug}</div>
              <div><span style={{ fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>状态</span><br />{statusLabel}</div>
              <div><span style={{ fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>更新</span><br />{new Date(product.updatedAt).toISOString().slice(0, 10)}</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: 验证**

访问 `/products` → 作品画廊；点击 → `/products/tools-2026` → iframe + 工具栏 + 信息抽屉面板。

- [ ] **Step 4: Commit**

```bash
git add app/products/
git commit -m "feat: implement product gallery and detail pages"
```

---

### Task 2.6：关于页

**Files:**
- Create: `app/about/page.tsx`

- [ ] **Step 1: 关于页**

```tsx
// app/about/page.tsx
import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { Footer } from "@/components/footer";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const siteInfo = await prisma.siteInfo.findFirst({ where: { id: 1 } });

  const bio = siteInfo?.aboutBio ?? "光影之间的创作者。";
  const links = (siteInfo?.aboutLinks as Array<{ label: string; url: string }>) ?? [];

  return (
    <>
      <ParallaxHero
        image="/uploads/prism-light.png"
        label="关于"
        title="光影之间"
        description="记录、实验与创作"
      />

      <section style={{ padding: "var(--sp-2xl) 0 var(--sp-3xl)" }}>
        <div className="container--narrow">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--sp-2xl)" }}>
            {/* 简介 */}
            <div>
              <p style={{ fontSize: "var(--fs-body)", lineHeight: 1.85, color: "var(--c-fg-dim)" }}>
                {bio}
              </p>
            </div>

            {/* 链接 */}
            <div>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-sm)" }}>
                {links.map((link, i) => (
                  <a key={i} href={link.url} target="_blank" rel="noopener noreferrer"
                    style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--sp-sm) 0", borderBottom: "1px solid var(--c-border)", transition: "border-color 0.3s ease" }}>
                    <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)" }}>{link.label}</span>
                    <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>→</span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add app/about/
git commit -m "feat: implement about page"
```

---

## 阶段 3：认证 + 后台

### Task 3.1：认证 API + 中间件

**Files:**
- Create: `lib/auth.ts`, `app/api/auth/login/route.ts`, `app/api/auth/logout/route.ts`, `app/api/auth/check/route.ts`, `middleware.ts`

- [ ] **Step 1: JWT session 工具**

```typescript
// lib/auth.ts
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";

const SECRET = new TextEncoder().encode(process.env.ADMIN_PASSWORD || "fallback-secret-change-me");
const COOKIE_NAME = "atelier_session";
const MAX_AGE = 60 * 60 * 24 * 7; // 7 days

export async function createSession(): Promise<string> {
  return new SignJWT({ role: "admin" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(SECRET);
}

export async function verifySession(token: string): Promise<boolean> {
  try {
    await jwtVerify(token, SECRET);
    return true;
  } catch {
    return false;
  }
}

export async function getSession(): Promise<boolean> {
  const cookieStore = await cookies();
  const token = cookieStore.get(COOKIE_NAME)?.value;
  if (!token) return false;
  return verifySession(token);
}

export async function setSessionCookie(token: string) {
  const cookieStore = await cookies();
  cookieStore.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: MAX_AGE,
    path: "/",
  });
}

export async function clearSessionCookie() {
  const cookieStore = await cookies();
  cookieStore.delete(COOKIE_NAME);
}
```

- [ ] **Step 2: 登录 API**

```typescript
// app/api/auth/login/route.ts
import { NextResponse } from "next/server";
import { createSession, setSessionCookie } from "@/lib/auth";

export async function POST(req: Request) {
  const { password } = await req.json();
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (!adminPassword) {
    return NextResponse.json({ error: "服务器未配置密码" }, { status: 500 });
  }

  if (password !== adminPassword) {
    return NextResponse.json({ error: "密码错误" }, { status: 401 });
  }

  const token = await createSession();
  await setSessionCookie(token);

  return NextResponse.json({ success: true });
}
```

- [ ] **Step 3: 登出 API**

```typescript
// app/api/auth/logout/route.ts
import { NextResponse } from "next/server";
import { clearSessionCookie } from "@/lib/auth";

export async function POST() {
  await clearSessionCookie();
  return NextResponse.json({ success: true });
}
```

- [ ] **Step 4: 登录状态检查 API**

```typescript
// app/api/auth/check/route.ts
import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";

export async function GET() {
  const authenticated = await getSession();
  return NextResponse.json({ authenticated });
}
```

- [ ] **Step 5: 中间件（路由保护）**

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

const SECRET = new TextEncoder().encode(process.env.ADMIN_PASSWORD || "fallback-secret-change-me");

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const token = req.cookies.get("atelier_session")?.value;

  let authenticated = false;
  if (token) {
    try { await jwtVerify(token, SECRET); authenticated = true; } catch {}
  }

  // 后台页面保护
  if (pathname.startsWith("/admin") && pathname !== "/admin/login") {
    if (!authenticated) {
      return NextResponse.redirect(new URL("/login", req.url));
    }
  }

  // API 写操作保护
  if (pathname.startsWith("/api/")) {
    const method = req.method;
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
    // /api/auth/login 和 /api/auth/logout 不需要认证
    if (isWrite && !pathname.startsWith("/api/auth/")) {
      if (!authenticated) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/api/:path*"],
};
```

- [ ] **Step 6: 验证**

```bash
curl -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"password":"wrong"}' # → 401
curl -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"password":"atelier2026"}' # → 200 + set-cookie
```

- [ ] **Step 7: Commit**

```bash
git add lib/auth.ts app/api/auth/ middleware.ts
git commit -m "feat: implement auth API, session management, and middleware"
```

---

### Task 3.2：登录页

**Files:**
- Create: `app/login/page.tsx`

- [ ] **Step 1: 登录页（Client Component，含表单交互）**

```tsx
// app/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    setLoading(false);

    if (res.ok) {
      router.push("/admin");
      router.refresh();
    } else {
      setError("密码错误，请重试。");
    }
  };

  return (
    <main style={{ display: "flex", minHeight: "100vh", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
      {/* 背景 */}
      <div style={{ position: "absolute", inset: 0, zIndex: 0 }}>
        <img src="/uploads/glass-shadow.png" alt=""
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.3) contrast(1.2) brightness(0.4)" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, oklch(0.035 0.008 275 / 0.7) 0%, var(--c-bg) 100%)" }} />
      </div>

      {/* 登录卡片 */}
      <div style={{
        position: "relative", zIndex: 2, width: "min(92%, 400px)", padding: "var(--sp-xl)",
        background: "oklch(0.08 0.01 270 / 0.85)", backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)",
        border: "1px solid var(--c-border)", borderRadius: "var(--radius-lg)",
        display: "flex", flexDirection: "column", gap: "var(--sp-lg)",
      }}>
        <div style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-display)", fontWeight: 400, textAlign: "center", color: "var(--c-light)" }}>
          Atelier
        </div>

        <div style={{ textAlign: "center" }}>
          <h1 style={{ fontFamily: "var(--ff-body)", fontSize: "var(--fs-h3)", fontWeight: 400, marginBottom: "var(--sp-xs)" }}>登录</h1>
          <p style={{ color: "var(--c-fg-dim)", fontSize: "var(--fs-small)" }}>输入凭据以管理后台</p>
        </div>

        {error && (
          <div style={{ padding: "var(--sp-sm) var(--sp-md)", background: "oklch(0.5 0.15 30 / 0.15)", border: "1px solid oklch(0.5 0.15 30 / 0.3)", borderRadius: "var(--radius-sm)", color: "oklch(0.7 0.12 30)", fontSize: "var(--fs-small)" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)" }}>
            <label style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="输入密码"
              style={{
                padding: "var(--sp-sm) var(--sp-md)", background: "oklch(0.15 0.012 270 / 0.6)",
                border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)",
                color: "var(--c-fg)", fontFamily: "var(--ff-body)", fontSize: "var(--fs-body)", outline: "none",
              }}
            />
          </div>
          <button type="submit" disabled={loading}
            className="btn" style={{ justifyContent: "center", opacity: loading ? 0.5 : 1 }}>
            {loading ? "验证中…" : "登录"}
          </button>
        </form>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: 验证**

访问 `/login` → 输错密码显示错误 → 输正确密码跳转 `/admin`。

- [ ] **Step 3: Commit**

```bash
git add app/login/
git commit -m "feat: implement login page with client-side auth"
```

---

### Task 3.3：后台布局 + 侧边栏

**Files:**
- Create: `components/admin/sidebar.tsx`, `app/admin/layout.tsx`

- [ ] **Step 1: 侧边栏组件**

```tsx
// components/admin/sidebar.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const ADMIN_NAV = [
  { href: "/admin", label: "仪表盘", icon: "dashboard" },
  { href: "/admin/articles", label: "文章管理", icon: "article" },
  { href: "/admin/products", label: "产品管理", icon: "product" },
  { href: "/admin/about", label: "关于页", icon: "about" },
  { href: "/admin/mascot", label: "看板娘", icon: "mascot" },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside style={{
      width: 240, minWidth: 240, height: "100vh", position: "fixed", top: 0, left: 0, zIndex: 50,
      display: "flex", flexDirection: "column",
      background: "var(--c-surf)", borderRight: "1px solid var(--c-border)",
    }}>
      {/* 头部 */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--sp-md) var(--sp-lg)", borderBottom: "1px solid var(--c-border)" }}>
        <span style={{ fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)", letterSpacing: "0.1em", color: "var(--c-fg)", textTransform: "uppercase" }}>
          管理后台
        </span>
      </div>

      {/* 导航 */}
      <nav style={{ flex: 1, padding: "var(--sp-sm)", display: "flex", flexDirection: "column", gap: "2px" }}>
        {ADMIN_NAV.map(({ href, label }) => {
          const active = pathname === href || (href !== "/admin" && pathname.startsWith(href));
          return (
            <Link key={href} href={href} style={{
              display: "flex", alignItems: "center", gap: "var(--sp-sm)", padding: "var(--sp-sm) var(--sp-md)",
              borderRadius: "var(--radius-sm)", fontSize: "var(--fs-small)", color: active ? "var(--c-fg)" : "var(--c-fg-dim)",
              background: active ? "var(--c-surf-2)" : "transparent", transition: "all 0.2s var(--ease-expo)",
              fontFamily: "var(--ff-body)",
            }}>
              {label}
            </Link>
          );
        })}
      </nav>

      {/* 底部 */}
      <div style={{ padding: "var(--sp-sm)", borderTop: "1px solid var(--c-border)" }}>
        <Link href="/" style={{
          display: "flex", alignItems: "center", gap: "var(--sp-sm)", padding: "var(--sp-sm) var(--sp-md)",
          borderRadius: "var(--radius-sm)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)",
          fontFamily: "var(--ff-body)",
        }}>
          ← 返回首页
        </Link>
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: 后台布局**

```tsx
// app/admin/layout.tsx
import { AdminSidebar } from "@/components/admin/sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      <AdminSidebar />
      <main style={{ flex: 1, marginLeft: 240, overflow: "auto", padding: "var(--sp-xl)", background: "var(--c-bg)" }}>
        {children}
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add components/admin/sidebar.tsx app/admin/layout.tsx
git commit -m "feat: add admin sidebar and layout"
```

---

### Task 3.4：仪表盘

**Files:**
- Create: `app/admin/page.tsx`

```tsx
// app/admin/page.tsx
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function AdminDashboard() {
  const [articleCount, productCount, publishedArticles, recentArticles] = await Promise.all([
    prisma.article.count(),
    prisma.product.count(),
    prisma.article.count({ where: { published: true } }),
    prisma.article.findMany({ orderBy: { createdAt: "desc" }, take: 5, select: { id: true, title: true, createdAt: true, published: true } }),
  ]);

  return (
    <div>
      <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400, marginBottom: "var(--sp-xl)" }}>仪表盘</h1>

      {/* 统计卡片 */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--sp-md)", marginBottom: "var(--sp-xl)" }}>
        <div style={{ padding: "var(--sp-lg)", background: "var(--c-surf)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)" }}>
          <p style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)", marginBottom: "var(--sp-xs)" }}>文章总数</p>
          <p style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400 }}>{articleCount}</p>
          <p style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>{publishedArticles} 已发布</p>
        </div>
        <div style={{ padding: "var(--sp-lg)", background: "var(--c-surf)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)" }}>
          <p style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)", marginBottom: "var(--sp-xs)" }}>作品总数</p>
          <p style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400 }}>{productCount}</p>
        </div>
        <div style={{ padding: "var(--sp-lg)", background: "var(--c-surf)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)" }}>
          <p style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)", marginBottom: "var(--sp-xs)" }}>发布率</p>
          <p style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400 }}>
            {articleCount > 0 ? Math.round((publishedArticles / articleCount) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* 最近文章 */}
      <div style={{ background: "var(--c-surf)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", padding: "var(--sp-lg)" }}>
        <h2 style={{ fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--c-fg-dim)", marginBottom: "var(--sp-md)" }}>最近创建</h2>
        {recentArticles.map((a) => (
          <div key={a.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--sp-sm) 0", borderBottom: "1px solid var(--c-border)" }}>
            <div>
              <span style={{ fontSize: "var(--fs-small)", color: "var(--c-fg)" }}>{a.title}</span>
              <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)", marginLeft: "var(--sp-sm)" }}>
                {new Date(a.createdAt).toISOString().slice(0, 10)}
              </span>
            </div>
            <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", padding: "1px 8px", border: "1px solid var(--c-border)", borderRadius: "1px", color: a.published ? "var(--c-fg-dim)" : "var(--c-muted)" }}>
              {a.published ? "已发布" : "草稿"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Commit**

```bash
git add app/admin/page.tsx
git commit -m "feat: implement admin dashboard"
```

---

### Task 3.5：文章管理 CRUD + API

**Files:**
- Create: `app/api/articles/route.ts`, `app/api/articles/[id]/route.ts`
- Create: `app/admin/articles/page.tsx`, `app/admin/articles/new/page.tsx`, `app/admin/articles/[id]/edit/page.tsx`
- Create: `components/admin/article-form.tsx`

- [ ] **Step 1: 文章 API**

```typescript
// app/api/articles/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  const articles = await prisma.article.findMany({
    orderBy: { createdAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, tags: true, published: true, featured: true, readingTime: true, createdAt: true, updatedAt: true },
  });
  return NextResponse.json(articles);
}

export async function POST(req: Request) {
  const body = await req.json();
  const article = await prisma.article.create({ data: body });
  return NextResponse.json(article, { status: 201 });
}
```

```typescript
// app/api/articles/[id]/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const article = await prisma.article.findUnique({ where: { id: parseInt(id) } });
  if (!article) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(article);
}

export async function PUT(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const article = await prisma.article.update({ where: { id: parseInt(id) }, data: body });
  return NextResponse.json(article);
}

export async function DELETE(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await prisma.article.delete({ where: { id: parseInt(id) } });
  return NextResponse.json({ success: true });
}
```

- [ ] **Step 2: 文章编辑表单组件**

```tsx
// components/admin/article-form.tsx
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface ArticleFormData {
  slug: string; title: string; excerpt: string; content: string;
  coverImage: string; tags: string; readingTime: number;
  featured: boolean; published: boolean;
}

const empty: ArticleFormData = {
  slug: "", title: "", excerpt: "", content: "",
  coverImage: "", tags: "", readingTime: 3,
  featured: false, published: false,
};

export function ArticleForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ArticleFormData>(empty);
  const [saving, setSaving] = useState(false);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "",
        title: initial.title ?? "",
        excerpt: initial.excerpt ?? "",
        content: initial.content ?? "",
        coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "),
        readingTime: initial.readingTime ?? 3,
        featured: initial.featured ?? false,
        published: initial.published ?? false,
      });
    }
  }, [initial]);

  const handleChange = (field: keyof ArticleFormData, value: string | number | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const payload = {
      ...form,
      tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
    };

    const url = isEdit ? `/api/articles/${initial.id}` : "/api/articles";
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    setSaving(false);

    if (res.ok) {
      router.push("/admin/articles");
      router.refresh();
    } else {
      alert("保存失败");
    }
  };

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "var(--sp-sm)", background: "var(--c-bg)",
    border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)",
    color: "var(--c-fg)", fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)",
    outline: "none",
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)", maxWidth: 800 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--sp-md)" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
          标识 (slug)
          <input style={inputStyle} value={form.slug} onChange={(e) => handleChange("slug", e.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
          阅读时长 (分钟)
          <input style={inputStyle} type="number" value={form.readingTime} onChange={(e) => handleChange("readingTime", parseInt(e.target.value) || 3)} />
        </label>
      </div>

      <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
        标题
        <input style={inputStyle} value={form.title} onChange={(e) => handleChange("title", e.target.value)} required />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
        摘要
        <textarea style={{ ...inputStyle, height: 60, resize: "vertical" }} value={form.excerpt} onChange={(e) => handleChange("excerpt", e.target.value)} />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
        正文 (Markdown)
        <textarea style={{ ...inputStyle, height: 280, resize: "vertical", fontFamily: "var(--ff-mono)" }} value={form.content} onChange={(e) => handleChange("content", e.target.value)} />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
        封面图 URL
        <input style={inputStyle} value={form.coverImage} onChange={(e) => handleChange("coverImage", e.target.value)} />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
        标签 (逗号分隔)
        <input style={inputStyle} value={form.tags} onChange={(e) => handleChange("tags", e.target.value)} />
      </label>

      <div style={{ display: "flex", gap: "var(--sp-lg)" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", cursor: "pointer" }}>
          <input type="checkbox" checked={form.published} onChange={(e) => handleChange("published", e.target.checked)} /> 发布
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", cursor: "pointer" }}>
          <input type="checkbox" checked={form.featured} onChange={(e) => handleChange("featured", e.target.checked)} /> 精选
        </label>
      </div>

      <button type="submit" className="btn" disabled={saving} style={{ alignSelf: "flex-start" }}>
        {saving ? "保存中…" : isEdit ? "更新文章" : "创建文章"}
      </button>
    </form>
  );
}
```

- [ ] **Step 3: 文章列表页**

```tsx
// app/admin/articles/page.tsx
import Link from "next/link";
import { prisma } from "@/lib/db";
import { AdminArticlesClient } from "./articles-client";

export const dynamic = "force-dynamic";

export default async function AdminArticlesPage() {
  const articles = await prisma.article.findMany({
    orderBy: { createdAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, tags: true, published: true, updatedAt: true },
  });
  return <AdminArticlesClient articles={articles} />;
}
```

```tsx
// app/admin/articles/articles-client.tsx
"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Tags } from "@/components/tags";

export function AdminArticlesClient({ articles }: { articles: any[] }) {
  const router = useRouter();

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`确定删除「${title}」？`)) return;
    await fetch(`/api/articles/${id}`, { method: "DELETE" });
    router.refresh();
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--sp-xl)" }}>
        <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400 }}>文章管理</h1>
        <Link href="/admin/articles/new" className="btn">新建文章</Link>
      </div>

      <div style={{ background: "var(--c-surf)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)" }}>
        {articles.map((a) => (
          <div key={a.id} style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.2fr) 180px 100px 120px 120px", gap: "var(--sp-md)", alignItems: "center", padding: "var(--sp-md) var(--sp-lg)", borderBottom: "1px solid var(--c-border)" }}>
            <div>
              <div style={{ fontSize: "var(--fs-small)", fontWeight: 500, color: "var(--c-fg)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.title}</div>
              <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>{a.slug}</div>
            </div>
            <Tags tags={a.tags} />
            <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: a.published ? "var(--c-fg-dim)" : "var(--c-muted)" }}>
              {a.published ? "已发布" : "草稿"}
            </span>
            <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>
              {new Date(a.updatedAt).toISOString().slice(0, 10)}
            </span>
            <div style={{ display: "flex", gap: "var(--sp-sm)", justifyContent: "flex-end" }}>
              <Link href={`/admin/articles/${a.id}/edit`} className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)" }}>编辑</Link>
              <button onClick={() => handleDelete(a.id, a.title)} className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)", borderColor: "oklch(0.5 0.15 30 / 0.3)", color: "oklch(0.7 0.12 30)" }}>删除</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: 新建 + 编辑页**

```tsx
// app/admin/articles/new/page.tsx
import { ArticleForm } from "@/components/admin/article-form";

export default function NewArticlePage() {
  return (
    <div>
      <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400, marginBottom: "var(--sp-xl)" }}>新建文章</h1>
      <ArticleForm />
    </div>
  );
}
```

```tsx
// app/admin/articles/[id]/edit/page.tsx
import { prisma } from "@/lib/db";
import { notFound } from "next/navigation";
import { ArticleForm } from "@/components/admin/article-form";

interface Props { params: Promise<{ id: string }>; }

export default async function EditArticlePage({ params }: Props) {
  const { id } = await params;
  const article = await prisma.article.findUnique({ where: { id: parseInt(id) } });
  if (!article) notFound();

  return (
    <div>
      <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400, marginBottom: "var(--sp-xl)" }}>编辑文章</h1>
      <ArticleForm initial={article} />
    </div>
  );
}
```

- [ ] **Step 5: 验证**

登录 → `/admin/articles` → 列表 → 新建 → 编辑 → 删除。全部操作通过 API 走通。

- [ ] **Step 6: Commit**

```bash
git add app/api/articles/ app/admin/articles/ components/admin/article-form.tsx
git commit -m "feat: implement article CRUD API and admin pages"
```

---

### Task 3.6：作品管理 + 图片上传 + 关于页编辑

**Files:**
- Create: `app/api/products/route.ts`, `app/api/products/[id]/route.ts`
- Create: `app/api/upload/route.ts`, `app/api/site-info/route.ts`
- Create: `app/admin/products/page.tsx`, `app/admin/products/new/page.tsx`, `app/admin/products/[id]/edit/page.tsx`
- Create: `components/admin/product-form.tsx`, `components/admin/image-upload.tsx`
- Create: `app/admin/about/page.tsx`, `app/admin/mascot/page.tsx`

由于作品管理结构与文章类似（CRUD 表单 + 列表），此处列出关键差异和 API 代码，完整文件按相同模式创建。

- [ ] **Step 1: 作品 API（与文章 API 结构相同，entity 替换为 product）**

```typescript
// app/api/products/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  const products = await prisma.product.findMany({ orderBy: { createdAt: "desc" } });
  return NextResponse.json(products);
}

export async function POST(req: Request) {
  const body = await req.json();
  const product = await prisma.product.create({ data: body });
  return NextResponse.json(product, { status: 201 });
}
```

```typescript
// app/api/products/[id]/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await prisma.product.findUnique({ where: { id: parseInt(id) } });
  if (!product) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(product);
}

export async function PUT(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const product = await prisma.product.update({ where: { id: parseInt(id) }, data: body });
  return NextResponse.json(product);
}

export async function DELETE(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await prisma.product.delete({ where: { id: parseInt(id) } });
  return NextResponse.json({ success: true });
}
```

- [ ] **Step 2: 图片上传 API**

```typescript
// app/api/upload/route.ts
import { NextResponse } from "next/server";
import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  const formData = await req.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return NextResponse.json({ error: "No file" }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  const uploadsDir = join(process.cwd(), "public", "uploads");
  await mkdir(uploadsDir, { recursive: true });

  const filename = `${Date.now()}-${file.name}`;
  const filepath = join(uploadsDir, filename);
  await writeFile(filepath, buffer);

  const url = `/uploads/${filename}`;

  // 记录到数据库
  const media = await prisma.media.create({
    data: {
      filename: file.name,
      url,
      alt: "",
      width: 0,
      height: 0,
    },
  });

  return NextResponse.json({ url, id: media.id });
}
```

- [ ] **Step 3: 站点信息 API**

```typescript
// app/api/site-info/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  const info = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  if (!info) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(info);
}

export async function PUT(req: Request) {
  const body = await req.json();
  const info = await prisma.siteInfo.upsert({
    where: { id: 1 },
    update: body,
    create: { id: 1, ...body },
  });
  return NextResponse.json(info);
}
```

- [ ] **Step 4: 关于页编辑**

```tsx
// app/admin/about/page.tsx
import { prisma } from "@/lib/db";
import { AboutEditor } from "./about-editor";

export const dynamic = "force-dynamic";

export default async function AdminAboutPage() {
  const info = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  return <AboutEditor info={info} />;
}
```

```tsx
// app/admin/about/about-editor.tsx
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export function AboutEditor({ info }: { info: any }) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [bio, setBio] = useState(info?.aboutBio ?? "");
  const [linksJson, setLinksJson] = useState(JSON.stringify((info?.aboutLinks as any[]) ?? [], null, 2));

  const handleSave = async () => {
    setSaving(true);
    let links = [];
    try { links = JSON.parse(linksJson); } catch { alert("链接 JSON 格式错误"); setSaving(false); return; }

    await fetch("/api/site-info", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aboutBio: bio, aboutLinks: links }),
    });
    setSaving(false);
    router.refresh();
  };

  const textareaStyle: React.CSSProperties = {
    width: "100%", padding: "var(--sp-sm)", background: "var(--c-bg)",
    border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)",
    color: "var(--c-fg)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", outline: "none", resize: "vertical",
  };

  return (
    <div>
      <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400, marginBottom: "var(--sp-xl)" }}>编辑关于页</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-lg)", maxWidth: 700 }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
          个人简介
          <textarea style={{ ...textareaStyle, height: 120 }} value={bio} onChange={(e) => setBio(e.target.value)} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "var(--sp-xs)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>
          链接列表 (JSON)
          <textarea style={{ ...textareaStyle, height: 200 }} value={linksJson} onChange={(e) => setLinksJson(e.target.value)} />
        </label>
        <button className="btn" onClick={handleSave} disabled={saving} style={{ alignSelf: "flex-start" }}>
          {saving ? "保存中…" : "保存"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: 吉祥物管理页（原型为占位页，用 StateCard 提示）**

```tsx
// app/admin/mascot/page.tsx
import { StateCard } from "@/components/state-card";

export default function MascotPage() {
  return (
    <div>
      <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h2)", fontWeight: 400, marginBottom: "var(--sp-xl)" }}>看板娘</h1>
      <StateCard type="empty" title="功能开发中" desc="看板娘管理功能即将上线。" minHeight="300px" />
    </div>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add app/api/products/ app/api/upload/ app/api/site-info/
git add app/admin/products/ app/admin/about/ app/admin/mascot/
git add components/admin/
git commit -m "feat: implement product CRUD, image upload, site-info editor, and mascot placeholder"
```

---

## 阶段 4：打磨 & 部署

### Task 4.1：SEO 元数据

**Files:**
- Modify: `app/layout.tsx`, `app/blog/[slug]/page.tsx`, `app/products/[slug]/page.tsx`

- [ ] **Step 1: 全局 SEO + 动态页面元数据**

根布局已有基础 `metadata`。为文章和作品详情页添加 `generateMetadata`：

```typescript
// 在 app/blog/[slug]/page.tsx 中添加:
import type { Metadata } from "next";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug }, select: { title: true, excerpt: true, coverImage: true } });
  if (!article) return { title: "未找到" };
  return {
    title: `${article.title} · Atelier`,
    description: article.excerpt,
    openGraph: {
      title: article.title,
      description: article.excerpt,
      images: [article.coverImage || ""],
    },
  };
}
```

作品详情页同理。

- [ ] **Step 2: Commit**

```bash
git add app/layout.tsx app/blog/ app/products/
git commit -m "feat: add SEO metadata and Open Graph tags"
```

---

### Task 4.2：响应式 + 性能检查

- [ ] **Step 1: 在 768px 和 430px 宽度下检查每个页面**

验证要点：
- 导航在移动端隐藏链接（globals.css 中已有 `@media` 规则）
- 首页 section 在移动端自适应
- 后台管理侧边栏在移动端的表现
- 登录卡片不超出屏幕

- [ ] **Step 2: 运行 Lighthouse 并修复关键问题**

```bash
npm run build
npm start
```

检查: 图片有无使用 `loading="lazy"`、字体有无预加载、动画有无 GPU 加速 (`will-change`)

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "fix: responsive polish and performance optimizations"
```

---

### Task 4.3：部署

- [ ] **Step 1: 构建生产版本**

```bash
npm run build
```

Expected: 无 TypeScript 错误，所有页面编译成功。

- [ ] **Step 2: 服务器部署**

服务器上:
```bash
# 安装 Node.js 18+
# 安装 PostgreSQL 并创建数据库
createdb atelier

# 配置 .env
# DATABASE_URL="postgresql://..."
# ADMIN_PASSWORD="..."

# 构建 + 迁移 + 种子
npm ci
npx prisma migrate deploy
npx prisma db seed
npm run build

# 用 PM2 运行
npm install -g pm2
pm2 start npm --name "atelier" -- start
pm2 save
```

- [ ] **Step 3: 验证线上**

访问服务器域名 → 确认所有页面正常、登录正常、管理功能正常。

---

## 完成

**所有阶段完成后的验收清单：**

- [ ] `/` 首页 4 屏视差滚动，动画流畅
- [ ] `/blog` 笔记列表，有数据
- [ ] `/blog/slug` 文章详情，Markdown 渲染 + 代码高亮
- [ ] `/products` 作品画廊
- [ ] `/products/slug` 作品 iframe + 信息面板
- [ ] `/about` 关于页，数据来自 SiteInfo 表
- [ ] `/login` 登录页，密码校验
- [ ] `/admin` 仪表盘，统计数据
- [ ] `/admin/articles` 文章 CRUD
- [ ] `/admin/products` 作品 CRUD
- [ ] `/admin/about` 关于编辑保存
- [ ] `/api/auth/check` 返回认证状态
- [ ] 未登录访问 `/admin` → 跳转 `/login`
- [ ] 图片上传成功，返回 URL
