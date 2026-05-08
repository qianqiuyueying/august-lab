# 看板娘 AI 对话 + 主题配色重构 · 设计文档

## 1. 概述

两个并行任务：
- **主题配色重构**：GlassPanel Depth Layer 方案 + 其他组件硬编码颜色修复
- **看板娘 AI 对话 + 管理后台**：DeepSeek API 驱动的对话气泡 + 前台配置数据库化

---

## 2. 主题配色重构

### 2.1 GlassPanel · Depth Layer

在 `index.css` 新增 `.glass-panel` component class，替代 `GlassPanel.tsx` 中的硬编码颜色。

**浅色模式：**
- background: `linear-gradient(180deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.35) 100%)`
- border: `1px solid rgba(255,255,255,0.4)`
- box-shadow: `inset 0 1px 0 rgba(255,255,255,0.8), 0 8px 32px rgba(15,23,42,0.04)`
- backdrop-filter: `blur(20px)`

**暗色模式 (`.dark .glass-panel`)：**
- background: `linear-gradient(180deg, rgba(23,31,51,0.7) 0%, rgba(17,24,39,0.4) 100%)`
- border: `1px solid rgba(255,255,255,0.06)`
- box-shadow: `inset 0 1px 0 rgba(255,255,255,0.06), 0 8px 32px rgba(0,0,0,0.3)`
- backdrop-filter: `blur(20px)`

**GlassPanel.tsx 改动：**
- 移除内联所有颜色 class，改为 `className="glass-panel ..."`
- 保留 `accentLine` prop（顶部渐变线不变）

### 2.2 其他组件硬编码颜色修复

| 文件 | 当前 | 修复后 |
|------|------|--------|
| `ProductPage.tsx` 信息栏 | `bg-white/80` | `bg-white/80 dark:bg-surface-dark/80` |
| `ProductPage.tsx` 滑出面板 | `bg-white/95` | `bg-white/95 dark:bg-surface-dark/95` |
| `ProductsPage.tsx` hover | `group-hover:bg-white/70` | 改用 `.glass-panel` |
| `ArticleEditor.tsx` | `dark:bg-zinc-900` | `dark:bg-surface-dark`（统一 token） |
| `ProductPage.tsx` iframe | `bg-white` | `bg-white dark:bg-surface-dark` |

---

## 3. 看板娘 AI 对话 + 管理后台

### 3.1 数据库

新建 `mascot_settings` 表（单行配置，ORM 模型）：

| 字段 | 类型 | 默认值 |
|------|------|--------|
| `id` | int PK | 1 |
| `persona` | text | 见 3.2 |
| `api_key` | text | "" |
| `api_base_url` | text | `https://api.deepseek.com` |
| `model` | text | `deepseek-chat` |
| `temperature` | float | 0.8 |
| `max_tokens` | int | 512 |
| `enabled` | bool | false |
| `mascot_visible` | bool | true |
| `mascot_scale` | float | 1.2 |
| `mascot_position_x` | int | null (默认右下) |
| `mascot_position_y` | int | null |
| `show_on_mobile` | bool | false |
| `greeting_enabled` | bool | true |
| `greeting_delay_seconds` | int | 8 |
| `random_action_interval` | int | 15 |
| `context_aware` | bool | false |
| `drag_enabled` | bool | true |

### 3.2 默认 System Prompt

```
你是刻晴，August's Lab 技术博客的看板娘小助手。
性格：活泼元气、略傲娇、喜欢用颜文字和拟声词。
说话风格：轻松可爱、偶尔吐槽，对技术保持好奇心。
知识范围：前端开发、React、Python、开源技术。
规则：回复简洁（1-3 句），不要长篇大论，保持角色感。
```

### 3.3 API 端点

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| `GET` | `/api/mascot/settings` | 公开 | 返回前端所需配置（排除 api_key） |
| `POST` | `/api/mascot/chat` | 公开 | `{ message, context? }` → 流式 SSE 返回 |
| `GET` | `/api/admin/mascot/settings` | JWT | 管理员读完整配置 |
| `PUT` | `/api/admin/mascot/settings` | JWT | 管理员更新配置 |

