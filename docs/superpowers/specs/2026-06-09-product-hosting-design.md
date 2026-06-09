# 作品托管 — 静态页面上传与 iframe 运行

> 日期：2026-06-09  
> 状态：已确认

---

## 1. 问题

产品（作品）当前理解为"外部链接"，产品详情用 iframe 加载第三方 URL。实际需求是：产品是用户上传的**静态页面/游戏/Demo**，系统托管后通过 iframe 在前台运行。

---

## 2. Product 模型变更

| 字段 | 旧 | 新 | 说明 |
|------|-----|-----|------|
| `url` | String | **移除** | 不再需要外部链接 |
| `runtimePath` | — | String (新增) | 解压后的文件夹路径，如 `products/tools-2026` |
| `fileSize` | — | Int (新增) | 上传 zip 的文件大小（字节） |
| `runtimeEntry` | — | String (新增)，默认 `index.html` | 入口文件名 |

---

## 3. 上传流程

```
管理员选择 zip 文件
  ↓
前端校验：扩展名必须为 .zip，文件大小 ≤ 50MB
  ↓
POST /api/products/upload/[id]（上传运行时文件）
  ↓
后端校验：
  1. 文件是有效的 zip 格式
  2. 解压总大小 ≤ 100MB
  3. 根目录必须包含 index.html
  4. 遍历所有文件，检查扩展名白名单
     （不允许 .php .exe .dll .sh .bat .py .pl .rb .jsp 等服务端/可执行文件）
  ↓
校验失败 → 返回错误消息
  ↓
校验通过 → 解压到 public/products/[slug]/
  ↓
更新 Product.runtimePath = "products/[slug]"
更新 Product.fileSize = 上传的 zip 文件大小
  ↓
返回成功
```

---

## 4. 运行时访问

产品详情页（`/products/[slug]`）：

- iframe `src` = `/products/[slug]/index.html`
- 没有上传运行时文件时，iframe 显示占位提示
- "新窗口"按钮打开 `/products/[slug]/index.html` 到新标签页

---

## 5. 允许的静态文件扩展名白名单

| 类别 | 扩展名 |
|------|--------|
| 页面 | `.html` `.htm` `.xhtml` |
| 样式 | `.css` `.scss` `.less` |
| 脚本 | `.js` `.mjs` `.ts` `.json` `.jsx` `.tsx` |
| 图片 | `.png` `.jpg` `.jpeg` `.gif` `.svg` `.webp` `.ico` `.bmp` `.avif` |
| 字体 | `.woff` `.woff2` `.ttf` `.otf` `.eot` |
| 音频 | `.mp3` `.wav` `.ogg` `.m4a` `.aac` `.flac` |
| 视频 | `.mp4` `.webm` `.ogv` `.avi` `.mov` |
| WebAssembly | `.wasm` |
| 数据 | `.csv` `.xml` `.txt` `.md` `.yaml` `.yml` `.toml` |
| 地图瓦片 | `.pbf` `.mvt` |

校验时文件名转为小写后匹配。

---

## 6. 涉及变更的页面和 API

| 位置 | 变更 |
|------|------|
| `prisma/schema.prisma` | Product 模型：删 `url`，加 `runtimePath`、`fileSize`、`runtimeEntry` |
| `app/api/products/route.ts` | 创建/更新 Product 时处理新字段 |
| `app/api/products/upload/[id]/route.ts` | 新增：接收 zip、校验、解压 |
| `app/admin/products/new/page.tsx` | 产品新建表单：去外部 URL，加上传文件区 |
| `app/admin/products/[id]/edit/page.tsx` | 产品编辑表单：显示已上传文件的路径和大小 |
| `app/products/[slug]/product-detail-client.tsx` | iframe src 改为 `/products/[slug]/index.html` |
| `app/products/[slug]/product-detail.css` | 无变更 |

---

## 7. 约束

- 单个 zip 最大 50MB，解压后总大小 ≤ 100MB
- 必须包含 `index.html` 作为入口
- 只允许白名单扩展名
- zip 解压覆盖已有文件（更新操作时覆盖旧文件）
- 不扫描文件内容，仅校验扩展名
- 大文件（30MB+）上传可能超时，前端显示进度提示

---

## 8. 与现有文章的边界

- **文章**：Markdown 内容，博客性质
- **作品/产品**：上传的静态页面，可在线运行/体验
- 两者不交叉
