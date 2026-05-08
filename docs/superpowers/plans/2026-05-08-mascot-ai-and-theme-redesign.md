# 看板娘 AI 对话 + 主题配色重构 · 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 GlassPanel 为深度叠层效果，接入 DeepSeek API 为看板娘增加 AI 对话功能，并构建后台管理页面。

**Architecture:** 前端 Canvas 动画引擎保持不变，新增 ChatBubble 对话气泡组件；后端新增 mascot router 代理 DeepSeek API 调用；数据库新增 mascot_settings 单行配置表。

**Tech Stack:** FastAPI + SQLAlchemy + OpenAI SDK (DeepSeek 兼容) / React + TypeScript + Tailwind v4 + Framer Motion

---

## 文件结构总览

```
backend/
├── app/
│   ├── models/mascot_settings.py      ← 创建
│   ├── schemas/mascot.py              ← 创建
│   ├── routers/mascot.py              ← 创建
│   ├── models/__init__.py             ← 修改 (导入新模型)
│   └── main.py                        ← 修改 (注册新路由)
├── alembic/versions/xxxx_mascot_settings.py ← 创建 (migration)
└── requirements.txt                   ← 修改 (添加 openai)

frontend/
├── src/
│   ├── api/mascot.ts                  ← 创建
│   ├── components/mascot/
│   │   ├── MascotPet.tsx              ← 修改 (集成 ChatBubble，远程 settings)
│   │   └── ChatBubble.tsx             ← 创建
│   ├── pages/admin/AdminMascot.tsx    ← 创建
│   ├── components/admin/AdminLayout.tsx ← 修改 (添加导航项)
│   ├── components/ui/GlassPanel.tsx   ← 修改 (引用 .glass-panel)
│   ├── types/index.ts                 ← 修改 (新增 MascotSettings)
│   ├── App.tsx                        ← 修改 (添加路由)
│   └── index.css                      ← 修改 (新增 .glass-panel)
```

---

### Task 1: 主题配色 — 新增 `.glass-panel` component class

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/components/ui/GlassPanel.tsx`

- [ ] **Step 1: 在 index.css 的 @layer components 末尾添加 .glass-panel**

在 `frontend/src/index.css` 的 `@layer components { ... }` 末尾（`}` 闭合前）添加：

```css
  .glass-panel {
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.7) 0%, rgba(255, 255, 255, 0.35) 100%);
    backdrop-filter: blur(20px);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8), 0 8px 32px rgba(15, 23, 42, 0.04);
    overflow: hidden;
  }

  .dark .glass-panel {
    border-color: rgba(255, 255, 255, 0.06);
    background: linear-gradient(180deg, rgba(23, 31, 51, 0.7) 0%, rgba(17, 24, 39, 0.4) 100%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 8px 32px rgba(0, 0, 0, 0.3);
  }
```

- [ ] **Step 2: 更新 GlassPanel.tsx 使用新的 class**

将 `frontend/src/components/ui/GlassPanel.tsx` 改为：

```tsx
interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  accentLine?: boolean;
}

export default function GlassPanel({ children, className = '', accentLine = false }: GlassPanelProps) {
  return (
    <div className={`glass-panel ${className}`}>
      {accentLine && (
        <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-accent-start to-accent-mid" />
      )}
      {children}
    </div>
  );
}
```

- [ ] **Step 3: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/index.css frontend/src/components/ui/GlassPanel.tsx
git commit -m "refactor: redesign GlassPanel with depth-layer gradient effect"
```

---

### Task 2: 主题配色 — 修复其他组件硬编码颜色

**Files:**
- Modify: `frontend/src/pages/ProductPage.tsx`
- Modify: `frontend/src/pages/ProductsPage.tsx`
- Modify: `frontend/src/components/articles/ArticleEditor.tsx`

- [ ] **Step 1: 修复 ProductPage.tsx**

在 `frontend/src/pages/ProductPage.tsx` 中：