**POST /api/mascot/chat 处理流程：**
1. 读取 mascot_settings
2. 拼接 messages: `[{ role: "system", content: persona }, { role: "user", content: message }]`
3. 如果 context_aware 且前端传了 `context`（页面标题等），追加到 system prompt
4. 调用 DeepSeek API（OpenAI 兼容格式），流式返回 SSE

**DeepSeek API 调用 (OpenAI SDK)：**
```python
client = OpenAI(base_url=settings.api_base_url, api_key=settings.api_key)
response = client.chat.completions.create(
    model=settings.model,
    messages=messages,
    temperature=settings.temperature,
    max_tokens=settings.max_tokens,
    stream=True,
)
```

### 3.4 前端文件

| 文件 | 说明 |
|------|------|
| `src/api/mascot.ts` | getMascotSettings(), sendMascotChat(message, context?) |
| `src/components/mascot/ChatBubble.tsx` | 对话气泡组件：消息展示 + 输入框 + 流式渲染 |
| `src/components/mascot/MascotPet.tsx` | 改动：从 API 加载 settings；集成 ChatBubble |
| `src/pages/admin/AdminMascot.tsx` | 管理页面：分组表单 + 右侧实时预览 |
| `src/components/admin/AdminLayout.tsx` | 侧边栏新增"看板娘"入口 |
| `src/types/index.ts` | 新增 MascotSettings 类型 |

### 3.5 ChatBubble 交互

- 点击看板娘：弹出对话窗口（带输入框）
- 发送消息：POST 流式请求，逐字渲染回复
- 自动问候：页面加载后 `greeting_delay_seconds` 秒弹出气泡（无输入框，仅显示一句问候）
- 上下文感知：如果开启，将 `document.title` 或当前文章标题作为 context 发送
- 关闭气泡：点击 x 或点击看板娘其他区域

### 3.6 管理页面 AdminMascot.tsx 布局

```
┌──────────────────────────────────────────────────┐
│  看板娘设置                                       │
├────────────────────┬─────────────────────────────┤
│  [角色设定]         │                             │
│  ┌──────────────┐  │    👤 看板娘实时预览         │
│  │ textarea     │  │                             │
│  │ (system      │  │    ┌───────────────────┐    │
│  │  prompt)     │  │    │  💬 你好呀！       │    │
│  └──────────────┘  │    │  我是刻晴~ ⚡     │    │
│                    │    └───────────────────┘    │
│  [API 配置]         │                             │
│  api_key / url     │    🎨 外观预览               │
│  model / temp      │    (Canvas 实时渲染)         │
│                    │                             │
│  [外观设置]         │                             │
│  scale / visible   │                             │
│  position / mobile │                             │
│                    │                             │
│  [行为设置]         │                             │
│  greeting / random │                             │
│  context / drag    │                             │
├────────────────────┴─────────────────────────────┤
│  [保存]                                            │
└──────────────────────────────────────────────────┘
```

---

## 4. 实现顺序

1. **数据库 + 后端模型** — `mascot_settings` 表 + ORM + migration
2. **后端 API** — schemas + router + DeepSeek 集成
3. **主题修复** — GlassPanel + index.css + 各组件硬编码修复
4. **前端 MascotPet 改造** — settings 加载 + 看板娘配置从 API 读取
5. **ChatBubble 组件** — 对话 UI + 流式渲染
6. **AdminMascot 页面** — 管理表单 + 预览
7. **集成 + 路由** — AdminLayout 侧边栏 + App.tsx
8. **构建验证**

## 5. 验证

- `cd backend && uv run pytest tests/ -v` — 后端测试（含新增 mascot API 测试）
- `cd frontend && npm run build && npm run lint` — 前端类型检查 + 构建
- 浏览器验证：看板娘对话、管理后台 CRUD、暗色/浅色 GlassPanel 效果
