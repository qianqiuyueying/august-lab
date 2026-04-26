# About 页面重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将分散的 About 页配置合并为专属数据模型，后台"页面管理"改造为 About 专属编辑器，移除通用 Page 管理系统。

**Architecture:** 新建 AboutPage ORM 模型和 REST 接口，前端用新 API 替换三层降级逻辑。通用 Page CRUD 和 `/:slug` 通配路由整体移除，保留产品/文章详情页。

**Tech Stack:** FastAPI + SQLAlchemy (async) + Alembic (后端), React + TypeScript + Vite (前端)

---

## 文件清单

### 新建
- `backend/app/models/about_page.py` — AboutPage ORM 模型
- `backend/app/schemas/about.py` — Pydantic 请求/响应模式
- `backend/app/routers/about.py` — GET/PUT 接口
- `backend/alembic/versions/<timestamp>_add_about_page_table.py` — 数据库迁移
- `frontend/src/api/about.ts` — About API 客户端
- `frontend/src/components/admin/TagInput.tsx` — 技术栈标签输入组件

### 修改
- `backend/app/main.py:1-32` — 移除 pages router，添加 about router
- `backend/app/models/__init__.py` — 移除 Page 导入，添加 AboutPage
- `frontend/src/App.tsx` — 移除 `/:slug` 路由和 StaticPage 导入
- `frontend/src/types/index.ts` — 移除 Page 接口，添加 AboutPage 接口
- `frontend/src/pages/AboutPage.tsx` — 全部重写，使用新 API
- `frontend/src/pages/admin/AdminPages.tsx` — 全部重写为 About 编辑器
- `frontend/src/pages/admin/AdminSettings.tsx` — 移除 about_bio 相关代码
- `frontend/src/components/admin/AdminLayout.tsx:62-68` — 导航文案改为"关于页"

### 删除
- `backend/app/models/page.py`
- `backend/app/schemas/page.py`
- `backend/app/routers/pages.py`
- `frontend/src/pages/StaticPage.tsx`
- `frontend/src/api/pages.ts`

---

## 任务分解

### Task 1: 后端 — 新建 AboutPage 模型和 Schema

**Files:**
- Create: `backend/app/models/about_page.py`
- Create: `backend/app/schemas/about.py`

- [ ] **Step 1: 创建 ORM 模型**

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class AboutPage(Base):
    __tablename__ = "about_pages"

    id = Column(Integer, primary_key=True, index=True)
    eyebrow = Column(String(100), default="About")
    title = Column(String(255), nullable=False, default="")
    cover_image = Column(String(500), default="")
    content = Column(Text, default="")
    content_type = Column(String(20), default="markdown")
    tech_stack = Column(Text, default="[]")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建 Pydantic Schema**

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AboutPageUpdate(BaseModel):
    eyebrow: Optional[str] = "About"
    title: Optional[str] = None
    cover_image: Optional[str] = ""
    content: Optional[str] = ""
    content_type: Optional[str] = "markdown"
    tech_stack: Optional[str] = "[]"


class AboutPageOut(BaseModel):
    id: int
    eyebrow: str
    title: str
    cover_image: str
    content: str
    content_type: str
    tech_stack: str
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 更新 models/__init__.py**

```python
from app.models.user import User  # noqa: F401
from app.models.article import Article  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.about_page import AboutPage  # noqa: F401
from app.models.article_tag import article_tag  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.asset import Asset  # noqa: F401
```

移除 `from app.models.page import Page` 行。

- [ ] **Step 4: 验证导入**