行 56 区域，`bg-white/80` 改为 `bg-white/80 dark:bg-surface-dark/80`：
```tsx
// 修改前: bg-white/80
// 修改后: bg-white/80 dark:bg-surface-dark/80
className="pointer-events-auto flex items-center gap-2 rounded-xl border border-border/60 bg-white/80 px-3 py-2 shadow-lg backdrop-blur-md dark:border-border-dark/60 dark:bg-surface-dark/80"
```

行 99 区域，`bg-white/95` 改为 `bg-white/95 dark:bg-surface-dark/95`：
```tsx
// 修改前: bg-white/95
// 修改后: bg-white/95 dark:bg-surface-dark/95
className="... bg-white/95 ... dark:bg-surface-dark/95"
```

行 42 区域，`bg-white` 改为 `bg-white dark:bg-surface-dark`：
```tsx
// 修改前: bg-white
// 修改后: bg-white dark:bg-surface-dark
className="h-full w-full border-0 bg-white dark:bg-surface-dark"
```

- [ ] **Step 2: 修复 ProductsPage.tsx**

在 `frontend/src/pages/ProductsPage.tsx` 行 77 区域，`group-hover:bg-white/70` 已有 dark variant 保留不变，只需确认兼容性（无需改动）。

- [ ] **Step 3: 修复 ArticleEditor.tsx**

在 `frontend/src/components/articles/ArticleEditor.tsx` 行 51 区域：
```tsx
// 修改前: dark:bg-zinc-900
// 修改后: dark:bg-surface-dark
className="... dark:bg-surface-dark dark:text-zinc-100"
```

- [ ] **Step 4: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/pages/ProductPage.tsx frontend/src/components/articles/ArticleEditor.tsx
git commit -m "fix: replace hardcoded light-mode colors with design tokens"
```

---

### Task 3: 后端 — MascotSettings 模型

**Files:**
- Create: `backend/app/models/mascot_settings.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建模型**

```python
# backend/app/models/mascot_settings.py
from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from app.database import Base


class MascotSettings(Base):
    __tablename__ = "mascot_settings"

    id = Column(Integer, primary_key=True, index=True, default=1)
    persona = Column(Text, nullable=False, default=(
        "你是刻晴，August's Lab 技术博客的看板娘小助手。\n"
        "性格：活泼元气、略傲娇、喜欢用颜文字和拟声词。\n"
        "说话风格：轻松可爱、偶尔吐槽，对技术保持好奇心。\n"
        "知识范围：前端开发、React、Python、开源技术。\n"
        "规则：回复简洁（1-3 句），不要长篇大论，保持角色感。"
    ))
    api_key = Column(String(255), nullable=False, default="")
    api_base_url = Column(String(500), nullable=False, default="https://api.deepseek.com")
    model = Column(String(100), nullable=False, default="deepseek-chat")
    temperature = Column(Float, nullable=False, default=0.8)
    max_tokens = Column(Integer, nullable=False, default=512)
    enabled = Column(Boolean, nullable=False, default=False)
    mascot_visible = Column(Boolean, nullable=False, default=True)
    mascot_scale = Column(Float, nullable=False, default=1.2)
    mascot_position_x = Column(Integer, nullable=True)
    mascot_position_y = Column(Integer, nullable=True)
    show_on_mobile = Column(Boolean, nullable=False, default=False)
    greeting_enabled = Column(Boolean, nullable=False, default=True)
    greeting_delay_seconds = Column(Integer, nullable=False, default=8)
    random_action_interval = Column(Integer, nullable=False, default=15)
    context_aware = Column(Boolean, nullable=False, default=False)
    drag_enabled = Column(Boolean, nullable=False, default=True)
```

- [ ] **Step 2: 在 __init__.py 中注册模型**

在 `backend/app/models/__init__.py` 末尾添加：
```python
from app.models.mascot_settings import MascotSettings  # noqa: F401
```

- [ ] **Step 3: 生成数据库迁移**

```bash
cd backend
uv run alembic revision --autogenerate -m "add mascot_settings table"
uv run alembic upgrade head
```

