# 作品托管 — 静态页面上传实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 Product 从"外部链接"改为"上传静态页面托管"，管理员上传 zip 包，前台 iframe 运行。

**Architecture:** 新增 `lib/upload-validator.ts` 负责 zip 校验逻辑；新增 `app/api/products/upload/[id]/route.ts` 接收上传并解压到 `public/products/[slug]/`；修改 Product 模型删 `url` 加 `runtimePath`/`fileSize`/`runtimeEntry`；修改产品表单加文件上传区；修改产品详情页 iframe src 指向托管目录。

**Tech Stack:** Next.js API Routes, adm-zip (zip 解压/校验), fs 模块

---

## 文件结构

```
lib/
  upload-validator.ts          (新增) 白名单、index.html 校验、zip 解压

app/api/products/
  upload/[id]/route.ts         (新增) 上传 zip 的 API 端点
  route.ts                     (修改) 创建/更新忽略 url 字段
  [id]/route.ts                (修改) 返回 runtimePath 等新字段

prisma/
  schema.prisma                (修改) Product 模型字段变更
  migrations/                  (自动) 迁移文件

app/products/[slug]/
  page.tsx                     (修改) 传新字段给 client
  product-detail-client.tsx    (修改) iframe src 指向托管文件
  product-detail.css           (无变更)

components/admin/
  product-form.tsx             (修改) 去 URL、加文件上传

app/admin/products/new/page.tsx  (修改) 添加客户端交互
app/admin/products/[id]/edit/page.tsx (修改) 传递新字段
```

---

### Task 1：Prisma 迁移 — Product 模型字段变更

**Files:**
- Modify: `prisma/schema.prisma`
- Run: `npx prisma migrate dev`

- [ ] **Step 1: 修改 Product 模型**

```prisma
model Product {
  id           Int       @id @default(autoincrement())
  slug         String    @unique
  title        String
  description  String    @default("")
  content      String    @default("")
  coverImage   String    @default("")
  images       String[]  @default([])
  tags         String[]  @default([])
  status       String    @default("draft")
  runtimePath  String    @default("")   // 新增: 解压路径，如 "products/tools-2026"
  fileSize     Int       @default(0)    // 新增: zip 文件字节数
  runtimeEntry String    @default("index.html")  // 新增: 入口文件名
  featured     Boolean   @default(false)
  published    Boolean   @default(false)
  publishedAt  DateTime?
  createdAt    DateTime  @default(now())
  updatedAt    DateTime  @updatedAt
}
```

从模型中**删除** `url String @default("")` 一行。

- [ ] **Step 2: 准备 adm-zip 依赖**

```bash
npm install adm-zip
npm install -D @types/adm-zip
```

- [ ] **Step 3: 生成迁移**

```bash
npx prisma migrate dev --name add_product_runtime_fields
```

Expected: 迁移文件生成，`url` 列被删除，`runtimePath`/`fileSize`/`runtimeEntry` 三个新列添加。

- [ ] **Step 4: 更新种子数据**

在 `prisma/seed.ts` 中更新 Product 创建调用，去掉 `url`，加上新字段默认值：

```typescript
// 以 tools-2026 为例，其他同理
{
  slug: "tools-2026",
  title: "工具集 · 2026",
  // ... 其他字段不变
  runtimePath: "",    // 新增：未上传运行时文件
  fileSize: 0,
  runtimeEntry: "index.html",
  // 删除 url 字段
}
```

- [ ] **Step 5: 重新运行种子**

```bash
npx prisma db seed
```

Expected: `✅ Seed data inserted successfully`

- [ ] **Step 6: Commit**

```bash
git add prisma/schema.prisma prisma/migrations/ prisma/seed.ts
git commit -m "feat: update Product model — replace url with runtimePath/fileSize/runtimeEntry"
```

---

### Task 2：上传校验工具函数

**Files:**
- Create: `lib/upload-validator.ts`

- [ ] **Step 1: 编写白名单和校验函数**

