# 首页图片加载优化 — 设计方案

**日期:** 2026-06-10  
**状态:** 待实施  
**目标:** 首页 4 张全屏背景图从 ~4MB 压缩到 ~350KB，消除白屏闪烁

---

## 问题现状

首页使用 4 张全屏背景 PNG 图片，合计约 4 MB：

| 文件 | 大小 |
|------|------|
| `venetian-blind-shadow.png` | 1.38 MB |
| `perforated-metal-shadow.png` | 1.01 MB |
| `plaster-geometric.png` | 794 KB |
| `glass-shadow.png` | 847 KB |

使用原生 `<img>` 标签，无 Next.js 图片优化。仅 Hero 图用了 `loading="eager"`，其余为 `loading="lazy"`。弱网下首屏 LCP 可达 3-5 秒。

---

## 方案

采用 **Next.js Image 优化管道**：

1. PNG → WebP 格式转换（质量 82）
2. `next/image` + `fill` 模式自动生成 AVIF/WebP 多尺寸变体
3. Hero 首屏图 `priority` 预加载，其余自动懒加载
4. 新建 `BgImage` 组件封装背景图渲染逻辑

---

## 涉及文件

| 文件 | 操作 |
|------|------|
| `next.config.ts` | 改 — 添加 `images.formats: ["image/avif", "image/webp"]` |
| `public/uploads/*.webp` | 新增 — 4 张 WebP 图片 (sharp 转换) |
| `components/bg-image.tsx` | 新增 — 全屏背景图组件 |
| `app/home-client.tsx` | 改 — 更新 secImages URL + 使用 BgImage |
| `app/home.css` | 改 — 删除 `.home-section__bg img` 冗余规则 |

---

## 各模块设计

### 1. 格式转换

`public/uploads/` 目录下的 4 张 PNG 转 WebP（质量 82），预估体积：

| 原文件 (PNG) | 新文件 (WebP) |
|---|---|
| 1.38 MB → | ~180 KB |
| 1.01 MB → | ~140 KB |
| 794 KB → | ~110 KB |
| 847 KB → | ~120 KB |
| **~4 MB →** | **~550 KB** |

转换后删除原 PNG 文件（经搜索确认无其他引用）。

### 2. next.config.ts

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
```

开启后 `next/image` 自动为每张图生成 AVIF + WebP 多尺寸版本。AVIF 浏览器覆盖率 ~93%，不支持时回落 WebP。

### 3. BgImage 组件 (`components/bg-image.tsx`)

```tsx
import Image from "next/image";

interface BgImageProps {
  src: string;
  alt: string;
  priority?: boolean;
  parallax?: string;
}

export function BgImage({ src, alt, priority = false, parallax }: BgImageProps) {
  return (
    <div className="home-section__bg" data-parallax={parallax}>
      <Image
        src={src}
        alt={alt}
        fill
        sizes="100vw"
        priority={priority}
        quality={82}
        style={{ objectFit: "cover" }}
      />
    </div>
  );
}
```

- `fill` — 自动填充父容器（`.home-section__bg` 已有 `position: absolute`）
- `sizes="100vw"` — 全屏宽度，Next.js 按此生成合适尺寸
- `priority` — Hero 传 `true`，跳过懒加载；其余不传，自动 `loading="lazy"`
- `quality={82}` — 兼顾画质与体积

### 4. home-client.tsx

- `secImages` 数组：`.png` → `.webp`
- 背景图渲染：`<img>` → `<BgImage>`，Hero 加 `priority`

```tsx
const secImages = [
  "/uploads/venetian-blind-shadow.webp",
  "/uploads/perforated-metal-shadow.webp",
  "/uploads/plaster-geometric.webp",
  "/uploads/glass-shadow.webp",
];

// Hero (section 0):
<BgImage src={secImages[0]} alt="百叶窗光影" priority parallax="0.3" />

// 其余 section:
<BgImage src={secImages[i]} alt="..." parallax="0.3" />
```

### 5. home.css

`.home-section__bg img` 规则直接删除 — Next.js `fill` 模式已内置 `position: absolute; height: 100%; width: 100%`。

`.home-section__bg` 自身保持不变：
```css
.home-section__bg {
  position: absolute;
  inset: -8%;
  z-index: 0;
  overflow: hidden;
}
```

---

## 不做的事

- **blurDataURL 模糊占位** — 背景图在深色渐变叠层下方，加载过程中深色背景已吸收白屏，blur placeholder 边际收益小，省掉复杂度
- **sharp 运行时生成** — Next.js 内置优化已覆盖，无需手动调用 sharp API
- **CDN 缓存策略配置** — 保持现有部署方式不变

---

## 预期效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 4 张图总体积 | ~4 MB (PNG) | ~550 KB (WebP 源) + AVIF 变体 |
| 实际传输（浏览器选最优格式） | 4 MB | ~350 KB |
| 首屏 Hero LCP | 3-5s (弱网) | < 1s (priority preload) |
| 非首屏图 | 滚动时加载 3 张 PNG | 懒加载 AVIF/WebP |