- [ ] **Step 4: 验证迁移**

```bash
cd backend && uv run python -c "from app.models.mascot_settings import MascotSettings; print('OK')"
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/models/mascot_settings.py backend/app/models/__init__.py backend/alembic/versions/
git commit -m "feat: add mascot_settings model and migration"
```

---

### Task 4: 后端 — Schema

**Files:**
- Create: `backend/app/schemas/mascot.py`

- [ ] **Step 1: 创建 schema 文件**

```python
# backend/app/schemas/mascot.py
from typing import Optional

from pydantic import BaseModel, Field


class MascotSettingsUpdate(BaseModel):
    persona: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    enabled: Optional[bool] = None
    mascot_visible: Optional[bool] = None
    mascot_scale: Optional[float] = None
    mascot_position_x: Optional[int] = None
    mascot_position_y: Optional[int] = None
    show_on_mobile: Optional[bool] = None
    greeting_enabled: Optional[bool] = None
    greeting_delay_seconds: Optional[int] = None
    random_action_interval: Optional[int] = None
    context_aware: Optional[bool] = None
    drag_enabled: Optional[bool] = None


class MascotSettingsPublic(BaseModel):
    """Public settings — api_key excluded"""
    persona: str
    api_base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 0.8
    max_tokens: int = 512
    enabled: bool = False
    mascot_visible: bool = True
    mascot_scale: float = 1.2
    mascot_position_x: Optional[int] = None
    mascot_position_y: Optional[int] = None
    show_on_mobile: bool = False
    greeting_enabled: bool = True
    greeting_delay_seconds: int = 8
    random_action_interval: int = 15
    context_aware: bool = False
    drag_enabled: bool = True

    model_config = {"from_attributes": True}


class MascotSettingsOut(MascotSettingsPublic):
    """Admin output — includes api_key"""
    id: int
    api_key: str = ""


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None  # page title or article summary


class ChatResponse(BaseModel):
    reply: str
```

- [ ] **Step 2: 验证导入**

```bash
cd backend && uv run python -c "from app.schemas.mascot import MascotSettingsUpdate, MascotSettingsPublic, ChatRequest; print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/schemas/mascot.py
git commit -m "feat: add mascot settings and chat schemas"
```

---

### Task 5: 后端 — 安装 openai 依赖

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 添加 openai 包**

```bash
cd backend && uv pip install openai
```

在 `backend/requirements.txt` 末尾添加：
```
openai>=1.0.0
```

- [ ] **Step 2: 验证安装**

```bash
cd backend && uv run python -c "from openai import OpenAI; print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add backend/requirements.txt
git commit -m "chore: add openai SDK for DeepSeek API integration"
```

---

### Task 6: 后端 — Mascot Router

**Files:**
- Create: `backend/app/routers/mascot.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 router**

```python
# backend/app/routers/mascot.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

from app.database import get_db
from app.dependencies import get_current_user
from app.models.mascot_settings import MascotSettings
from app.schemas.mascot import (
    ChatRequest,
    ChatResponse,
    MascotSettingsPublic,
    MascotSettingsUpdate,
    MascotSettingsOut,
)

router = APIRouter()


async def _get_settings(db: AsyncSession) -> MascotSettings:
    result = await db.execute(select(MascotSettings).where(MascotSettings.id == 1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = MascotSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("/settings", response_model=MascotSettingsPublic)
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    return settings


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    if not settings.enabled or not settings.api_key:
        raise HTTPException(status_code=503, detail="AI chat is not enabled")

    system_prompt = settings.persona
    if settings.context_aware and req.context:
        system_prompt += f"\n当前用户正在浏览的页面内容：{req.context}"

    client = OpenAI(
        base_url=settings.api_base_url,
        api_key=settings.api_key,
    )

    try:
        response = client.chat.completions.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message},
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            stream=False,
        )
        reply = response.choices[0].message.content or ""
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI API error: {str(e)}")