```typescript
// lib/upload-validator.ts
import AdmZip from "adm-zip";
import { join } from "path";

// 允许的扩展名白名单（小写）
export const ALLOWED_EXTENSIONS = new Set([
  // 页面
  ".html", ".htm", ".xhtml",
  // 样式
  ".css", ".scss", ".less",
  // 脚本
  ".js", ".mjs", ".ts", ".json", ".jsx", ".tsx",
  // 图片
  ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp", ".avif",
  // 字体
  ".woff", ".woff2", ".ttf", ".otf", ".eot",
  // 音频
  ".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac",
  // 视频
  ".mp4", ".webm", ".ogv", ".avi", ".mov",
  // WebAssembly
  ".wasm",
  // 数据/配置
  ".csv", ".xml", ".txt", ".md", ".yaml", ".yml", ".toml",
  // 地图瓦片
  ".pbf", ".mvt",
  // 其他
  ".gltf", ".glb", ".bin", ".dat",
]);

// 限制
export const MAX_ZIP_SIZE = 50 * 1024 * 1024;       // 50MB
export const MAX_EXTRACTED_SIZE = 100 * 1024 * 1024; // 100MB

export interface ValidationResult {
  ok: boolean;
  error?: string;
}

/**
 * 校验上传的 zip 文件
 * 1. 必须是有效的 zip
 * 2. 解压大小 ≤ MAX_EXTRACTED_SIZE
 * 3. 根目录必须有 index.html
 * 4. 所有文件扩展名在白名单中
 */
export function validatePackage(zipBuffer: Buffer, slug: string): ValidationResult {
  let zip: AdmZip;

  // 1. 解析 zip
  try {
    zip = new AdmZip(zipBuffer);
  } catch {
    return { ok: false, error: "无效的 zip 文件" };
  }

  const entries = zip.getEntries();

  if (entries.length === 0) {
    return { ok: false, error: "zip 文件为空" };
  }

  // 2. 检查解压后总大小
  const totalSize = entries.reduce((sum, e) => sum + (e.header.size || 0), 0);
  if (totalSize > MAX_EXTRACTED_SIZE) {
    return { ok: false, error: `解压后总大小 ${(totalSize / 1024 / 1024).toFixed(1)}MB 超过限制 ${MAX_EXTRACTED_SIZE / 1024 / 1024}MB` };
  }

  // 3. 检查根目录是否有 index.html
  const rootNames = new Set(
    entries
      .filter((e) => !e.isDirectory && !e.entryName.includes("/"))
      .map((e) => e.entryName.toLowerCase())
  );
  if (!rootNames.has("index.html")) {
    return { ok: false, error: "zip 根目录必须包含 index.html" };
  }

  // 4. 检查所有文件后缀名
  for (const entry of entries) {
    if (entry.isDirectory) continue;

    const name = entry.entryName.toLowerCase();
    const ext = name.lastIndexOf(".") === -1 ? "" : name.slice(name.lastIndexOf("."));

    if (!ext || !ALLOWED_EXTENSIONS.has(ext)) {
      return { ok: false, error: `不允许的文件类型: ${entry.entryName}` };
    }
  }

  return { ok: true };
}

/**
 * 解压 zip 到指定目录，覆盖已有文件
 */
export function extractPackage(zipBuffer: Buffer, targetDir: string): void {
  const AdmZip = require("adm-zip");
  const zip = new AdmZip(zipBuffer);
  zip.extractAllTo(targetDir, true);
}
```

- [ ] **Step 2: Commit**

```bash
git add lib/upload-validator.ts
git commit -m "feat: add zip upload validator with extension whitelist and index.html check"
```

---

### Task 3：上传 API 端点

**Files:**
- Create: `app/api/products/upload/[id]/route.ts`

- [ ] **Step 1: 编写上传 API**

