# 首页图片加载优化 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 首页 4 张全屏背景图从 ~4MB PNG 改为 WebP + Next.js Image 优化管道，体积减少 ~86%，首屏 Hero LCP < 1s

**Architecture:** 用 sharp 将 4 张 PNG 转为 WebP（质量 82），新建 `BgImage` 组件封装 `next/image` 的 `fill` 模式，替换 `home-client.tsx` 中的原生 `<img>` 标签，Hero 图用 `priority` 预加载。配置 `next.config.ts` 开启 AVIF/WebP 自动格式。

**Tech Stack:** Next.js (app router), sharp (已安装), TypeScript, CSS

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `public/uploads/*.webp` | 4 张新 WebP 图片（与 PNG 原文件共存） |
| `next.config.ts` | Next.js 全局配置 — 开启 AVIF/WebP 图片格式 |
| `components/bg-image.tsx` | 新建 — 全屏背景图组件，封装 next/image fill 模式 |
| `app/home-client.tsx` | 改 — secImages 数组换 WebP 扩展名，4 处 `<img>` 换 `<BgImage>` |
| `app/home.css` | 改 — 删除 `.home-section__bg img` 规则（已被 next/image 内置样式覆盖） |

---

### Task 1: 转换 4 张背景 PNG → WebP

**Files:**
- Create: `public/uploads/venetian-blind-shadow.webp`
- Create: `public/uploads/perforated-metal-shadow.webp`
- Create: `public/uploads/plaster-geometric.webp`
- Create: `public/uploads/glass-shadow.webp`

- [ ] **Step 1: 用 sharp 批量转换 4 张 PNG 为 WebP（质量 82）**

```bash
node -e "
const sharp = require('sharp');
const path = require('path');
const files = [
  'venetian-blind-shadow.png',
  'perforated-metal-shadow.png',
  'plaster-geometric.png',
  'glass-shadow.png',
];
(async () => {
  for (const f of files) {
    const inPath = path.join('public/uploads', f);
    const outPath = path.join('public/uploads', f.replace(/\.png$/, '.webp'));
    const { size: inSize } = require('fs').statSync(inPath);
    await sharp(inPath).webp({ quality: 82 }).toFile(outPath);
    const { size: outSize } = require('fs').statSync(outPath);
    console.log(f, '→', path.basename(outPath), (inSize/1024).toFixed(0) + 'KB → ' + (outSize/1024).toFixed(0) + 'KB', '(' + (100 - outSize/inSize*100).toFixed(0) + '% smaller)');
  }
})();
"
```

Expected output: 每行显示转换前后的文件大小和压缩率。

- [ ] **Step 2: 确认 4 个 WebP 文件已生成且大小合理**

```bash
ls -la public/uploads/*.webp
```

Expected: 4 个 `.webp` 文件，每个约 100-200 KB。

- [ ] **Step 3: 提交**

```bash
git add public/uploads/venetian-blind-shadow.webp public/uploads/perforated-metal-shadow.webp public/uploads/plaster-geometric.webp public/uploads/glass-shadow.webp
git commit -m "perf: convert 4 homepage background images from PNG to WebP (quality 82)

~4MB → ~550KB total, 86% smaller. Original PNGs kept for fallback uses in blog, products, login pages.
"
```

---

### Task 2: 配置 Next.js 图片格式

**Files:**
- Modify: `next.config.ts`

- [ ] **Step 1: 修改 next.config.ts 开启 AVIF/WebP**

当前内容：
```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
```

改为：
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

- [ ] **Step 2: 验证配置无语法错误**

```bash
npx tsc --noEmit next.config.ts 2>&1
```

Expected: no errors（或只有 pre-existing 的非本项目错误）。

- [ ] **Step 3: 提交**

```bash
git add next.config.ts
git commit -m "feat: enable AVIF/WebP image optimization in Next.js config"
```

---

### Task 3: 创建 BgImage 组件

**Files:**
- Create: `components/bg-image.tsx`

- [ ] **Step 1: 创建组件文件**

```tsx
import Image from "next/image";

interface BgImageProps {
  src: string;
  alt: string;
  priority?: boolean;
  /** parallax speed, passed to data-parallax attribute */
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

- [ ] **Step 2: 验证 TypeScript 无错误**

```bash
npx tsc --noEmit
```

Expected: 无新增 TS 错误。

- [ ] **Step 3: 提交**

```bash
git add components/bg-image.tsx
git commit -m "feat: add BgImage component for fullscreen background images

Wraps next/image fill mode with quality=82, sizes=100vw,
priority prop for above-the-fold preload."
```

---

### Task 4: 更新 home-client.tsx

**Files:**
- Modify: `app/home-client.tsx`

- [ ] **Step 1: 修改 secImages 数组（第 161-166 行）**

原文：
```tsx
  const secImages = [
    "/uploads/venetian-blind-shadow.png",
    "/uploads/perforated-metal-shadow.png",
    "/uploads/plaster-geometric.png",
    "/uploads/glass-shadow.png",
  ];