```bash
cd backend && uv run python -c "from app.models.about_page import AboutPage; from app.schemas.about import AboutPageOut; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: 删除旧 Page 模型**

```bash
rm backend/app/models/page.py backend/app/schemas/page.py
```

- [ ] **Step 6: 提交**

```bash
git add backend/app/models/about_page.py backend/app/schemas/about.py backend/app/models/__init__.py
git rm backend/app/models/page.py backend/app/schemas/page.py
git commit -m "feat: replace generic Page model with dedicated AboutPage model"
```

---

### Task 2: 后端 — 新建 About 路由，移除 Pages 路由

**Files:**
- Create: `backend/app/routers/about.py`
- Modify: `backend/app/main.py`
- Delete: `backend/app/routers/pages.py`

- [ ] **Step 1: 创建 About 路由**

```python
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.about_page import AboutPage
from app.schemas.about import AboutPageUpdate, AboutPageOut

router = APIRouter()


@router.get("", response_model=AboutPageOut)
async def get_about(db: AsyncSession = Depends(get_db)):
    """公开接口：获取关于页数据。"""
    result = await db.execute(select(AboutPage).limit(1))
    about = result.scalar_one_or_none()
    if not about:
        raise HTTPException(status_code=404, detail="About page not configured")
    return about


@router.put("", response_model=AboutPageOut)
async def update_about(
    data: AboutPageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """认证接口：更新关于页（upsert）。"""
    result = await db.execute(select(AboutPage).limit(1))
    about = result.scalar_one_or_none()
    if about:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(about, field, value)
    else:
        defaults = {
            "eyebrow": "About",
            "title": "",
            "cover_image": "",
            "content": "",
            "content_type": "markdown",
            "tech_stack": "[]",
        }
        defaults.update(data.model_dump(exclude_unset=True))
        about = AboutPage(**defaults)
        db.add(about)
    await db.commit()
    await db.refresh(about)
    return about
```

- [ ] **Step 2: 更新 main.py**

修改前：
```python
from app.routers import admin, articles, assets, auth, dashboard, pages, products, settings, tags
```
修改后：
```python
from app.routers import admin, articles, assets, auth, about, dashboard, products, settings, tags
```

修改前：
```python
app.include_router(pages.router, prefix="/api/pages", tags=["pages"])
```
修改后：
```python
app.include_router(about.router, prefix="/api/about", tags=["about"])
```

- [ ] **Step 3: 删除旧 Pages 路由**

```bash
rm backend/app/routers/pages.py
```

- [ ] **Step 4: 验证导入**

```bash
cd backend && uv run python -c "from app.main import app; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: 提交**

```bash
git add backend/app/routers/about.py backend/app/main.py
git rm backend/app/routers/pages.py
git commit -m "feat: add about router with GET/PUT, remove generic pages router"
```

---

### Task 3: 后端 — Alembic 迁移

**Files:**
- Create: `backend/alembic/versions/<timestamp>_add_about_page_table.py`

- [ ] **Step 1: 生成空迁移文件**

```bash
cd backend && uv run alembic revision -m "add about page table"
```

记下生成的文件名。

- [ ] **Step 2: 编写迁移逻辑**

编辑生成的迁移文件，填入以下内容（保持 revision 链不动）：

```python
def upgrade() -> None:
    # 新建 about_pages 表
    op.create_table(
        "about_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("eyebrow", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=20), nullable=True),
        sa.Column("tech_stack", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_about_pages_id"), "about_pages", ["id"], unique=False)

    # 将旧的 about_bio 迁移到 about_pages.content
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT value FROM site_configs WHERE key = 'about_bio'"))
    row = result.fetchone()
    if row:
        op.execute(
            sa.text("INSERT INTO about_pages (eyebrow, title, content, content_type, tech_stack) VALUES ('About', '关于 August''s Lab', :content, 'markdown', '[]')").bindparams(content=row[0])
        )

    # 删除旧表
    op.drop_table("pages")


def downgrade() -> None:
    # 恢复 pages 表
    op.create_table(
        "pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("content_type", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pages_id"), "pages", ["id"], unique=False)
    op.create_index(op.f("ix_pages_slug"), "pages", ["slug"], unique=True)

    # 删除 about_pages 表
    op.drop_index(op.f("ix_about_pages_id"), table_name="about_pages")
    op.drop_table("about_pages")
```

- [ ] **Step 3: 提交**

```bash
git add backend/alembic/versions/*add_about_page_table.py
git commit -m "migration: add about_pages table, migrate about_bio, drop pages table"
```

---

### Task 4: 前端 — 新建 About API 和类型

**Files:**
- Create: `frontend/src/api/about.ts`
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: 更新 types/index.ts**

修改 `frontend/src/types/index.ts`，将 `Page` 接口替换为 `AboutPage`：

修改前（删除这部分）：
```typescript
export interface Page {
  id: number;
  slug: string;
  title: string;
  content: string;
  description: string;
  content_type: string;  // "markdown" | "html"
  status: string;
  created_at: string | null;
  updated_at: string | null;
}
```

新增：
```typescript
export interface AboutPage {
  id: number;
  eyebrow: string;
  title: string;
  cover_image: string;
  content: string;
  content_type: string;  // "markdown" | "html"
  tech_stack: string;  // JSON array string
  updated_at: string | null;
}
```

- [ ] **Step 2: 创建 About API 客户端**

```typescript
import client from './client';
import type { AboutPage } from '../types';

export const getAbout = async () => {
  const { data } = await client.get<AboutPage>('/about');
  return data;
};

export const updateAbout = async (data: Partial<AboutPage>) => {
  const { data: result } = await client.put<AboutPage>('/about', data);
  return result;
};
```

- [ ] **Step 3: 验证类型**

```bash
cd frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: 会有编译错误（因为其他文件还引用了旧的 Page 类型），下一步会修复。

- [ ] **Step 4: 删除旧 Pages API**

```bash
rm frontend/src/api/pages.ts
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/api/about.ts frontend/src/types/index.ts
git rm frontend/src/api/pages.ts
git commit -m "feat: add about API client, replace Page type with AboutPage"
```

---

### Task 5: 前端 — 改造 AboutPage 组件

**Files:**
- Modify: `frontend/src/pages/AboutPage.tsx`

- [ ] **Step 1: 重写 AboutPage**

完全替换 `frontend/src/pages/AboutPage.tsx` 内容：

```tsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getAbout } from '../api/about';
import type { AboutPage } from '../types';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';
import PageIntro from '../components/ui/PageIntro';
import BrandMark from '../components/ui/BrandMark';
import { Skeleton } from '../components/ui/Skeleton';

const sectionVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.38, ease: [0.16, 1, 0.3, 1] as const },
  },
};

export default function AboutPage() {
  const [about, setAbout] = useState<AboutPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAbout()
      .then(setAbout)
      .catch((err) => {
        if (err.response?.status !== 404) {
          setError(err.response?.data?.detail || '加载失败');
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-5">
        <Skeleton className="h-14 w-72" />
        <Skeleton className="h-28" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) {
    return (
      <AnimatedPage className="mx-auto max-w-4xl py-20 text-center">
        <p className="text-text-muted dark:text-text-muted-dark">{error}</p>
      </AnimatedPage>
    );
  }

  if (!about) {
    return (
      <AnimatedPage className="mx-auto max-w-5xl space-y-12">
        <section className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <motion.div variants={sectionVariants} initial="hidden" animate="visible">
            <div className="relative overflow-hidden rounded-lg border border-border bg-paper shadow-md dark:border-border-dark dark:bg-surface-dark">
              <img
                src="/images/brand/about-workbench.webp"
                alt=""
                aria-hidden="true"
                className="aspect-[4/3] w-full object-cover"
              />
              <div className="absolute left-4 top-4 rounded-lg border border-border bg-paper/86 p-3 shadow-sm backdrop-blur-md dark:border-border-dark dark:bg-surface-dark/82">
                <BrandMark compact className="h-14 w-14" />
              </div>
            </div>
          </motion.div>
          <PageIntro eyebrow="About" title="August's Lab" />
        </section>
        <ProfileSections techStack={[]} />
      </AnimatedPage>
    );
  }

  return (
    <AnimatedPage className="mx-auto max-w-4xl space-y-10">
      <PageIntro eyebrow={about.eyebrow} title={about.title} />
      {about.cover_image && (
        <div className="overflow-hidden rounded-lg border border-border bg-paper shadow-sm dark:border-border-dark dark:bg-surface-dark">
          <img
            src={about.cover_image}
            alt=""
            aria-hidden="true"
            className="aspect-[16/9] w-full object-cover"
          />
        </div>
      )}
      {about.content && (
        <section className="paper-panel-strong p-6 sm:p-8">
          <ArticleContent content={about.content} />
        </section>
      )}
      <ProfileSections
        techStack={(() => {
          try {
            return JSON.parse(about.tech_stack) as string[];
          } catch {
            return [];
          }
        })()}
      />
    </AnimatedPage>
  );
}

function ProfileSections({ techStack }: { techStack: string[] }) {
  if (!techStack.length) return null;
  return (
    <div className="grid gap-6">
      <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }} className="paper-panel p-6">
        <p className="section-label mb-4">Stack</p>
        <h2 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">常用技术栈</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {techStack.map((tech) => (
            <span key={tech} className="lab-chip">
              {tech}
            </span>
          ))}
        </div>
      </motion.section>
    </div>
  );
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/pages/AboutPage.tsx
git commit -m "feat: rewrite AboutPage to use new about API, remove fallback logic"
```

---

### Task 6: 前端 — 改造 AdminPages 为 About 专属编辑器

**Files:**
- Modify: `frontend/src/pages/admin/AdminPages.tsx`

- [ ] **Step 1: 创建 TagInput 子组件**

创建 `frontend/src/components/admin/TagInput.tsx`：

```tsx
import { useState } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
}