# -- Admin endpoints --

@router.get("/admin/settings", response_model=MascotSettingsOut)
async def get_admin_settings(
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return await _get_settings(db)


@router.put("/admin/settings", response_model=MascotSettingsOut)
async def update_admin_settings(
    data: MascotSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    settings = await _get_settings(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings
```

- [ ] **Step 2: 在 main.py 注册路由**

在 `backend/app/main.py` 中：

导入行添加：
```python
from app.routers import mascot
```

在 `include_router` 段落添加：
```python
app.include_router(mascot.router, prefix="/api/mascot", tags=["mascot"])
```

- [ ] **Step 3: 验证后端启动**

```bash
cd backend && uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/routers/mascot.py backend/app/main.py
git commit -m "feat: add mascot chat and admin settings API endpoints"
```

---

### Task 7: 前端 — 类型和 API 模块

**Files:**
- Modify: `frontend/src/types/index.ts`
- Create: `frontend/src/api/mascot.ts`

- [ ] **Step 1: 在 types/index.ts 添加 MascotSettings 接口**

```ts
// 看板娘设置（公开字段）
export interface MascotSettings {
  persona: string;
  api_base_url: string;
  model: string;
  temperature: number;
  max_tokens: number;
  enabled: boolean;
  mascot_visible: boolean;
  mascot_scale: number;
  mascot_position_x: number | null;
  mascot_position_y: number | null;
  show_on_mobile: boolean;
  greeting_enabled: boolean;
  greeting_delay_seconds: number;
  random_action_interval: number;
  context_aware: boolean;
  drag_enabled: boolean;
}

// 管理后台完整设置（含 api_key）
export interface MascotSettingsAdmin extends MascotSettings {
  id: number;
  api_key: string;
}
```

- [ ] **Step 2: 创建 src/api/mascot.ts**

```ts
import client from './client';
import type { MascotSettings, MascotSettingsAdmin } from '../types';

export const getMascotSettings = async (): Promise<MascotSettings> => {
  const { data } = await client.get<MascotSettings>('/mascot/settings');
  return data;
};

export const sendMascotChat = async (message: string, context?: string) => {
  const { data } = await client.post<{ reply: string }>('/mascot/chat', {
    message,
    context,
  });
  return data;
};

export const getAdminMascotSettings = async (): Promise<MascotSettingsAdmin> => {
  const { data } = await client.get<MascotSettingsAdmin>('/mascot/admin/settings');
  return data;
};

export const updateAdminMascotSettings = async (
  settings: Partial<MascotSettingsAdmin>
): Promise<MascotSettingsAdmin> => {
  const { data } = await client.put<MascotSettingsAdmin>('/mascot/admin/settings', settings);
  return data;
};
```

- [ ] **Step 3: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/types/index.ts frontend/src/api/mascot.ts
git commit -m "feat: add mascot types and API client module"
```

---

### Task 8: 前端 — ChatBubble 组件

**Files:**
- Create: `frontend/src/components/mascot/ChatBubble.tsx`

- [ ] **Step 1: 创建 ChatBubble 组件**

```tsx
// frontend/src/components/mascot/ChatBubble.tsx
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendMascotChat } from '../../api/mascot';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

interface ChatBubbleProps {
  visible: boolean;
  persona?: string;
  greetingEnabled?: boolean;
  greetingDelaySeconds?: number;
  onClose: () => void;
}

export default function ChatBubble({
  visible,
  greetingEnabled = true,
  greetingDelaySeconds = 8,
  onClose,
}: ChatBubbleProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [greeted, setGreeted] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto greeting
  useEffect(() => {
    if (!visible || !greetingEnabled || greeted) return;
    const timer = setTimeout(async () => {
      try {
        const res = await sendMascotChat('你好呀~');
        setMessages([{ role: 'assistant', content: res.reply }]);
      } catch {
        setMessages([{ role: 'assistant', content: '你好呀！欢迎来到 August\'s Lab~ ⚡' }]);
      }
      setGreeted(true);
    }, greetingDelaySeconds * 1000);
    return () => clearTimeout(timer);
  }, [visible, greetingEnabled, greeted, greetingDelaySeconds]);

  // Focus input when visible
  useEffect(() => {
    if (visible) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [visible]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);

    try {
      const context = document.title;
      const res = await sendMascotChat(text, context);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: '呜...脑子有点乱，待会再聊吧 (´•ω•`)' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.96 }}
      transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
      className="absolute bottom-full mb-3 right-0 w-72 rounded-xl border border-white/10 bg-surface-dark/90 backdrop-blur-xl shadow-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2.5">
        <span className="text-xs font-bold text-text-muted-dark">与刻晴聊天</span>
        <button
          onClick={onClose}
          className="flex h-5 w-5 items-center justify-center rounded-full text-text-muted-dark hover:bg-white/10 hover:text-text-primary-dark transition-colors text-xs"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="max-h-56 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && !loading && (
          <p className="text-xs text-text-muted-dark text-center py-4">
            输入消息开始聊天~
          </p>
        )}
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className={`text-xs leading-relaxed ${
                msg.role === 'assistant'
                  ? 'text-text-primary-dark'
                  : 'text-accent-mid text-right'
              }`}
            >
              {msg.content}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <div className="text-xs text-text-muted-dark animate-pulse">
            刻晴正在思考...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-white/[0.06] px-3 py-2.5 flex items-center gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="说点什么..."
          disabled={loading}
          className="flex-1 min-w-0 rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-1.5 text-xs text-text-primary-dark placeholder:text-text-muted-dark focus:outline-none focus:border-accent/40 transition-colors"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-bold text-white hover:bg-accent-hover disabled:opacity-40 transition-all"
        >
          发送
        </button>
      </div>
    </motion.div>
  );
}
```

- [ ] **Step 2: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/mascot/ChatBubble.tsx
git commit -m "feat: add mascot chat bubble component with auto-greeting"
```