```

改为：
```tsx
  const secImages = [
    "/uploads/venetian-blind-shadow.webp",
    "/uploads/perforated-metal-shadow.webp",
    "/uploads/plaster-geometric.webp",
    "/uploads/glass-shadow.webp",
  ];
```

- [ ] **Step 2: 在文件顶部添加 BgImage 导入**

在现有 `import Link from "next/link";` 之后添加：
```tsx
import { BgImage } from "@/components/bg-image";
```

- [ ] **Step 3: 替换 Hero section 背景图（原第 202-204 行）**

原文：
```tsx
          <div className="home-section__bg" data-parallax="0.3">
            <img src={secImages[0]} alt="百叶窗光影" loading="eager" />
          </div>
```

改为：
```tsx
          <BgImage src={secImages[0]} alt="百叶窗光影" priority parallax="0.3" />
```

- [ ] **Step 4: 替换 Section 2（博客）背景图（原第 232-233 行）**

原文：
```tsx
          <div className="home-section__bg" data-parallax="0.3">
            <img src={secImages[1]} alt="穿孔金属板光影" loading="lazy" />
          </div>
```

改为：
```tsx
          <BgImage src={secImages[1]} alt="穿孔金属板光影" parallax="0.3" />
```

- [ ] **Step 5: 替换 Section 3（产品）背景图（原第 279-280 行）**

原文：
```tsx
          <div className="home-section__bg" data-parallax="0.25">
            <img src={secImages[2]} alt="几何石膏体" loading="lazy" />
          </div>
```

改为：
```tsx
          <BgImage src={secImages[2]} alt="几何石膏体" parallax="0.25" />
```

- [ ] **Step 6: 替换 Section 4（引用）背景图（原第 322-323 行）**

原文：
```tsx
          <div className="home-section__bg" data-parallax="0.2">
            <img src={secImages[3]} alt="玻璃杯阴影" loading="lazy" />
          </div>
```

改为：
```tsx
          <BgImage src={secImages[3]} alt="玻璃杯阴影" parallax="0.2" />
```

- [ ] **Step 7: 验证 TypeScript 无错误**

```bash
npx tsc --noEmit
```

Expected: 无新增 TS 错误。

- [ ] **Step 8: 提交**

```bash
git add app/home-client.tsx
git commit -m "refactor: replace native img with BgImage component on homepage

Use Next.js Image optimization for all 4 fullscreen background
images. Hero gets priority preload; others lazy-load with AVIF/WebP."
```

---

### Task 5: 清理 home.css 冗余样式

**Files:**
- Modify: `app/home.css`

- [ ] **Step 1: 删除 `.home-section__bg img` 规则（第 116-121 行）**

原文：
```css
.home-section__bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  will-change: transform;
}
```

直接删除这 6 行。Next.js `fill` 模式已内置 `position: absolute; height: 100%; width: 100%`，`object-fit: cover` 由 BgImage 组件的 `style` prop 提供。`will-change: transform` 在 `.home-section__bg` 上已有。

- [ ] **Step 2: 确认 `.home-section__bg` 规则不变**

保留（确认无需修改，`position: absolute; inset: -8%; overflow: hidden; will-change: transform;` 是 next/image fill 需要的定位上下文）：

```css
.home-section__bg {
  position: absolute;
  inset: -8%;
  z-index: 0;
  overflow: hidden;
  will-change: transform;
}
```

- [ ] **Step 3: 提交**

```bash
git add app/home.css
git commit -m "style: remove redundant .home-section__bg img rule

Next.js Image fill mode already sets position, width, height.
object-fit is handled by BgImage component style prop.
will-change is already on the parent .home-section__bg."
```

---

### Task 6: 构建验证

- [ ] **Step 1: 生产构建测试**

```bash
npm run build 2>&1
```

Expected: 构建成功，无错误。观察是否有任何关于 images 配置的 warning。

- [ ] **Step 2: 检查构建输出中的图片引用**

```bash
ls -la .next/cache/images/ 2>&1 || echo "No image cache yet (expected on first build with next/image)"
```

Expected: Next.js 会在构建时或首次请求时生成优化后的图片变体。

- [ ] **Step 3: 最终提交（如有必要）**

仅当构建过程中产生了需要追踪的配置变更时提交。

---

## 预期结果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 4 张背景图源文件总大小 | ~4 MB (PNG) | ~550 KB (WebP) |
| 实际传输（浏览器选最优） | ~4 MB | ~350 KB |
| Hero 首屏 LCP | 3-5s (弱网) | < 1s (priority preload) |
| 非首屏图行为 | 懒加载原始 PNG | 懒加载 AVIF/WebP 优化版本 |

## 不在此计划范围内

- `lib/constants.ts`、`app/blog/`、`app/products/`、`app/login/`、`prisma/seed.ts` 中的 PNG 引用保持不变（它们用的是 fallback/cover 场景，体积影响较小）
- `atelier/` 目录（静态 HTML 原型，非 Next.js 应用，不参与构建）
