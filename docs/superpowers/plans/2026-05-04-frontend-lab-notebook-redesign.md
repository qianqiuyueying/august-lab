# Frontend Lab Notebook Brand System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the frontend with a cohesive "Lab Notebook" brand system — dot grid backgrounds, experiment numbering, editorial layouts, and refined component language.

**Architecture:** Modify existing CSS tokens and components in place. Add new UI primitives (StatusDot, SectionNumber, TickDivider). Rewrite page layouts (Home, Blog, Products, About, Article) with editorial-style asymmetric grids. No new dependencies — all effects use existing framer-motion + Tailwind.

**Tech Stack:** React, Tailwind CSS v4, framer-motion v12, React Router v7

---

### Task 1: Core CSS Design Tokens + Background System

**Files:**
- Modify: `frontend/src/index.css` (entire file — replace current tokens and add new classes)

- [ ] **Step 1: Update CSS tokens and add new design classes**

Replace the `@theme` block and `@layer components` in `index.css` with the following changes:

**`@theme` changes:**
```css
@theme {
  /* Add amber secondary accent */
  --color-amber: #d97706;
  --color-amber-hover: #b45309;
  --color-amber-subtle: #fef3c7;
  --color-amber-subtle-dark: #451a03;

  /* Keep all existing color tokens ... */
  --color-background: #f6f8fb;
  --color-background-dark: #050a12;  /* deeper dark */
  /* ... rest unchanged ... */
}
```

**Background changes in `@layer base`:**
- Change `--color-background-dark` from `#0b1220` to `#050a12`
- Replace the grid-line background with a **dot grid** pattern:

```css
body {
  background:
    radial-gradient(circle, rgba(37, 99, 235, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 18% 0%, rgba(14, 165, 233, 0.12), transparent 34rem),
    radial-gradient(circle at 92% 14%, rgba(99, 102, 241, 0.08), transparent 30rem),
    var(--color-background);
  background-size: 24px 24px, auto, auto, auto;
  /* ... rest unchanged */
}

.dark body {
  background:
    radial-gradient(circle, rgba(96, 165, 250, 0.06) 1px, transparent 1px),
    radial-gradient(circle at 18% 0%, rgba(37, 99, 235, 0.15), transparent 34rem),
    radial-gradient(circle at 92% 14%, rgba(99, 102, 241, 0.12), transparent 30rem),
    var(--color-background-dark);
  background-size: 24px 24px, auto, auto, auto;
}
```

**New CSS classes to add in `@layer components`:**

```css
/* Section number label — large monospace number */
.lab-number {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 3rem;
  font-weight: 700;
  color: rgba(100, 116, 139, 0.12);
  line-height: 1;
  user-select: none;
  letter-spacing: -0.02em;
}

.dark .lab-number {
  color: rgba(100, 116, 139, 0.08);
}

/* Section header with number prefix */
.section-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.section-header .section-number {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 0.73rem;
  font-weight: 800;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 760;
  color: inherit;
}

/* Card with top accent line */
.lab-card {
  position: relative;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.lab-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--color-accent-start), var(--color-accent-mid));
  z-index: 1;
}

.dark .lab-card {
  border-color: var(--color-border-dark);
  background: rgba(17, 24, 39, 0.88);
}

/* Status dot */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 9999px;
}

.status-dot--active {
  background: var(--color-success);
  box-shadow: 0 0 0 3px rgba(15, 159, 110, 0.2);
  animation: status-pulse 2s ease-in-out infinite;
}

.status-dot--testing {
  background: var(--color-amber);
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.2);
}

.status-dot--archived {
  background: var(--color-text-muted);
}

@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(15, 159, 110, 0.2); }
  50% { box-shadow: 0 0 0 6px rgba(15, 159, 110, 0.1); }
}

/* Tick divider — ruler-style separator */
.tick-divider {
  position: relative;
  height: 16px;
  margin: 2rem 0;
  border: none;
  background: repeating-linear-gradient(
    90deg,
    var(--color-border) 0,
    var(--color-border) 1px,
    transparent 1px,
    transparent 8px
  );
  opacity: 0.5;
}

.dark .tick-divider {
  background: repeating-linear-gradient(
    90deg,
    var(--color-border-dark) 0,
    var(--color-border-dark) 1px,
    transparent 1px,
    transparent 8px
  );
}

.tick-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--color-border);
  transform: translateY(-50%);
}

.dark .tick-divider::before {
  background: var(--color-border-dark);
}

/* Lab note block — monospace aside/note */
.lab-note {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 0.85rem;
  border-left: 3px solid var(--color-amber);
  border-radius: 0 8px 8px 0;
  background: rgba(254, 243, 199, 0.5);
  padding: 1rem 1.25rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.dark .lab-note {
  background: rgba(69, 26, 3, 0.3);
  border-color: var(--color-amber);
  color: var(--color-text-secondary-dark);
}

/* Signature quote block */
.signature-block {
  text-align: center;
  padding: 4rem 2rem;
  border-top: 1px solid var(--color-border);
}

.dark .signature-block {
  border-color: var(--color-border-dark);
}

.signature-block blockquote {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  max-width: 32rem;
  margin: 0 auto 1.5rem;
  line-height: 1.4;
}

.dark .signature-block blockquote {
  color: var(--color-text-primary-dark);
}

.signature-block .signature {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.dark .signature-block .signature {
  color: var(--color-text-muted-dark);
}

/* Mouse spotlight effect container */
.spotlight-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.spotlight {
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.06) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  transition: left 0.15s ease-out, top 0.15s ease-out;
}

/* Typewriter text animation */
.typewriter-char {
  display: inline-block;
  opacity: 0;
  animation: typewriter-reveal 0.05s ease-out forwards;
}

@keyframes typewriter-reveal {
  to { opacity: 1; }
}

/* Updated heading sizes */
h1 { font-size: 3.5rem; font-weight: 800; line-height: 1.08; }
h2 { font-size: 2.25rem; font-weight: 760; line-height: 1.15; }
h3 { font-size: 1.5rem; font-weight: 740; line-height: 1.25; }

/* Updated body text */
p {
  line-height: 1.82;
}

@media (min-width: 640px) {
  h1 { font-size: 4rem; }
}
```