export default function TagInput({ tags, onChange }: TagInputProps) {
  const [input, setInput] = useState('');

  const add = () => {
    const trimmed = input.trim();
    if (!trimmed || tags.includes(trimmed)) return;
    onChange([...tags, trimmed]);
    setInput('');
  };

  const remove = (index: number) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-2">
        {tags.map((tag, i) => (
          <span key={i} className="inline-flex items-center gap-1 bg-accent-subtle dark:bg-accent-subtle-dark text-accent dark:text-accent px-3 py-1 rounded-full text-sm">
            {tag}
            <button
              type="button"
              onClick={() => remove(i)}
              className="ml-0.5 text-accent/60 hover:text-accent dark:text-accent-dark/60 dark:hover:text-accent-dark"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add(); } }}
          placeholder="输入标签后按回车"
          className="flex-1 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm"
        />
        <button type="button" onClick={add} className="px-4 py-2 bg-accent text-white rounded-lg text-sm hover:bg-accent-hover transition-colors">
          添加
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 重写 AdminPages**

完全替换 `frontend/src/pages/admin/AdminPages.tsx`：

```tsx
import { useState, useEffect, type FormEvent } from 'react';
import { motion } from 'framer-motion';
import { getAbout, updateAbout } from '../../api/about';
import type { AboutPage } from '../../types';
import ArticleContent from '../../components/articles/ArticleContent';
import TagInput from '../../components/admin/TagInput';

export default function AdminPages() {
  const [about, setAbout] = useState<AboutPage | null>(null);
  const [eyebrow, setEyebrow] = useState('About');
  const [title, setTitle] = useState('');
  const [coverImage, setCoverImage] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('markdown');
  const [techStack, setTechStack] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [preview, setPreview] = useState(false);

  useEffect(() => {
    loadAbout();
  }, []);

  const loadAbout = async () => {
    try {
      const data = await getAbout();
      setAbout(data);
      setEyebrow(data.eyebrow || 'About');
      setTitle(data.title);
      setCoverImage(data.cover_image);
      setContent(data.content);
      setContentType(data.content_type || 'markdown');
      try {
        setTechStack(JSON.parse(data.tech_stack) as string[]);
      } catch {
        setTechStack([]);
      }
    } catch {
      // About page doesn't exist yet — show empty form
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateAbout({
        eyebrow,
        title,
        cover_image: coverImage,
        content,
        content_type: contentType,
        tech_stack: JSON.stringify(techStack),
      });
      setSuccess('已保存');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse h-64 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">关于页</h1>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-sm">
          {error}
        </motion.div>
      )}
      {success && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-green-600 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg text-sm">
          {success}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Eyebrow + Title */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Eyebrow 标签</label>
              <input
                type="text"
                value={eyebrow}
                onChange={(e) => setEyebrow(e.target.value)}
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">主标题</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                placeholder="关于 August's Lab"
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
          </div>

          {/* Cover Image */}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">封面图片路径</label>
            <input
              type="text"
              value={coverImage}
              onChange={(e) => setCoverImage(e.target.value)}
              placeholder="/images/brand/about-workbench.webp"
              className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
            />
          </div>

          {/* Content type selector + editor */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">正文内容</label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
                className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-2 py-1 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-xs focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              >
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
            </div>

            {/* Toggle */}
            {contentType === 'markdown' && (
              <div className="mb-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => setPreview(false)}
                  className={`px-3 py-1 text-xs rounded-md transition-colors ${!preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}
                >
                  编辑
                </button>
                <button
                  type="button"
                  onClick={() => setPreview(true)}
                  className={`px-3 py-1 text-xs rounded-md transition-colors ${preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}
                >
                  预览
                </button>
              </div>
            )}

            {contentType === 'markdown' && preview ? (
              <div className="border border-zinc-300 dark:border-zinc-700 rounded-lg p-4 bg-white dark:bg-zinc-900 min-h-[160px] prose dark:prose-invert max-w-none">
                <ArticleContent content={content} />
              </div>
            ) : (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={10}
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all font-mono text-sm"
                placeholder="输入 Markdown 内容..."
              />
            )}
          </div>

          {/* Tech Stack */}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">技术栈标签</label>
            <TagInput tags={techStack} onChange={setTechStack} />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <motion.button
              type="submit"
              disabled={saving}
              whileTap={{ scale: saving ? 1 : 0.98 }}
              className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
            >
              {saving ? '保存中...' : '保存'}
            </motion.button>
            <a
              href="/about"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-500 dark:text-zinc-400 hover:text-accent dark:hover:text-accent-dark transition-colors"
            >
              前台预览 →
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/admin/AdminPages.tsx frontend/src/components/admin/TagInput.tsx
git commit -m "feat: rewrite AdminPages as dedicated About editor with markdown preview and tag input"
```

---

### Task 7: 前端 — 清理 StaticPage、AdminSettings、App.tsx、AdminLayout

**Files:**
- Delete: `frontend/src/pages/StaticPage.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/pages/admin/AdminSettings.tsx`
- Modify: `frontend/src/components/admin/AdminLayout.tsx`

- [ ] **Step 1: 删除 StaticPage**

```bash
rm frontend/src/pages/StaticPage.tsx
```

- [ ] **Step 2: 更新 App.tsx**

修改 `frontend/src/App.tsx`：

删除导入：
```typescript
import StaticPage from './pages/StaticPage';
```

删除路由：
```tsx
<Route path=":slug" element={<StaticPage />} />
```

最终 App.tsx 应为：

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import AdminLayout from './components/admin/AdminLayout';
import HomePage from './pages/HomePage';
import BlogPage from './pages/BlogPage';
import ProductsPage from './pages/ProductsPage';
import ProductPage from './pages/ProductPage';
import AboutPage from './pages/AboutPage';
import ArticlePage from './pages/ArticlePage';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminArticles from './pages/admin/AdminArticles';
import AdminProducts from './pages/admin/AdminProducts';
import AdminPages from './pages/admin/AdminPages';
import AdminSettings from './pages/admin/AdminSettings';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="blog" element={<BlogPage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="products/:slug" element={<ProductPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="articles/:slug" element={<ArticlePage />} />
            <Route path="login" element={<LoginPage />} />
          </Route>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="articles" element={<AdminArticles />} />
            <Route path="products" element={<AdminProducts />} />
            <Route path="pages" element={<AdminPages />} />
            <Route path="settings" element={<AdminSettings />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

- [ ] **Step 3: 清理 AdminSettings**

修改 `frontend/src/pages/admin/AdminSettings.tsx`，移除所有 about_bio 相关代码：

```tsx
export default function AdminSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">站点设置</h1>
      <div className="text-zinc-500 dark:text-zinc-400 text-sm">
        关于页配置已迁移至 <a href="/admin/pages" className="text-accent hover:underline">页面管理</a>。
      </div>
    </div>
  );
}
```

- [ ] **Step 4: 更新 AdminLayout 导航文案**

修改 `frontend/src/components/admin/AdminLayout.tsx` 第 66 行：

```typescript
{ to: '/admin/pages', label: '关于页', icon: DocumentIcon },
```

将"页面管理"改为"关于页"。

- [ ] **Step 5: 前端构建验证**

```bash
cd frontend && npm run build
```

Expected: 构建成功，无类型错误。

- [ ] **Step 6: 提交**

```bash
git rm frontend/src/pages/StaticPage.tsx
git add frontend/src/App.tsx frontend/src/pages/admin/AdminSettings.tsx frontend/src/components/admin/AdminLayout.tsx
git commit -m "feat: remove StaticPage and pages route, update admin nav and settings"
```

---

### Task 8: 后端测试 — 验证 About API

**Files:**
- Create: `backend/tests/test_about.py`

- [ ] **Step 1: 编写测试**

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_about_not_configured(client: AsyncClient):
    """未配置时返回 404。"""
    resp = await client.get("/about")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_about(auth_client: AsyncClient, client: AsyncClient):
    """创建后能获取。"""
    resp = await auth_client.put("/about", json={
        "eyebrow": "About",
        "title": "关于我们",
        "cover_image": "/images/test.webp",
        "content": "# Hello",
        "content_type": "markdown",
        "tech_stack": '["Python","React"]',
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "关于我们"
    assert data["tech_stack"] == '["Python","React"]'

    # 公开接口获取
    resp = await client.get("/about")
    assert resp.status_code == 200
    assert resp.json()["title"] == "关于我们"


@pytest.mark.asyncio
async def test_update_about(auth_client: AsyncClient):
    """更新已存在的记录。"""
    # 先创建
    await auth_client.put("/about", json={"title": "初始"})
    # 再更新
    resp = await auth_client.put("/about", json={"title": "新标题"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "新标题"


@pytest.mark.asyncio
async def test_update_about_requires_auth(client: AsyncClient):
    """未认证返回 401。"""
    resp = await client.put("/about", json={"title": "test"})
    assert resp.status_code == 401
```

- [ ] **Step 2: 运行后端测试**

```bash
cd backend && uv run pytest tests/test_about.py -v
```

Expected: 全部 4 个测试通过。

- [ ] **Step 3: 提交**

```bash
git add backend/tests/test_about.py
git commit -m "test: add about API tests"
```

---

### Task 9: 最终验证 — 运行完整 CI 检查

- [ ] **Step 1: 后端导入验证**

```bash
cd backend && uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 2: 后端测试**

```bash
cd backend && uv run pytest tests/ -v
```

- [ ] **Step 3: 前端类型检查 + 构建**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 前端 lint**

```bash
cd frontend && npm run lint
```

以上全部通过则完成。如有失败，按错误信息修复后重新提交。