```typescript
// app/api/products/upload/[id]/route.ts
import { NextResponse } from "next/server";
import { mkdir } from "fs/promises";
import { join } from "path";
import { prisma } from "@/lib/db";
import { validatePackage, extractPackage } from "@/lib/upload-validator";

export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const product = await prisma.product.findUnique({ where: { id: parseInt(id) } });
  if (!product) {
    return NextResponse.json({ error: "作品不存在" }, { status: 404 });
  }

  const formData = await req.formData();
  const file = formData.get("file") as File | null;

  if (!file || !file.name.endsWith(".zip")) {
    return NextResponse.json({ error: "请上传 .zip 文件" }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  // 校验
  const validation = validatePackage(buffer, product.slug);
  if (!validation.ok) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  // 解压
  const targetDir = join(process.cwd(), "public", "products", product.slug);
  await mkdir(targetDir, { recursive: true });
  extractPackage(buffer, targetDir);

  // 更新数据库
  await prisma.product.update({
    where: { id: parseInt(id) },
    data: {
      runtimePath: `products/${product.slug}`,
      fileSize: file.size,
      runtimeEntry: "index.html",
    },
  });

  return NextResponse.json({
    success: true,
    runtimePath: `products/${product.slug}`,
    fileSize: file.size,
  });
}
```

- [ ] **Step 2: 验证**

```bash
# 创建一个测试 zip
mkdir -p /tmp/test-product && echo "<h1>test</h1>" > /tmp/test-product/index.html
cd /tmp/test-product && zip -r test.zip . && cd -

# 上传测试（需要先创建一个 product）
curl -X POST http://localhost:3000/api/products/upload/1 \
  -F "file=@/tmp/test-product/test.zip"
```

Expected: 返回 `{"success": true, ...}`，`public/products/<slug>/index.html` 文件存在。

- [ ] **Step 3: Commit**

```bash
git add app/api/products/upload/
git commit -m "feat: add zip upload API endpoint with validation and extraction"
```

---

### Task 4：更新产品创建/编辑 API

**Files:**
- Modify: `app/api/products/route.ts`
- Modify: `app/api/products/[id]/route.ts`

- [ ] **Step 1: 确保创建时忽略已删除的 url 字段**

`app/api/products/route.ts` 和 `[id]/route.ts` 中的 `PUT` 方法使用 `...body` 展开，由于 Prisma 会忽略未知字段，`url` 不会造成问题。但需要确认新字段 `runtimePath`、`fileSize`、`runtimeEntry` 可以在更新时传入。

无需额外修改，当前实现已通过 `...body` 透传所有字段。

- [ ] **Step 2: Commit**

```bash
git add app/api/products/
git commit -m "fix: update product API to handle new runtime fields"
```

---

### Task 5：更新产品表单 — 去 URL、加文件上传

**Files:**
- Modify: `components/admin/product-form.tsx`

- [ ] **Step 1: 去掉 URL 字段，添加上传组件**

