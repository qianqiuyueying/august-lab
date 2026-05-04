# Frontend Design Upgrade — Lab Notebook Brand System

**Date:** 2026-05-04
**Status:** Approved by user
**Scope:** Frontend visual redesign — brand system + editorial layout

---

## 1. Design Language: Lab Notebook

### Core Metaphor
Every visual element serves the "scientific lab notebook" metaphor. No random decorative shapes — every element has a purpose within the lab notebook visual language.

### Visual Identity Elements

| Element | Description |
|---------|-------------|
| **Dot grid background** | Replaces current grid lines with a dot-matrix pattern, like graph paper in a lab notebook |
| **Experiment numbering** | Every section has an "EXP-001" style number in the top-left corner |
| **Scale/tick decorations** | Page edges feature ruler-style tick marks instead of random floating shapes |
| **Microscope spotlight** | Circular gradient halo that follows the mouse cursor — a focused light effect |
| **Amber accent color** | Secondary accent `#d97706` for warnings/notes, complementing the primary blue `#2563eb` |

### Color Token Changes

| Token | Current | New |
|-------|---------|-----|
| Background | `#f6f8fb` flat + grid | Add dot-grid texture overlay |
| Card background | `rgba(255,255,255,0.84)` | Add **top 2px accent line** (gradient from accent-start to accent-mid) |
| Dark mode bg | `#0b1220` | Deeper `#050a12` with star-point effect |
| Secondary accent | None | Amber `#d97706` |

### Animation Changes

- **Keep:** TiltCard 3D tilt, page transitions, scroll parallax, staggered entrance
- **Remove:** Random rotating rings, crosses, floating colored blocks
- **Add:**
  - Card glow scan line on hover (light sweeps from top to bottom of card)
  - Typewriter effect for hero title (characters appear one by one)
  - Scale/tick unfold animation on section scroll-into-view

---

## 2. Component Language

### New Components

#### `.lab-number` (Experiment Number Label)
- Large, light-gray monospace number in the top-left of sections
- Font: `ui-monospace`, size ~3-4rem, weight 700, color `rgba(var(--color-text-muted), 0.15)`
- Format: "001", "002", etc.

#### Status Dot
- Small colored circle (8px diameter) replacing StatusBadge
- Green `#0f9f6e` = active, Yellow `#d97706` = testing/beta, Gray `#64748b` = archived
- With pulse animation for active items

#### Tick Divider
- Section separator styled like a ruler with tick marks
- SVG-based decorative element

#### Lab Chip (Tag Redesign)
- Rounded pill shape with small icon prefix
- Like chemical reagent bottle labels
- Color-coded by category

### Updated Components

#### ArticleCard
- Add left column with experiment number + date (vertical)
- Featured variant has larger cover image
- Standard variant is text-only with small thumbnail
- Top 2px accent line on card border

#### GlassPanel
- Keep backdrop-blur style
- Add subtle top accent line (gradient)
- Slightly larger border-radius (12px from 8px)

#### Header
- Nav links with monospace numbering: `01 Home`, `02 Blog`, `03 Products`, `04 About`
- Active link number highlighted in accent color
- Keep animated nav marker but reduce to thin line

#### Footer
- Two-column: brand info left, numbered navigation right
- Bottom tagline: "Built with curiosity and caffeine"

---

## 3. Page Layouts

### 3.1 HomePage

#### Hero Section — Split Layout
- **Left 60%:** Large title (3.5-4rem), label text, CTA buttons
- **Right 40%:** 2-3 small glass panels (code preview, tags, activity bar) — like margin notes in a lab notebook
- **Bottom:** Scale/tick decoration bar as visual anchor
- **Background:** Dot grid + two large decorative halos
- **"EXP-001"** number in top-left monospace
- TiltCard removed from hero (too large, breaks editorial rhythm)

#### Latest Articles — Editorial Grid
- Section title: "02 / 实验记录"
- Featured article (65% width) with large cover image
- Second article (35% width) as smaller card
- 3 standard cards in a row below
- Last slot is "查看更多 →" button
- Each card has left column with number + date

#### Products — Showcase
- Section title: "03 / 实验成果"
- Featured product (full-width) with large image
- 2 standard product cards below
- Status shown as colored dot

#### Footer Signature (New)
- Full-width quote block with personal signature style
- "好的代码像好的实验——每一步都值得重复。"
- Social links below

### 3.2 BlogPage

- Section title: "02 / 实验记录索引"
- Article list has left number column (#01, #02...)
- First article has cover image, rest are text-only
- Tag filters styled as reagent label chips
- Sidebar retitled "实验分类"
- Pagination styled with monospace numbers

### 3.3 ArticlePage

- "EXP-XXXX" article number at top
- Unified metadata row (date · reading time · tags)
- Cover image full-width
- Code blocks styled as terminal windows (rounded + 3 dots + dark bg)
- New "实验备注" section for author's notes — monospace font + special background
- Images have border + caption below

### 3.4 ProductsPage

- Section title: "03 / 实验成果"
- Featured product full-width card
- Standard products in 2-column grid
- Status as colored dot
- Number prefix on each product

### 3.5 AboutPage

- Section title: "04 / 研究员档案"
- Avatar + bio layout
- "实验技能" section with progress bars for skills
- Tech stack as lab chips
- Contact links with icons

### 3.6 Login Page

- Minimal change — keep current design, add lab number "EXP-LOGIN"
- Subtle dot-grid background

---

## 4. Typography System

| Element | Current | New |
|---------|---------|-----|
| h1 | 2.75rem / 800 | 3.5-4rem / 800 |
| h2 | 2rem / 760 | 2.25rem / 760 |
| h3 | 1.45rem / 740 | 1.5rem / 740 |
| Section labels | `0.73rem` uppercase accent | `0.73rem` monospace with number prefix |
| Body text | 15px / 1.7 | 16px / 1.75 |
| Monospace elements | N/A | `ui-monospace, "Cascadia Code"` for numbers, labels, notes |

---

## 5. Implementation Notes

### Files to Modify
- `frontend/src/index.css` — new design tokens, dot-grid texture, component classes
- `frontend/src/pages/HomePage.tsx` — complete rewrite of layout
- `frontend/src/pages/BlogPage.tsx` — new list format
- `frontend/src/pages/ArticlePage.tsx` — metadata row, code block, notes section
- `frontend/src/pages/ProductsPage.tsx` — featured product, status dots
- `frontend/src/pages/AboutPage.tsx` — skills bars, new layout
- `frontend/src/pages/LoginPage.tsx` — minor additions
- `frontend/src/components/layout/Header.tsx` — numbered nav links
- `frontend/src/components/layout/Layout.tsx` — footer signature, dot-grid background
- `frontend/src/components/articles/ArticleCard.tsx` — experiment number column
- `frontend/src/components/ui/` — new: StatusDot, TickDivider, LabChip updates
- `frontend/src/components/ui/GlassPanel.tsx` — top accent line, larger radius

### Dependencies
- Current: `framer-motion` (v12), `react-router-dom` (v7)
- No new dependencies needed — all effects achievable with existing framer-motion + Tailwind

### Performance Considerations
- Dot-grid SVG should be inline (data URI) to avoid extra request
- Typewriter effect uses framer-motion `AnimatePresence` — keep within 50 chars to avoid perf issues
- Mouse spotlight effect should use CSS custom properties + `requestAnimationFrame` — throttle to 60fps