---

### Task 9: 前端 — MascotPet 改造（加载远程 settings，集成 ChatBubble）

**Files:**
- Modify: `frontend/src/components/mascot/MascotPet.tsx`

- [ ] **Step 1: 更新 MascotPet.tsx 从 API 加载配置**

将当前的本地常量 `DEFAULT_SCALE`、`MARGIN` 等改为从 `getMascotSettings()` API 加载。

```tsx
// frontend/src/components/mascot/MascotPet.tsx
import { useEffect, useRef, useState, useCallback } from 'react';
import { MascotEngine } from './mascotEngine';
import type { AnimationName } from './mascotEngine';
import ChatBubble from './ChatBubble';
import { getMascotSettings } from '../../api/mascot';
import type { MascotSettings } from '../../types';

const CELL_W = 192;
const CELL_H = 208;
const MARGIN = 20;
const DRAG_THRESHOLD = 5;
const CLOSE_BUTTON_SIZE = 20;
const INTERACTION_COOLDOWN = 3000;

// ... pickWeighted, INTERACT_ANIMS, RANDOM_ANIMS 保持不变 ...

export default function MascotPet() {
  const [settings, setSettings] = useState<MascotSettings | null>(null);
  const [dismissed, setDismissed] = useState(() => sessionStorage.getItem('mascot-dismissed') === 'true');
  const defaultX = window.innerWidth - CELL_W * 1.2 - MARGIN;
  const defaultY = window.innerHeight - CELL_H * 1.2 - MARGIN;
  const [position, setPosition] = useState({ x: defaultX, y: defaultY });
  const [isMobile, setIsMobile] = useState(() => window.matchMedia('(max-width: 767px)').matches);
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [chatVisible, setChatVisible] = useState(false);

  // ... refs: containerRef, canvasRef, engineRef, dragOriginRef, etc. ...

  // Load remote settings
  useEffect(() => {
    getMascotSettings()
      .then((s) => {
        setSettings(s);
        if (s.mascot_position_x != null && s.mascot_position_y != null) {
          setPosition({ x: s.mascot_position_x, y: s.mascot_position_y });
        }
      })
      .catch(() => {
        // Fallback: mascot works with defaults even without API
      });
  }, []);

  const scale = settings?.mascot_scale ?? 1.2;
  const visible = settings?.mascot_visible ?? true;
  const showOnMobile = settings?.show_on_mobile ?? false;
  const dragEnabled = settings?.drag_enabled ?? true;
  const randomInterval = settings?.random_action_interval ?? 15;
  const greetingEnabled = settings?.greeting_enabled ?? true;
  const greetingDelay = settings?.greeting_delay_seconds ?? 8;

  // ... scheduleRandomRef, engine init (adapted for dynamic interval) ...

  // Engine init effect — depends on settings being loaded
  useEffect(() => {
    if (dismissed || isMobile || !visible) return;
    // ... same engine creation, sprite loading ...
  }, [dismissed, isMobile, visible, scale]);

  // Click -> toggle chat instead of random animation
  const handleClick = useCallback(() => {
    lastInteractionRef.current = performance.now();
    if (settings?.enabled) {
      setChatVisible((prev) => !prev);
    } else {
      // Fallback: play wave/jump animation when AI is disabled
      const anim = INTERACT_ANIMS[Math.floor(Math.random() * INTERACT_ANIMS.length)];
      engineRef.current?.playAnimation(anim);
    }
  }, [settings?.enabled]);

  // Pointer down handler — respect dragEnabled
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (!dragEnabled) return;
    // ... same drag logic ...
  }, [position, dragEnabled]);

  // Dismiss handler — keep sessionStorage
  // ... unchanged ...

  if (dismissed || (isMobile && !showOnMobile) || !visible) return null;

  const cssW = CELL_W * scale;
  const cssH = CELL_H * scale;

  return (
    <div
      ref={containerRef}
      className="fixed z-50 select-none"
      style={{
        left: position.x,
        top: position.y,
        width: cssW,
        height: cssH,
        cursor: dragEnabled ? (isDragging ? 'grabbing' : 'grab') : 'pointer',
      }}
      onPointerDown={dragEnabled ? handlePointerDown : undefined}
      onClick={dragEnabled ? undefined : handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={CELL_W}
          height={CELL_H}
          style={{ width: cssW, height: cssH }}
          className="pointer-events-none block"
        />

        {/* Chat bubble positioned above the mascot */}
        <ChatBubble
          visible={chatVisible}
          greetingEnabled={greetingEnabled}
          greetingDelaySeconds={greetingDelay}
          onClose={() => setChatVisible(false)}
        />

        {/* Close button */}
        <button
          className="absolute rounded-full bg-black/50 text-white text-xs leading-none
                     flex items-center justify-center hover:bg-black/70 transition-opacity"
          style={{
            top: -6,
            right: -6,
            width: CLOSE_BUTTON_SIZE,
            height: CLOSE_BUTTON_SIZE,
            opacity: isHovered ? 1 : 0,
          }}
          onClick={handleDismiss}
          aria-label="关闭看板娘"
        >
          &times;
        </button>
      </div>
    </div>
  );
}
```

