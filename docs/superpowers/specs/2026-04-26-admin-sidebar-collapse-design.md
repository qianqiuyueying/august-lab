# 后台侧边栏折叠/展开功能 — 设计文档

> 日期：2026-04-26
> 状态：待审批

## 背景

当前后台管理侧边栏固定宽度（208px），无法收起，内容区域空间受限。用户希望在不使用时将侧边栏折叠成极窄的轨道，需要时通过点击或悬停快速展开。

## 架构

仅改动 1 个文件：`frontend/src/components/admin/AdminLayout.tsx`。

通过 `useState` 管理折叠状态，`localStorage` 持久化用户选择。

## 交互设计

### 展开状态（当前状态）

侧边栏完整显示，宽度 208px。导航项显示"图标 + 文字"。

顶部新增折叠按钮（`<<` 或 `<` 图标），点击后收起侧边栏。

```
┌─── 管理后台 ──────────── <<
│ [仪表盘]
│ [文章管理]
│ [产品管理]
│ [关于页]
│ [站点设置]
│
│ 返回首页
│ 退出登录
└──────────────────────────┐
│                         │  主内容区
│                         │
└──────────────────────────┘
```

### 折叠状态

侧边栏缩成 40px 宽的窄条，不显示导航项文字和底部按钮。

窄条顶部显示展开按钮（`>>`），点击展开。
鼠标悬停在窄条上时自动展开完整侧边栏，鼠标离开后重新收起。

```
┌── >>
│
│
│
│
│
│
└──┐
   │  主内容区（占满剩余空间）
   │
```

## 状态管理

```ts
const [collapsed, setCollapsed] = useState(() => {
  const saved = localStorage.getItem('admin-sidebar-collapsed');
  return saved === 'true';
});
```

折叠/展开时同步写入 `localStorage`：
```ts
const toggle = (next: boolean) => {
  setCollapsed(next);
  localStorage.setItem('admin-sidebar-collapsed', String(next));
};
```

## 动画与过渡

- 侧边栏宽度变化使用 `framer-motion` 的 `animate` 属性，`layout` 动画平滑过渡
- 文字在折叠时淡出（`opacity` 从 1 → 0），展开时淡入
- 窄条背景与完整侧边栏相同（`bg-white dark:bg-zinc-900`）

## 技术细节

- **折叠按钮**：放在侧边栏顶部标题旁边，`absolute` 定位在右侧
- **展开按钮**：折叠状态下固定在窄条顶部
- **悬停展开**：在折叠状态下的侧边栏上绑定 `onMouseEnter` / `onMouseLeave`
- **防抖**：鼠标快速滑过窄条时不应频繁切换，设置 100ms 延迟