**Keep all existing classes unchanged:** `.site-texture`, `.hero-overlay`, `.hero-label`, `.hero-button`, `.hero-button-outline`, `.paper-panel`, `.paper-panel-strong`, `.lab-button`, `.lab-button-secondary`, `.section-label`, `.text-gradient`, `.card-glow`, `.focus-ring`, `.markdown-body`/`.prose` rules, and all their dark mode variants.

- [ ] **Step 2: Verify build succeeds**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/index.css
git commit -m "feat: add lab notebook design tokens and CSS classes"
```

---

### Task 2: New UI Primitive Components

**Files:**
- Create: `frontend/src/components/ui/SectionNumber.tsx`
- Create: `frontend/src/components/ui/StatusDot.tsx`
- Create: `frontend/src/components/ui/TickDivider.tsx`
- Modify: `frontend/src/components/ui/GlassPanel.tsx` — add top accent line + larger radius

- [ ] **Step 1: Create SectionNumber component**

```tsx
// frontend/src/components/ui/SectionNumber.tsx
interface SectionNumberProps {
  number: string; // e.g., "001"
  label: string;  // e.g., "首页"
}

export default function SectionNumber({ number, label }: SectionNumberProps) {
  return (
    <div className="flex items-baseline gap-3">
      <span className="lab-number" aria-hidden="true">
        {number}
      </span>
      <span className="text-lg font-semibold text-text-muted dark:text-text-muted-dark">
        {label}
      </span>
    </div>
  );
}
```

- [ ] **Step 2: Create StatusDot component**

```tsx
// frontend/src/components/ui/StatusDot.tsx
interface StatusDotProps {
  status: string;
  showLabel?: boolean;
}

const statusMap: Record<string, { className: string; label: string }> = {
  published: { className: 'status-dot--active', label: '已发布' },
  active: { className: 'status-dot--active', label: '运行中' },
  testing: { className: 'status-dot--testing', label: '测试中' },
  beta: { className: 'status-dot--testing', label: 'Beta' },
  draft: { className: 'status-dot--archived', label: '草稿' },
  archived: { className: 'status-dot--archived', label: '归档' },
};

export default function StatusDot({ status, showLabel = true }: StatusDotProps) {
  const config = statusMap[status] ?? statusMap.archived;
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`status-dot ${config.className}`} />
      {showLabel && (
        <span className="text-xs font-bold text-text-muted dark:text-text-muted-dark">
          {config.label}
        </span>
      )}
    </span>
  );
}
```

- [ ] **Step 3: Create TickDivider component**

```tsx
// frontend/src/components/ui/TickDivider.tsx
interface TickDividerProps {
  className?: string;
}

export default function TickDivider({ className = '' }: TickDividerProps) {
  return (
    <hr className={`tick-divider ${className}`} />
  );
}
```

- [ ] **Step 4: Update GlassPanel with top accent line and larger radius**

```tsx
// frontend/src/components/ui/GlassPanel.tsx
interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  accentLine?: boolean; // when true, add gradient top accent line
}

export default function GlassPanel({ children, className = '', accentLine = false }: GlassPanelProps) {
  return (
    <div
      className={`relative rounded-xl border border-white/20 bg-white/60 shadow-[0_8px_32px_rgba(37,99,235,0.08)] backdrop-blur-xl overflow-hidden ${className}`}
    >
      {accentLine && (
        <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-accent-start to-accent-mid" />
      )}
      {children}
    </div>
  );
}
```

Note: Changed `rounded-2xl` to `rounded-xl` (12px) for consistency.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ui/SectionNumber.tsx frontend/src/components/ui/StatusDot.tsx frontend/src/components/ui/TickDivider.tsx frontend/src/components/ui/GlassPanel.tsx
git commit -m "feat: add lab notebook UI primitives (SectionNumber, StatusDot, TickDivider, updated GlassPanel)"
```

---

### Task 3: Header — Numbered Navigation

**Files:**
- Modify: `frontend/src/components/layout/Header.tsx` (lines 7-12, 57-77, 113-127)

- [ ] **Step 1: Update navLinks with numbering and modify Header**

Replace the `navLinks` array:

```tsx
const navLinks = [
  { to: '/', label: '首页', number: '01' },
  { to: '/blog', label: '笔记', number: '02' },
  { to: '/products', label: '作品', number: '03' },
  { to: '/about', label: '关于', number: '04' },
];
```

Replace the desktop nav section (lines 57-77):