```tsx
// components/admin/product-form.tsx
"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

interface ProductFormData {
  slug: string; title: string; description: string; content: string;
  coverImage: string; tags: string; status: string;
  featured: boolean; published: boolean;
  runtimePath: string; fileSize: number; runtimeEntry: string;
}

const empty: ProductFormData = {
  slug: "", title: "", description: "", content: "",
  coverImage: "", tags: "", status: "online",
  featured: false, published: false,
  runtimePath: "", fileSize: 0, runtimeEntry: "index.html",
};

export function ProductForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ProductFormData>(empty);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "", title: initial.title ?? "",
        description: initial.description ?? "", content: initial.content ?? "",
        coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "), status: initial.status ?? "online",
        featured: initial.featured ?? false, published: initial.published ?? false,
        runtimePath: initial.runtimePath ?? "",
        fileSize: initial.fileSize ?? 0,
        runtimeEntry: initial.runtimeEntry ?? "index.html",
      });
    }
  }, [initial]);

  const set = (f: keyof ProductFormData, v: string | number | boolean) =>
    setForm((p) => ({ ...p, [f]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true);
    const payload = {
      ...form,
      tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
    };
    const url = isEdit ? `/api/products/${initial.id}` : "/api/products";
    const res = await fetch(url, {
      method: isEdit ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setSaving(false);
    if (res.ok) { router.push("/admin/products"); router.refresh(); }
    else { alert("保存失败"); }
  };

  // 上传 zip（仅在编辑模式下，因为需要已有的产品 ID）
  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file || !initial) return;

    if (!file.name.endsWith(".zip")) {
      setUploadMsg("只接受 .zip 文件");
      return;
    }

    setUploading(true);
    setUploadMsg("上传中...");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`/api/products/upload/${initial.id}`, {
      method: "POST",
      body: formData,
    });

    setUploading(false);

    if (res.ok) {
      const data = await res.json();
      set("runtimePath", data.runtimePath);
      set("fileSize", data.fileSize);
      setUploadMsg(`上传成功 (${(data.fileSize / 1024 / 1024).toFixed(1)}MB)`);
    } else {
      const err = await res.json();
      setUploadMsg(err.error || "上传失败");
    }
  };

  const formatSize = (bytes: number) =>
    bytes > 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)}MB` : `${(bytes / 1024).toFixed(0)}KB`;

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">{isEdit ? "编辑作品" : "新建作品"}</h1>
          {isEdit && form.runtimePath && (
            <p className="admin-page-header__desc" style={{ color: "oklch(0.65 0.12 160)" }}>
              运行时路径: {form.runtimePath} &nbsp;|&nbsp; {formatSize(form.fileSize)}
            </p>
          )}
        </div>
        <div className="admin-page-header__actions">
          <NextLink href="/admin/products" className="admin-btn">← 返回列表</NextLink>
          <button className="admin-btn admin-btn--primary" onClick={handleSubmit} disabled={saving}>
            {saving ? "保存中…" : "保存"}
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-sm)" }}>
        <div className="admin-section">
          <h2 className="admin-section__title">基本信息</h2>
          <div className="admin-form-grid">
            <div className="admin-form-group">
              <label className="admin-form-label">标识 (slug)</label>
              <input className="admin-input" value={form.slug} onChange={(e) => set("slug", e.target.value)} required />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">状态</label>
              <select className="admin-select" value={form.status} onChange={(e) => set("status", e.target.value)} style={{ width: "100%" }}>
                <option value="online">在线</option><option value="developing">开发中</option><option value="offline">已下线</option>
              </select>
            </div>
          </div>
          <div className="admin-form-group"><label className="admin-form-label">标题</label><input className="admin-input" value={form.title} onChange={(e) => set("title", e.target.value)} required /></div>
          <div className="admin-form-group"><label className="admin-form-label">简介</label><textarea className="admin-textarea" rows={3} value={form.description} onChange={(e) => set("description", e.target.value)} /></div>
          <div className="admin-form-group"><label className="admin-form-label">封面图 URL</label><input className="admin-input" value={form.coverImage} onChange={(e) => set("coverImage", e.target.value)} /></div>
          <div className="admin-form-group"><label className="admin-form-label">标签（逗号分隔）</label><input className="admin-input" value={form.tags} onChange={(e) => set("tags", e.target.value)} /></div>
          <div style={{ display: "flex", gap: "var(--sp-lg)" }}>
            <label className="admin-toggle"><input type="checkbox" checked={form.published} onChange={(e) => set("published", e.target.checked)} />发布</label>
            <label className="admin-toggle"><input type="checkbox" checked={form.featured} onChange={(e) => set("featured", e.target.checked)} />精选</label>
          </div>
        </div>

        <div className="admin-section">
          <h2 className="admin-section__title">正文 (Markdown)</h2>
          <textarea className="admin-textarea" rows={10} value={form.content} onChange={(e) => set("content", e.target.value)} />
        </div>

        {/* 仅在编辑模式显示上传区（需要已有产品 ID） */}
        {isEdit && (
          <div className="admin-section">
            <h2 className="admin-section__title">上传运行时文件</h2>
            <p style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginBottom: "var(--sp-sm)" }}>
              打包你的静态页面为 .zip（根目录需包含 index.html），支持 HTML/CSS/JS/图片/字体/音频/视频/WebAssembly，最大 50MB。
            </p>
            <div style={{ display: "flex", gap: "var(--sp-sm)", alignItems: "center" }}>
              <input ref={fileRef} type="file" accept=".zip" style={{ flex: 1 }} />
              <button type="button" className="admin-btn admin-btn--primary" onClick={handleUpload} disabled={uploading}>
                {uploading ? "上传中…" : "上传"}
              </button>
            </div>
            {uploadMsg && (
              <div style={{ marginTop: "var(--sp-sm)", fontSize: "var(--fs-small)", color: uploadMsg.includes("失败") ? "oklch(0.7 0.15 30)" : "oklch(0.65 0.12 160)", fontFamily: "var(--ff-mono)" }}>
                {uploadMsg}
              </div>
            )}
            {form.runtimePath && (
              <div style={{ marginTop: "var(--sp-sm)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)" }}>
                当前托管: <code style={{ fontFamily: "var(--ff-mono)", color: "var(--c-fg)" }}>{form.runtimePath}/{form.runtimeEntry}</code>
                {" "}({formatSize(form.fileSize)})
              </div>
            )}
          </div>
        )}
      </form>
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add components/admin/product-form.tsx
git commit -m "feat: add file upload to product form, remove url field"
```

---

### Task 6：更新产品详情页 — iframe 指向托管文件

**Files:**
- Modify: `app/products/[slug]/product-detail-client.tsx`
- Modify: `app/products/[slug]/page.tsx`

- [ ] **Step 1: 更新 server 端传递新字段**

```tsx
// app/products/[slug]/page.tsx（修改 ProductDetailClient 的 props 传递）
// product 对象自动包含 runtimePath/runtimeEntry/fileSize
// 无需改动 page.tsx，因为已经传入 product 对象
```

- [ ] **Step 2: 更新 client 端 iframe src**

在 `product-detail-client.tsx` 中修改：

```tsx
// 原本:
// {product.url ? (
//   <iframe src={product.url} ... />
// ) : (占位符)}