**关键改动点：**
1. 导入 `getMascotSettings`、`ChatBubble`、`MascotSettings` 类型
2. 新增 `settings` state，`useEffect` 加载远程配置
3. `scale`、`visible`、`dragEnabled` 等从 settings 取值，带 fallback
4. 点击行为：AI 开启时切换对话面板，关闭时播放动画（原有逻辑）
5. 新增 `chatVisible` state 控制 ChatBubble 显隐
6. 拖拽逻辑仅在 `dragEnabled` 时启用

- [ ] **Step 2: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/mascot/MascotPet.tsx
git commit -m "feat: integrate remote settings and chat bubble into MascotPet"
```

---

### Task 10: 前端 — AdminMascot 管理页面

**Files:**
- Create: `frontend/src/pages/admin/AdminMascot.tsx`

- [ ] **Step 1: 创建管理页面**

```tsx
// frontend/src/pages/admin/AdminMascot.tsx
import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { getAdminMascotSettings, updateAdminMascotSettings } from '../../api/mascot';
import type { MascotSettingsAdmin } from '../../types';
import {
  AdminPageHeader,
  AdminPanel,
  AdminErrorBanner,
} from '../../components/admin/AdminPrimitives';

function getErrorMessage(e: unknown, fallback: string): string {
  if (e && typeof e === 'object' && 'response' in e) {
    const resp = (e as { response?: { data?: { detail?: string } } }).response;
    return resp?.data?.detail || fallback;
  }
  return fallback;
}