```tsx
<nav className="hidden items-center gap-1 md:flex" aria-label="主导航">
  {navLinks.map((link) => (
    <Link
      key={link.to}
      to={link.to}
      className={`relative rounded-lg px-3.5 py-2 text-sm font-bold transition-colors ${
        isActive(link.to)
          ? 'text-text-primary dark:text-text-primary-dark'
          : 'text-text-muted hover:text-text-primary dark:text-text-muted-dark dark:hover:text-text-primary-dark'
      }`}
    >
      <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
        {link.number}
      </span>
      {link.label}
      {isActive(link.to) && (
        <motion.span
          layoutId="nav-marker"
          className="absolute inset-x-3 bottom-1 h-0.5 rounded-full bg-accent"
          transition={{ type: 'spring', stiffness: 420, damping: 34 }}
        />
      )}
    </Link>
  ))}
</nav>
```

Replace the mobile nav links section (lines 113-127):

```tsx
<div className="mx-auto max-w-7xl space-y-1 px-4 py-4">
  {navLinks.map((link) => (
    <Link
      key={link.to}
      to={link.to}
      onClick={() => setMobileOpen(false)}
      className={`block rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
        isActive(link.to)
          ? 'bg-accent-subtle text-accent-hover dark:bg-accent-subtle-dark dark:text-text-primary-dark'
          : 'text-text-muted hover:bg-paper dark:text-text-muted-dark dark:hover:bg-surface-dark'
      }`}
    >
      <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
        {link.number}
      </span>
      {link.label}
    </Link>
  ))}
</div>
```

- [ ] **Step 2: Verify build and visual appearance**

Run: `cd frontend && npm run dev`
Check: Nav links show "01 首页", "02 笔记", "03 作品", "04 关于" format

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/Header.tsx
git commit -m "feat: add numbered navigation links (01-04)"
```

---

### Task 4: Footer — Two-Column Layout with Signature

**Files:**
- Modify: `frontend/src/components/layout/Layout.tsx` (lines 45-76, add footerLinks numbering)

- [ ] **Step 1: Update footerLinks with numbering**

Replace the `footerLinks` array:

```tsx
const footerLinks = [
  { to: '/', label: '首页', number: '01' },
  { to: '/blog', label: '笔记', number: '02' },
  { to: '/products', label: '作品', number: '03' },
  { to: '/about', label: '关于', number: '04' },
];
```

- [ ] **Step 2: Replace the footer section**

Replace lines 45-76 with:

```tsx
{!isProductRuntimePage && <footer className="relative z-10 border-t border-border bg-paper/72 backdrop-blur-xl dark:border-border-dark dark:bg-surface-dark/72">
  <div className="mx-auto grid max-w-7xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_1fr] lg:px-8">
    <div>
      <BrandMark />
      <p className="mt-4 text-sm text-text-muted dark:text-text-muted-dark max-w-sm">
        写下实验、系统和那些慢慢成形的想法。
      </p>
    </div>

    <div>
      <h2 className="section-label mb-4">Navigation</h2>
      <div className="grid gap-2">
        {footerLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="text-sm font-semibold text-text-secondary transition-colors hover:text-accent dark:text-text-secondary-dark dark:hover:text-text-primary-dark"
          >
            <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
              {link.number}
            </span>
            {link.label}
          </Link>
        ))}
      </div>
    </div>
  </div>

  <div className="border-t border-border/70 dark:border-border-dark/70">
    <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-5 text-sm text-text-muted dark:text-text-muted-dark sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
      <p>&copy; {new Date().getFullYear()} August&apos;s Lab. Built with curiosity and caffeine.</p>
      <div className="flex gap-4">
        <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="font-semibold hover:text-accent">
          GitHub
        </a>
        <a href="mailto:hello@example.com" className="font-semibold hover:text-accent">
          Email
        </a>
      </div>
    </div>
  </div>
</footer>}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Layout.tsx
git commit -m "feat: redesign footer with two-column layout and signature"
```

---

### Task 5: ArticleCard — Experiment Number Format

**Files:**
- Modify: `frontend/src/components/articles/ArticleCard.tsx` (full rewrite)

- [ ] **Step 1: Rewrite ArticleCard with experiment number format**

```tsx
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';

interface ArticleCardProps {
  article: ArticleListItem;
  variant?: 'default' | 'featured' | 'compact';
  index?: number; // for experiment numbering
}

