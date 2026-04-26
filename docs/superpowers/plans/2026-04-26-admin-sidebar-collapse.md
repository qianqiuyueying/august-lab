# 后台侧边栏折叠/展开功能 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为后台管理系统侧边栏添加折叠和展开功能，折叠后变成 40px 窄条，点击或悬停可展开。

**Architecture:** 在 AdminLayout 组件中新增 `collapsed` 状态，`localStorage` 持久化。展开状态显示完整侧边栏（208px），折叠状态显示 40px 窄条仅含展开按钮。鼠标悬停窄条自动展开，离开后重新收起。

**Tech Stack:** React (useState), framer-motion (animate 动画), localStorage

---

## 文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| 修改 | `frontend/src/components/admin/AdminLayout.tsx` | 添加折叠状态和相关 UI |

---

### Task 1: 在 AdminLayout 中添加折叠状态和基础 UI

**Files:**
- Modify: `frontend/src/components/admin/AdminLayout.tsx`

- [ ] **Step 1: 添加状态和新图标导入**

在文件顶部 import 区域，添加以下 import（放在 motion import 后）：

```tsx
import { useState, useRef, useEffect, useCallback } from 'react';
```

在现有的 icon 组件下方添加两个新图标组件：

```tsx
function ChevronLeftIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}
```

- [ ] **Step 2: 在 AdminLayout 组件中添加状态管理**

在 `AdminLayout` 组件内，`location` 变量声明后添加：

```tsx
const [collapsed, setCollapsed] = useState(() => {
  const saved = localStorage.getItem('admin-sidebar-collapsed');
  return saved === 'true';
});

const hoverTimerRef = useRef<ReturnType<typeof setTimeout>>();

const handleCollapse = useCallback(() => {
  setCollapsed(true);
  localStorage.setItem('admin-sidebar-collapsed', 'true');
}, []);

const handleExpand = useCallback(() => {
  setCollapsed(false);
  localStorage.setItem('admin-sidebar-collapsed', 'false');
  if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
}, []);

const handleMouseEnter = useCallback(() => {
  if (!collapsed) return;
  hoverTimerRef.current = setTimeout(() => {
    handleExpand();
  }, 100);
}, [collapsed, handleExpand]);

const handleMouseLeave = useCallback(() => {
  if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
  if (!collapsed) {
    handleCollapse();
  }
}, [collapsed, handleCollapse]);

useEffect(() => {
  return () => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
  };
}, []);
```

- [ ] **Step 3: 替换侧边栏 JSX**

将 `AdminLayout` 中 `return` 内的整个 `<motion.aside>` 替换为以下代码：

```tsx
<motion.aside
  initial={false}
  animate={{ width: collapsed ? 40 : 208 }}
  transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
  onMouseEnter={collapsed ? handleMouseEnter : undefined}
  onMouseLeave={collapsed ? handleMouseLeave : undefined}
  className="h-screen bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 flex flex-col overflow-hidden"
>
  {/* 顶部标题行 */}
  <div className="relative flex items-center h-14 px-2 border-b border-zinc-200 dark:border-zinc-800">
    <motion.p
      animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
      transition={{ duration: 0.15 }}
      className="text-sm font-bold text-zinc-900 dark:text-white tracking-tight whitespace-nowrap overflow-hidden"
    >
      管理后台
    </motion.p>
    {collapsed ? (
      <button
        onClick={handleExpand}
        className="absolute left-1/2 -translate-x-1/2 p-1 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-500 dark:text-zinc-400 transition-colors"
        title="展开侧边栏"
      >
        <ChevronRightIcon />
      </button>
    ) : (
      <button
        onClick={handleCollapse}
        className="absolute right-2 p-1 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors"
        title="收起侧边栏"
      >
        <ChevronLeftIcon />
      </button>
    )}
  </div>

  {/* 导航区域 */}
  <nav className="flex-1 p-2.5 space-y-0.5">
    {navItems.map(({ to, label, icon: Icon }) => (
      <NavLink
        key={to}
        to={to}
        end={to === '/admin'}
        className={({ isActive }) =>
          `flex items-center gap-2.5 rounded-lg text-sm font-medium transition-colors ${
            collapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
          } ${
            isActive
              ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white'
              : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-white'
          }`
        }
      >
        <Icon />
        <motion.span
          animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
          transition={{ duration: 0.15 }}
          className="whitespace-nowrap overflow-hidden"
        >
          {label}
        </motion.span>
      </NavLink>
    ))}
  </nav>

  {/* 底部操作 */}
  <div className="p-2.5 border-t border-zinc-200 dark:border-zinc-800 space-y-0.5">
    <button
      onClick={() => navigate('/')}
      className={`flex items-center gap-2.5 w-full rounded-lg text-sm font-medium transition-colors ${
        collapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
      } text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-white`}
      title="返回首页"
    >
      <HomeIcon />
      <motion.span
        animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
        transition={{ duration: 0.15 }}
        className="whitespace-nowrap overflow-hidden"
      >
        返回首页
      </motion.span>
    </button>
    <button
      onClick={logout}
      className={`flex items-center gap-2.5 w-full rounded-lg text-sm font-medium transition-colors ${
        collapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
      } text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10`}
      title="退出登录"
    >
      <LogoutIcon />
      <motion.span
        animate={{ opacity: collapsed ? 0 : 1, width: collapsed ? 0 : 'auto' }}
        transition={{ duration: 0.15 }}
        className="whitespace-nowrap overflow-hidden"
      >
        退出登录
      </motion.span>
    </button>
  </div>
</motion.aside>
```

- [ ] **Step 4: 验证构建**

```bash
cd frontend && npm run build
```

预期：构建成功。如有类型检查错误，确保所有变量和回调引用正确。

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/admin/AdminLayout.tsx
git commit -m "feat: add collapsible sidebar with hover expand and localStorage persistence"
```

---

## 验证

1. `npm run dev` 启动前端
2. 访问 `/admin`，确认侧边栏正常显示（展开状态）
3. 点击顶部 `<<` 按钮，侧边栏平滑收起至 40px 窄条
4. 确认窄条上显示 `>>` 展开按钮
5. 鼠标悬停在窄条上，确认 100ms 后自动展开
6. 鼠标离开，确认自动重新收起
7. 点击 `>>` 按钮展开，刷新页面，确认侧边栏保持展开状态（localStorage 生效）