const emptyForm: MascotSettingsAdmin = {
  id: 1,
  persona: '',
  api_key: '',
  api_base_url: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  temperature: 0.8,
  max_tokens: 512,
  enabled: false,
  mascot_visible: true,
  mascot_scale: 1.2,
  mascot_position_x: null,
  mascot_position_y: null,
  show_on_mobile: false,
  greeting_enabled: true,
  greeting_delay_seconds: 8,
  random_action_interval: 15,
  context_aware: false,
  drag_enabled: true,
};

export default function AdminMascot() {
  const [form, setForm] = useState<MascotSettingsAdmin>(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAdminMascotSettings();
      setForm(data);
    } catch (e) {
      setError(getErrorMessage(e, '加载配置失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void loadSettings(); }, [loadSettings]);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      await updateAdminMascotSettings(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      setError(getErrorMessage(e, '保存失败'));
    } finally {
      setSaving(false);
    }
  };

  const updateField = <K extends keyof MascotSettingsAdmin>(key: K, value: MascotSettingsAdmin[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-text-muted dark:text-text-muted-dark">加载中...</div>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <AdminPageHeader
        title="看板娘设置"
        description="配置刻晴看板娘的 AI 对话、外观和行为"
      />

      {error && <AdminErrorBanner message={error} />}
      {saved && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="rounded-lg border border-success/60 bg-success-subtle px-4 py-3 text-sm font-semibold text-success dark:bg-success-subtle-dark">
          设置已保存
        </motion.div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        {/* Left: form sections */}
        <div className="space-y-6">
          {/* Persona */}
          <AdminPanel>
            <h3 className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-3">角色设定</h3>
            <textarea
              value={form.persona}
              onChange={(e) => updateField('persona', e.target.value)}
              rows={6}
              className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-text-primary resize-y dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark"
              placeholder="System prompt..."
            />
          </AdminPanel>

          {/* API Config */}
          <AdminPanel>
            <h3 className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-3">API 配置</h3>
            <div className="grid gap-3">
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">API Key</label>
                <input type="password" value={form.api_key} onChange={(e) => updateField('api_key', e.target.value)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark"
                  placeholder="sk-..." />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">Base URL</label>
                <input type="text" value={form.api_base_url} onChange={(e) => updateField('api_base_url', e.target.value)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">模型</label>
                  <input type="text" value={form.model} onChange={(e) => updateField('model', e.target.value)}
                    className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">Temperature</label>
                  <input type="number" step="0.1" min="0" max="2" value={form.temperature} onChange={(e) => updateField('temperature', parseFloat(e.target.value) || 0)}
                    className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">Max Tokens</label>
                <input type="number" min="64" max="4096" value={form.max_tokens} onChange={(e) => updateField('max_tokens', parseInt(e.target.value) || 512)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
              </div>
            </div>
          </AdminPanel>

          {/* Behavior */}
          <AdminPanel>
            <h3 className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-3">行为设置</h3>
            <div className="grid gap-3">
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">自动问候</span>
                <input type="checkbox" checked={form.greeting_enabled} onChange={(e) => updateField('greeting_enabled', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">问候延迟 (秒)</label>
                <input type="number" min="1" max="60" value={form.greeting_delay_seconds} onChange={(e) => updateField('greeting_delay_seconds', parseInt(e.target.value) || 8)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">随机动作间隔 (秒)</label>
                <input type="number" min="5" max="120" value={form.random_action_interval} onChange={(e) => updateField('random_action_interval', parseInt(e.target.value) || 15)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
              </div>
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">上下文感知</span>
                <input type="checkbox" checked={form.context_aware} onChange={(e) => updateField('context_aware', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">允许拖拽</span>
                <input type="checkbox" checked={form.drag_enabled} onChange={(e) => updateField('drag_enabled', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
            </div>
          </AdminPanel>
        </div>

        {/* Right: toggles + preview */}
        <div className="space-y-6">
          <AdminPanel>
            <h3 className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-3">开关控制</h3>
            <div className="space-y-3">
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">启用 AI 对话</span>
                <input type="checkbox" checked={form.enabled} onChange={(e) => updateField('enabled', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">显示看板娘</span>
                <input type="checkbox" checked={form.mascot_visible} onChange={(e) => updateField('mascot_visible', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
              <label className="flex items-center justify-between">
                <span className="text-sm text-text-secondary dark:text-text-secondary-dark">移动端显示</span>
                <input type="checkbox" checked={form.show_on_mobile} onChange={(e) => updateField('show_on_mobile', e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent" />
              </label>
            </div>
          </AdminPanel>

          <AdminPanel>
            <h3 className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-3">外观</h3>
            <div className="grid gap-3">
              <div>
                <label className="block text-xs font-semibold text-text-muted dark:text-text-muted-dark mb-1">缩放比例</label>
                <input type="number" step="0.1" min="0.5" max="3" value={form.mascot_scale} onChange={(e) => updateField('mascot_scale', parseFloat(e.target.value) || 1.2)}
                  className="focus-ring w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary dark:border-border-dark dark:bg-surface-dark dark:text-text-primary-dark" />
              </div>
            </div>
          </AdminPanel>

          {/* Save */}
          <button onClick={handleSave} disabled={saving} className="lab-button w-full">
            {saving ? '保存中...' : '保存设置'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 构建验证**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/pages/admin/AdminMascot.tsx
git commit -m "feat: add admin mascot settings management page"
```

---

### Task 11: 前端 — 路由和导航集成

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/admin/AdminLayout.tsx`

- [ ] **Step 1: 在 App.tsx 添加路由**

在 `frontend/src/App.tsx` 中：

导入行添加：
```tsx
import AdminMascot from './pages/admin/AdminMascot';
```

在 `/admin` 路由组内添加：
```tsx
<Route path="mascot" element={<AdminMascot />} />
```

- [ ] **Step 2: 在 AdminLayout 添加侧边栏导航**

在 `frontend/src/components/admin/AdminLayout.tsx` 的 `navItems` 数组中添加：

找到 `navItems` 数组定义位置，在其中插入新项：
```tsx
{
  to: '/admin/mascot',
  label: '看板娘',
  icon: ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a4 4 0 014 4c0 1.1-.7 2.6-1.5 3.5" />
      <circle cx="12" cy="14" r="3" />
      <path d="M9 10c-2 0-4 1-4 3s1 3 2 3.5M15 10c2 0 4 1 4 3s-1 3-2 3.5" />
    </svg>
  ),
},
```

- [ ] **Step 3: 构建验证**

```bash
cd frontend && npm run build && npm run lint
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/App.tsx frontend/src/components/admin/AdminLayout.tsx
git commit -m "feat: add mascot admin route and sidebar navigation"
```

---

### Task 12: 最终验证 + 推送

- [ ] **Step 1: 后端验证**

```bash
cd backend && uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 2: 前端构建 + lint**

```bash
cd frontend && npm run build && npm run lint
```

- [ ] **Step 3: 如果有后端测试**

```bash
cd backend && uv run pytest tests/ -v
```

- [ ] **Step 4: 推送**

```bash
git add -A  # 仅包含本次变动的文件
git commit -m "chore: final verification before push"
git push origin main
```