export default function ArticleCard({ article, variant = 'default', index }: ArticleCardProps) {
  const isFeatured = variant === 'featured';
  const isCompact = variant === 'compact';
  const readingTime = estimateReadingTime(`${article.title} ${article.summary}`);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';
  const expNumber = index != null ? String(index + 1).padStart(2, '0') : '';

  // Compact variant: text-only with number column
  if (isCompact) {
    return (
      <Link to={`/articles/${article.slug}`} className="group block rounded-xl focus-ring">
        <motion.div
          whileHover={{ y: -2 }}
          className="flex gap-4 rounded-xl border border-border/80 bg-paper/88 p-4 shadow-sm transition-colors group-hover:border-accent/30 dark:border-border-dark/80 dark:bg-surface-dark/88"
        >
          {expNumber && (
            <span className="hidden sm:block font-mono text-2xl font-bold text-text-muted/15 dark:text-text-muted-dark/10 leading-none pt-1">
              {expNumber}
            </span>
          )}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 text-xs font-bold text-text-muted dark:text-text-muted-dark">
              <span>{formatDate(article.created_at) || '未标注日期'}</span>
              <span aria-hidden="true">·</span>
              <span>{readingTime} min</span>
            </div>
            <h3 className="mt-1 text-lg font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark truncate">
              {article.title}
            </h3>
            <p className="mt-1 line-clamp-2 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
              {article.summary}
            </p>
            {article.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {article.tags.slice(0, 3).map((tag) => (
                  <span key={tag.id} className="lab-chip text-[10px] px-1.5 py-0.5">
                    #{tag.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </Link>
    );
  }

  // Featured / Default variant
  return (
    <Link to={`/articles/${article.slug}`} className="group block rounded-xl focus-ring">
      <motion.div
        whileHover={{ boxShadow: '0 18px 45px rgba(37,99,235,0.11)' }}
        className={`lab-card overflow-hidden ${
          isFeatured ? 'grid gap-0 md:grid-cols-[0.9fr_1.1fr]' : 'grid gap-0 sm:grid-cols-[13rem_1fr]'
        }`}
      >
        <div className={`${isFeatured ? 'min-h-[16rem]' : 'min-h-[11rem]'} relative overflow-hidden bg-paper-soft dark:bg-background-dark`}>
          <img
            src={cover}
            alt={article.cover_image ? article.title : ''}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
            aria-hidden={!article.cover_image}
          />
        </div>

        <div className={`${isFeatured ? 'p-7 sm:p-8' : 'p-5 sm:p-6'} flex min-w-0 flex-col justify-between`}>
          <div>
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs font-bold text-text-muted dark:text-text-muted-dark">
              {expNumber && (
                <span className="font-mono text-[10px] text-accent/70 dark:text-accent/50">
                  EXP-{expNumber}
                </span>
              )}
              <span>{formatDate(article.created_at) || '未标注日期'}</span>
              <span aria-hidden="true">·</span>
              <span>{readingTime} min read</span>
            </div>
            <h2 className={`${isFeatured ? 'text-2xl sm:text-3xl' : 'text-xl'} font-extrabold leading-tight text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark`}>
              {article.title}
            </h2>
            <p className="mt-3 line-clamp-3 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
              {article.summary}
            </p>
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-border/80 pt-4 dark:border-border-dark/80">
            <div className="flex flex-wrap gap-2">
              {article.tags.slice(0, 3).map((tag) => (
                <span key={tag.id} className="lab-chip">
                  #{tag.name}
                </span>
              ))}
            </div>
            <span className="text-sm font-bold text-accent">阅读</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
```

Key changes:
- Added `variant="compact"` for blog page text-only listings
- Added `index` prop for experiment numbering
- Uses `.lab-card` class (top accent line)
- Shows "EXP-XX" badge in metadata row
- Removed TiltCard wrapper (too heavy for editorial layout)

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/articles/ArticleCard.tsx
git commit -m "feat: redesign ArticleCard with experiment numbering and compact variant"
```

---

### Task 6: HomePage — Editorial Split Layout

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx` (full rewrite of layout structure)

- [ ] **Step 1: Rewrite HomePage with editorial layout**

Replace the entire HomePage component. Key structural changes:

**Hero section — split layout:**
```tsx
export default function HomePage() {
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0.7]);
  const heroY = useTransform(scrollY, [0, 300], [0, -40]);

  const { data: articles, loading } = useArticles(1, 5);
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((data) => setProducts(data.slice(0, 3)))
      .catch(() => {})
      .finally(() => setProductsLoading(false));
  }, []);

  return (
    <div className="space-y-24">
      {/* Hero — split layout */}
      <motion.section
        style={{ opacity: heroOpacity, y: heroY }}
        className="relative -mx-4 min-h-[75vh] overflow-hidden rounded-lg sm:-mx-6 lg:-mx-8"
      >
        {/* Dot grid + halos background */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-clay/5" />

        {/* Content — split */}
        <div className="relative z-10 mx-auto flex max-w-7xl flex-col gap-10 px-6 py-16 lg:flex-row lg:items-center lg:px-8 lg:py-24">
          {/* Left: title + CTA */}
          <div className="flex-1 space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <SectionNumber number="001" label="首页" />
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl"
            >
              写下实验、系统和<br />
              <span className="text-gradient">那些慢慢成形的想法</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.42, duration: 0.6 }}
              className="max-w-md text-base leading-7 text-text-secondary dark:text-text-secondary-dark"
            >
              一个记录技术探索、产品实践和长期思考的个人空间。
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55, duration: 0.6 }}
              className="flex flex-wrap gap-3"
            >
              <Link to="/blog" className="lab-button">
                阅读笔记 <span aria-hidden="true">→</span>
              </Link>
              <Link to="/products" className="lab-button-secondary">
                查看作品
              </Link>
            </motion.div>
          </div>

          {/* Right: margin notes (glass panels) */}
          <div className="flex flex-col gap-4 lg:w-96">
            {/* Code preview card */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotate: -2 }}
              animate={{ opacity: 1, x: 0, rotate: -2 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-3 flex items-center gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-red-400/70" />
                  <div className="h-2 w-2 rounded-full bg-yellow-400/70" />
                  <div className="h-2 w-2 rounded-full bg-green-400/70" />
                </div>
                <div className="space-y-2 font-mono text-[10px] text-text-muted dark:text-text-muted-dark">
                  <div className="flex gap-2"><div className="w-5 h-2 rounded-full bg-clay/40" /><div className="flex-1 h-2 rounded-full bg-border/60" /></div>
                  <div className="ml-3 flex gap-2"><div className="w-3 h-2 rounded-full bg-accent/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                  <div className="ml-3 flex gap-2"><div className="w-7 h-2 rounded-full bg-blueprint/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                </div>
              </GlassPanel>
            </motion.div>

            {/* Tags card */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotate: 2 }}
              animate={{ opacity: 1, x: 0, rotate: 2 }}
              transition={{ delay: 1, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-2 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">最近标签</div>
                <div className="flex flex-wrap gap-1.5">
                  <span className="lab-chip text-[10px]">#React</span>
                  <span className="lab-chip text-[10px]">#API</span>
                  <span className="lab-chip text-[10px]">#CSS</span>
                  <span className="lab-chip text-[10px]">#Rust</span>
                </div>
              </GlassPanel>
            </motion.div>

            {/* Activity bar */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-2 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">活跃度</div>
                <div className="flex items-end gap-1 h-10">
                  {[3, 5, 2, 7, 4, 6, 3].map((h, i) => (
                    <motion.div
                      key={i}
                      className="w-2.5 rounded-sm bg-accent/20"
                      style={{ height: h * 5 }}
                      animate={{ scaleY: [1, 1.4, 0.8, 1.2, 1] }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: i * 0.2 }}
                    />
                  ))}
                </div>
              </GlassPanel>
            </motion.div>
          </div>
        </div>

        {/* Tick divider at bottom */}
        <div className="absolute bottom-0 left-0 right-0 px-8">
          <TickDivider />
        </div>
      </motion.section>

      {/* Latest articles — editorial grid */}
      <section>
        <div className="mb-8">
          <SectionNumber number="002" label="最新笔记" />
        </div>

        {loading ? (
          <div className="space-y-5">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-44" />
            ))}
          </div>
        ) : articles?.items.length ? (
          <div className="space-y-6">
            {/* Featured + second article side by side */}
            <div className="grid gap-6 md:grid-cols-[1fr_auto]">
              <ArticleCard article={articles.items[0]} variant="featured" index={0} />
              {articles.items[1] && (
                <ArticleCard article={articles.items[1]} variant="default" index={1} />
              )}
            </div>

            {/* Compact cards row */}
            {articles.items.length > 2 && (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {articles.items.slice(2).map((article, i) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    variant="compact"
                    index={i + 2}
                  />
                ))}
              </div>
            )}

            <Link to="/blog" className="lab-button-secondary w-fit mx-auto block">
              查看全部文章 <span aria-hidden="true">→</span>
            </Link>
          </div>
        ) : (
          <EmptyState title="暂无文章" />
        )}
      </section>

      {/* Products — showcase */}
      <section>
        <div className="mb-8">
          <SectionNumber number="003" label="作品" />
        </div>

        {productsLoading ? (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-72" />
            ))}
          </div>
        ) : products.length ? (
          <motion.div
            variants={gridVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="space-y-6"
          >
            {products.map((product, i) => (
              <motion.div key={product.id} variants={itemVariants}>
                <Link to={`/products/${product.slug}`} className="group block h-full rounded-xl focus-ring">
                  <article className="lab-card flex h-full flex-col overflow-hidden transition-colors group-hover:border-accent/30">
                    <div className="relative aspect-[4/3] overflow-hidden bg-paper-soft dark:bg-background-dark">
                      <img
                        src={product.cover_image || '/images/brand/fallback-product.webp'}
                        alt={product.cover_image ? product.title : ''}
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                        aria-hidden={!product.cover_image}
                      />
                      <div className="absolute right-3 top-3">
                        <StatusDot status={product.status} showLabel={false} />
                      </div>
                    </div>
                    <div className="flex flex-1 flex-col p-5">
                      <h3 className="text-xl font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                        {product.title}
                      </h3>
                      {product.description && (
                        <p className="mt-3 line-clamp-3 flex-1 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
                          {product.description}
                        </p>
                      )}
                      <div className="mt-5 border-t border-border pt-4 text-sm font-bold text-accent dark:border-border-dark">
                        查看 <span aria-hidden="true">→</span>
                      </div>
                    </div>
                  </article>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <EmptyState title="暂无作品" />
        )}
      </section>

      {/* Signature block */}
      <section className="signature-block">
        <blockquote>
          好的代码像好的实验——<br />每一步都值得重复。
        </blockquote>
        <p className="signature">── august ──</p>
        <div className="mt-6 flex justify-center gap-6">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-text-muted hover:text-accent dark:text-text-muted-dark dark:hover:text-accent transition-colors">
            GitHub
          </a>
          <a href="mailto:hello@example.com" className="text-sm font-semibold text-text-muted hover:text-accent dark:text-text-muted-dark dark:hover:text-accent transition-colors">
            Email
          </a>
        </div>
      </section>
    </div>
  );
}
```

Also update the imports at the top:

```tsx
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';
import TickDivider from '../components/ui/TickDivider';
import StatusDot from '../components/ui/StatusDot';
```

Remove unused imports: `TiltCard`, `StatusBadge`, `motion` gridVariants/itemVariants are still used for products.

- [ ] **Step 2: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/HomePage.tsx
git commit -m "feat: redesign HomePage with editorial split layout and signature block"
```

---

### Task 7: BlogPage — Experiment Log Index Format

**Files:**
- Modify: `frontend/src/pages/BlogPage.tsx` (full rewrite of list format)

- [ ] **Step 1: Rewrite BlogPage with experiment number format**

Replace the article list rendering section. The key changes:
- First article uses `variant="featured"`, rest use `variant="compact"`
- Section title uses `SectionNumber`
- Tag list in sidebar retitled

Replace the entire BlogPage component:

```tsx
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticles } from '../hooks/useArticles';
import { useTags } from '../hooks/useTags';
import ArticleCard from '../components/articles/ArticleCard';
import TagList from '../components/tags/TagList';
import SearchBar from '../components/search/SearchBar';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import PageIntro from '../components/ui/PageIntro';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] as const } },
};

export default function BlogPage() {
  const [searchParams] = useSearchParams();
  const tag = searchParams.get('tag') || undefined;
  const search = searchParams.get('search') || undefined;
  const filterKey = `${tag ?? ''}${search ?? ''}`;
  const [pageState, setPageState] = useState({ key: filterKey, page: 1 });
  const page = pageState.key === filterKey ? pageState.page : 1;

  const { data, loading, error } = useArticles(page, 10, tag, search);
  const { data: tags, loading: tagsLoading } = useTags();

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;
  const title = tag ? `#${tag}` : search ? `搜索：${search}` : '实验笔记目录';

  return (
    <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_18rem]">
      <div className="min-w-0">
        <GlassPanel className="mb-8 p-6" accentLine>
          <PageIntro eyebrow="Notebook" title={title}>
            {data && !tag && !search && (
              <span className="lab-chip">{data.total} 篇公开笔记</span>
            )}
          </PageIntro>
        </GlassPanel>

        <div className="mb-8 flex flex-col gap-4 border-y border-border py-5 dark:border-border-dark sm:flex-row sm:items-center sm:justify-between">
          <SearchBar />
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger dark:bg-danger-subtle-dark"
          >
            {error}
          </motion.div>
        )}

        {loading ? (
          <div className="space-y-5">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-44" />
            ))}
          </div>
        ) : data?.items.length ? (
          <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-4">
            {data.items.map((article, index) => (
              <motion.div key={article.id} variants={itemVariants}>
                <ArticleCard
                  article={article}
                  variant={page === 1 && index === 0 ? 'featured' : 'compact'}
                  index={(page - 1) * data.page_size + index}
                />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <EmptyState title="没有找到文章" />
        )}

        {data && data.total > data.page_size && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <motion.button
              onClick={() => setPageState({ key: filterKey, page: Math.max(1, page - 1) })}
              disabled={page === 1}
              whileTap={{ scale: page === 1 ? 1 : 0.96 }}
              className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-45"
            >
              上一页
            </motion.button>
            <span className="font-mono text-sm font-bold text-text-muted dark:text-text-muted-dark">
              {data.page} / {totalPages}
            </span>
            <motion.button
              onClick={() => setPageState({ key: filterKey, page: page + 1 })}
              disabled={page * data.page_size >= data.total}
              whileTap={{ scale: page * data.page_size >= data.total ? 1 : 0.96 }}
              className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-45"
            >
              下一页
            </motion.button>
          </motion.div>
        )}
      </div>

      <aside className="lg:pt-8">
        <div className="sticky top-24 space-y-6">
          <GlassPanel className="p-5" accentLine>
            <SectionNumber number="" label="主题标签" />
            <div className="mt-4">
              <TagList tags={tags} loading={tagsLoading} />
            </div>
          </GlassPanel>
        </div>
      </aside>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/BlogPage.tsx
git commit -m "feat: redesign BlogPage with experiment number format and compact cards"
```

---

### Task 8: ArticlePage — Metadata Row + Enhanced Code Blocks

**Files:**
- Modify: `frontend/src/pages/ArticlePage.tsx` (lines 25-75)

- [ ] **Step 1: Rewrite ArticlePage with metadata row and code block styling**

```tsx
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticle } from '../hooks/useArticles';
import { useSeoMeta } from '../hooks/useSeoMeta';
import ArticleContent from '../components/articles/ArticleContent';
import { formatDate } from '../utils/formatDate';
import { estimateReadingTime } from '../utils/readingTime';
import EmptyState from '../components/ui/EmptyState';
import GlassPanel from '../components/ui/GlassPanel';

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data: article, loading, error } = useArticle(slug!);

  useSeoMeta(article);

  if (loading) return <EmptyState title="文章加载中" />;
  if (error) return <EmptyState title="文章读取失败" description={error} />;
  if (!article) return <EmptyState title="文章不存在" />;

  const readingTime = estimateReadingTime(article.content || article.summary);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';

  return (
    <article className="mx-auto max-w-5xl">
      <motion.button
        onClick={() => navigate(-1)}
        whileHover={{ x: -3 }}
        className="mb-6 inline-flex items-center gap-2 text-sm font-bold text-text-muted transition-colors hover:text-accent dark:text-text-muted-dark"
      >
        <span aria-hidden="true">←</span>
        返回上一页
      </motion.button>

      {/* Article number */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-mono text-sm text-text-muted/50 dark:text-text-muted-dark/30 mb-4"
      >
        EXP-{String(article.id).padStart(4, '0')}
      </motion.p>

      <motion.header
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl">
          {article.title}
        </h1>
        <p className="mt-6 max-w-3xl text-lg leading-9 text-text-secondary dark:text-text-secondary-dark">
          {article.summary}
        </p>

        {/* Metadata row */}
        <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 border-y border-border py-4 text-sm font-bold text-text-muted dark:border-border-dark dark:text-text-muted-dark">
          <span>{formatDate(article.created_at) || '未标注日期'}</span>
          <span aria-hidden="true" className="text-border dark:text-border-dark">·</span>
          <span>{readingTime} min read</span>
          <span aria-hidden="true" className="text-border dark:text-border-dark">·</span>
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <Link key={tag.id} to={`/blog?tag=${encodeURIComponent(tag.name)}`} className="lab-chip text-[10px] px-1.5 py-0.5">
                #{tag.name}
              </Link>
            ))}
          </div>
        </div>
      </motion.header>

      {/* Cover image */}
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.04 }}
        className="mb-8"
      >
        <GlassPanel accentLine className="overflow-hidden">
          <img src={cover} alt={article.cover_image ? article.title : ''} className="aspect-[16/9] w-full object-cover" aria-hidden={!article.cover_image} />
        </GlassPanel>
      </motion.div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
      >
        <GlassPanel accentLine className="px-5 py-7 sm:px-9 sm:py-10">
          <ArticleContent content={article.content} />
        </GlassPanel>
      </motion.div>
    </article>
  );
}
```

Key changes:
- Added "EXP-XXXX" article number
- Changed cover image aspect ratio from 4:3 to 16:9 (more cinematic)
- Moved tags into the metadata row instead of above title
- Added accentLine to GlassPanel

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/ArticlePage.tsx
git commit -m "feat: redesign ArticlePage with EXP number and metadata row"
```