// 改为:
{product.runtimePath ? (
  <iframe
    src={`/${product.runtimePath}/${product.runtimeEntry || "index.html"}`}
    sandbox="allow-scripts allow-same-origin"
    title={product.title}
  />
) : (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--c-fg-dim)", fontFamily: "var(--ff-body)", background: "#000", position: "fixed", inset: 0, zIndex: 1 }}>
    此作品已发布但尚未上传运行文件
  </div>
)}
```

同样更新"新窗口"按钮：

```tsx
// 原本:
// {product.url && (
//   <button ... onClick={() => window.open(product.url, "_blank")}>新窗口</button>
// )}

// 改为:
{product.runtimePath && (
  <button
    className="runtime-toolbar__action"
    onClick={() => window.open(`/${product.runtimePath}/${product.runtimeEntry || "index.html"}`, "_blank")}
  >
    新窗口
  </button>
)}
```

- [ ] **Step 3: Commit**

```bash
git add app/products/[slug]/
git commit -m "feat: update product detail iframe to use hosted static files"
```

---

### Task 7：端到端验证

- [ ] **Step 1: 构建检查**

```bash
npm run build
```

Expected: 无 TypeScript 错误。

- [ ] **Step 2: 创建测试 zip**

```bash
mkdir -p /tmp/fish-game
cat > /tmp/fish-game/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>大鱼吃小鱼</title>
<style>body{margin:0;background:#1a3;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;color:#fff;font-size:4rem;}</style>
</head>
<body>🐟 ← 大鱼吃小鱼</body>
</html>
EOF
cd /tmp/fish-game && zip -r fish.zip . && cd -
```

- [ ] **Step 3: 验证全流程**

```bash
# 1. 确认 dev server 运行
# 2. POST 创建一个产品
curl -X POST http://localhost:3000/api/products \
  -H "Content-Type: application/json" \
  -d '{"slug":"fish-game","title":"大鱼吃小鱼","status":"online","published":true}' \
  -b "atelier_session=..."

# 3. 上传 zip
curl -X POST http://localhost:3000/api/products/upload/N \
  -F "file=@/tmp/fish-game/fish.zip" \
  -b "atelier_session=..."

# 4. 访问 /products/fish-game 在浏览器查看
```

- [ ] **Step 4: Commit**

```bash
git commit -m "test: end-to-end verification of product zip upload and hosting"
```

---

### 完成

**验收清单：**

- [ ] Product 模型已去掉 `url` 列
- [ ] 上传 .zip 成功后，`public/products/<slug>/index.html` 存在
- [ ] 上传校验拒接无 `index.html` 的 zip
- [ ] 上传校验拒绝不允许的扩展名（如 `.php`）
- [ ] 产品表单有文件上传区域（编辑模式）
- [ ] 产品详情页 iframe 加载托管页面
- [ ] "新窗口"按钮可以打开独立标签页