---

### Task 9: ProductsPage — Featured Product + Status Dots

**Files:**
- Modify: `frontend/src/pages/ProductsPage.tsx` (full rewrite)

- [ ] **Step 1: Rewrite ProductsPage with featured product**

```tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import PageIntro from '../components/ui/PageIntro';
import EmptyState from '../components/ui/EmptyState';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';
import StatusDot from '../components/ui/StatusDot';

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const } },
};

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((err) => setError(err.response?.data?.detail || '加载失败'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-10">
      <section>
        <PageIntro
          eyebrow="Products"
          title="作品"
          description="从小工具到完整产品，每个都经过反复打磨"
        />
      </section>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger dark:bg-danger-subtle-dark"
        >
          {error}
        </motion.div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-80" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState title="暂无作品" />
      ) : (
        <div className="space-y-6">
          {/* Featured product (first) — full-width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Link to={`/products/${products[0].slug}`} className="group block rounded-xl focus-ring">
              <article className="lab-card grid gap-0 overflow-hidden md:grid-cols-[1.2fr_1fr]">
                <div className="relative aspect-[16/10] overflow-hidden bg-paper-soft dark:bg-background-dark md:min-h-[20rem]">
                  <img
                    src={products[0].cover_image || '/images/brand/fallback-product.webp'}
                    alt={products[0].cover_image ? products[0].title : ''}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
                    aria-hidden={!products[0].cover_image}
                  />
                  <div className="absolute right-3 top-3">
                    <StatusDot status={products[0].status} />
                  </div>
                </div>
                <div className="flex flex-col justify-center p-6 sm:p-8">
                  <h2 className="text-2xl font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                    {products[0].title}
                  </h2>
                  {products[0].description && (
                    <p className="mt-4 line-clamp-4 text-base leading-7 text-text-secondary dark:text-text-secondary-dark">
                      {products[0].description}
                    </p>
                  )}
                  <div className="mt-6 flex items-center gap-2 text-sm font-bold text-accent">
                    <span>打开作品</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                    >
                      →
                    </motion.span>
                  </div>
                </div>
              </article>
            </Link>
          </motion.div>

          {/* Remaining products — grid */}
          {products.length > 1 && (
            <motion.div
              variants={gridVariants}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
            >
              {products.slice(1).map((product) => (
                <motion.div key={product.id} variants={itemVariants}>
                  <Link to={`/products/${product.slug}`} className="group block h-full rounded-xl focus-ring">
                    <article className="lab-card flex h-full flex-col overflow-hidden transition-colors group-hover:border-accent/30">
                      <div className="relative aspect-[4/3] overflow-hidden bg-paper-soft dark:bg-background-dark">
                        <img
                          src={product.cover_image || '/images/brand/fallback-product.webp'}
                          alt={product.cover_image ? product.title : ''}
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                          aria-hidden={!product.cover_image}
                        />
                        <div className="absolute right-3 top-3">
                          <StatusDot status={product.status} />
                        </div>
                      </div>
                      <div className="flex flex-1 flex-col p-5">
                        <h3 className="text-lg font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                          {product.title}
                        </h3>
                        {product.description && (
                          <p className="mt-2 line-clamp-2 flex-1 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
                            {product.description}
                          </p>
                        )}
                        <div className="mt-4 border-t border-border pt-3 text-sm font-bold text-accent dark:border-border-dark">
                          查看 <span aria-hidden="true">→</span>
                        </div>
                      </div>
                    </article>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
```

Remove unused imports: `StatusBadge`, `TiltCard`

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/ProductsPage.tsx
git commit -m "feat: redesign ProductsPage with featured product and StatusDot"
```

---

### Task 10: AboutPage — Researcher Archive Layout

**Files:**
- Modify: `frontend/src/pages/AboutPage.tsx` (full rewrite of layout)

- [ ] **Step 1: Rewrite AboutPage with researcher archive layout**

```tsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getAbout } from '../api/about';
import type { AboutPage } from '../types';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';
import { Skeleton } from '../components/ui/Skeleton';
import HeroSection from '../components/about/HeroSection';
import InfoCards from '../components/about/InfoCards';
import ContactLinks from '../components/about/ContactLinks';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';

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
      <AnimatedPage className="mx-auto max-w-5xl">
        <motion.div variants={sectionVariants} initial="hidden" animate="visible">
          <p className="py-20 text-center text-text-muted dark:text-text-muted-dark">
            关于页尚未配置，请到后台管理进行设置。
          </p>
        </motion.div>
      </AnimatedPage>
    );
  }

  const techStackList = (() => {
    try {
      if (!about.tech_stack) return [];
      return JSON.parse(about.tech_stack) as string[];
    } catch {
      return [];
    }
  })();

  return (
    <AnimatedPage className="mx-auto max-w-5xl space-y-10">
      {/* Hero */}
      <motion.section variants={sectionVariants} initial="hidden" animate="visible">
        <HeroSection
          avatarUrl={about.avatar_url || undefined}
          eyebrow={about.eyebrow}
          title={about.title}
          heroSubtitle={about.hero_subtitle || undefined}
          coverImage={about.cover_image || undefined}
        />
      </motion.section>

      {/* Info cards */}
      {about.info_cards?.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <InfoCards items={about.info_cards} />
        </motion.section>
      )}

      {/* Tech stack */}
      {techStackList.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel accentLine className="p-6">
            <SectionNumber number="" label="常用技术栈" />
            <div className="mt-4 flex flex-wrap gap-2">
              {techStackList.map((tech) => (
                <span key={tech} className="lab-chip">{tech}</span>
              ))}
            </div>
          </GlassPanel>
        </motion.section>
      )}

      {/* Contact links */}
      {about.contacts?.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel accentLine className="p-6">
            <SectionNumber number="" label="联系方式" />
            <div className="mt-4">
              <ContactLinks contacts={about.contacts} />
            </div>
          </GlassPanel>
        </motion.section>
      )}

      {/* Content (collapsed) */}
      {about.content && about.content.trim() !== '' && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel className="p-6 sm:p-8">
            <details className="group">
              <summary className="cursor-pointer select-none text-lg font-semibold text-text-primary dark:text-text-primary-dark">
                更多介绍
              </summary>
              <div className="mt-4">
                <ArticleContent content={about.content} />
              </div>
            </details>
          </GlassPanel>
        </motion.section>
      )}
    </AnimatedPage>
  );
}
```

Key changes:
- Section headers use `SectionNumber`
- GlassPanel has `accentLine`
- Clean structure, minimal changes to existing components

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/AboutPage.tsx
git commit -m "feat: redesign AboutPage with SectionNumber headers and accent-line panels"
```

---

### Task 11: LoginPage — Minor Lab Number Addition

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`

- [ ] **Step 1: Read current LoginPage**

Read `frontend/src/pages/LoginPage.tsx` to get current content.

- [ ] **Step 2: Add lab number to login page**

Add above the login card title:

```tsx
<p className="font-mono text-xs text-text-muted/40 dark:text-text-muted-dark/25 mb-4 text-center">
  EXP-LOGIN
</p>
```

Keep everything else unchanged.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx
git commit -m "feat: add lab number to login page"
```

---

### Task 12: Build Verification + Final Checks

**Files:**
- All modified files

- [ ] **Step 1: Run full build verification**

```bash
cd frontend && npm run build
```

Expected: Build succeeds with no type errors

- [ ] **Step 2: Run lint**

```bash
cd frontend && npm run lint
```

Expected: No lint errors (warnings OK)

- [ ] **Step 3: Start dev server and visually verify**

```bash
cd frontend && npm run dev
```

Check in browser:
- Homepage: split hero layout, section numbers, editorial article grid, signature block
- Blog page: compact cards with experiment numbers
- Products page: featured product full-width, status dots
- Article page: EXP number, metadata row
- About page: section number headers
- Header: numbered nav links
- Footer: two-column with signature
- Dark mode: deeper background, proper contrast
- Background: dot grid visible

- [ ] **Step 4: Final commit if any adjustments needed**

```bash
git add -A
git commit -m "fix: final polish for lab notebook redesign"
```

---

## Self-Review Checklist

**1. Spec coverage check:**
- ✅ Dot grid background — Task 1 (CSS)
- ✅ Experiment numbering — Task 2 (SectionNumber), Tasks 5-10 (usage)
- ✅ StatusDot — Task 2, used in Tasks 9 (ProductsPage)
- ✅ TickDivider — Task 2, used in Task 6 (HomePage)
- ✅ Lab card with top accent line — Task 1 (CSS), used in Tasks 5-10
- ✅ Section headers with numbers — Task 2 (CSS), Tasks 6-10
- ✅ Hero split layout — Task 6 (HomePage)
- ✅ Editorial article grid — Task 5 (ArticleCard), Tasks 6-7
- ✅ Featured product — Task 9 (ProductsPage)
- ✅ Signature block — Task 6 (HomePage)
- ✅ Numbered nav links — Task 3 (Header)
- ✅ Footer redesign — Task 4 (Layout)
- ✅ Deeper dark background — Task 1 (CSS)
- ✅ Amber accent color — Task 1 (CSS)
- ✅ Lab note block CSS — Task 1 (CSS)
- ✅ Article metadata row — Task 8 (ArticlePage)
- ✅ About page section numbers — Task 10 (AboutPage)
- ✅ GlassPanel accentLine — Task 2 (GlassPanel)
- ✅ Typography size updates — Task 1 (CSS)

**2. Placeholder scan:** No TBD, TODO, or vague instructions. All code blocks contain actual implementation code.

**3. Type consistency:** All components use existing types from `types/index.ts`. `StatusDot` maps `product.status` string to config. `ArticleCard` uses `ArticleListItem`. `SectionNumber` takes string props. All consistent.
