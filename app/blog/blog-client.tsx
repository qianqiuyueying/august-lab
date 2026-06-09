"use client";
import { useEffect, useRef } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

interface Article {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  coverImage: string;
  tags: string[];
  readingTime: number;
  publishedAt: string | null;
}

interface BlogClientProps {
  articles: Article[];
  allTags: string[];
  archives: { label: string; count: number }[];
}

export function BlogClient({ articles, allTags, archives }: BlogClientProps) {
  const searchParams = useSearchParams();
  const activeTag = searchParams.get("tag") || null;

  const filtered = activeTag
    ? articles.filter((a) => a.tags?.includes(activeTag))
    : articles;

  /* ===== 导航栏滚动 solid ===== */
  const heroRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const nav = document.getElementById("mainNav");
    const hero = heroRef.current;
    if (!nav || !hero) return;

    const updateNav = () => {
      const heroBottom = hero.getBoundingClientRect().bottom;
      nav.classList.toggle("nav-v2--solid", heroBottom < 60);
    };

    window.addEventListener("scroll", updateNav, { passive: true });
    updateNav();
    return () => window.removeEventListener("scroll", updateNav);
  }, []);

  /* ===== Hero 视差 ===== */
  useEffect(() => {
    const heroBg = document.getElementById("heroBg");
    const hero = heroRef.current;
    if (!heroBg || !hero) return;

    const onScroll = () => {
      const scrollY = window.scrollY;
      const heroTop = hero.offsetTop;
      const offset = (scrollY - heroTop) * 0.25;
      heroBg.style.transform = `translateY(${offset}px)`;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* ===== URL 参数状态 ===== */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get("state");
    if (state) document.body.dataset.state = state;
    return () => { document.body.dataset.state = ""; };
  }, []);

  /* ===== 网格排列：首篇全宽图片，其余交替 文本/图片 ===== */
  const renderArticleCard = (a: Article, index: number, isFirst: boolean) => {
    const variant = isFirst
      ? ("article-card--image" as const)
      : index % 2 === 0
        ? ("article-card--image" as const)
        : ("article-card--text" as const);

    const date = a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : "";

    return (
      <Link
        key={a.id}
        href={`/blog/${a.slug}`}
        className={`article-card ${variant}`}
        style={isFirst ? { gridColumn: "1 / -1" } : undefined}
      >
        {variant === "article-card--image" && (
          <div className="article-card__img">
            <img src={a.coverImage || "/uploads/venetian-blind-shadow.png"} alt={a.title} loading="lazy" />
          </div>
        )}
        <div className="article-card__body">
          <div className="article-card__meta">
            <span className="article-card__index">{String(index + 1).padStart(2, "0")}</span>
            <span className="article-card__dot"></span>
            <span>{date}</span>
            <span className="article-card__dot"></span>
            <span>{a.readingTime} 分钟</span>
          </div>
          <h2 className="article-card__title">{a.title}</h2>
          <p className="article-card__excerpt">{a.excerpt}</p>
          <div className="article-card__tags">
            {(a.tags || []).map((t) => (
              <span key={t} className={`tag${activeTag === t ? " tag--active" : ""}`}>{t}</span>
            ))}
          </div>
        </div>
      </Link>
    );
  };

  return (
    <>
      <main className="blog-state-default">
        {/* Hero 视差区 */}
        <header className="blog-hero" ref={heroRef}>
          <div className="blog-hero__bg" id="heroBg">
            <img src="/uploads/paper-folds-shadow.png" alt="折纸几何光影" loading="eager" />
          </div>
          <div className="blog-hero__overlay"></div>
          <div className="blog-hero__spot"></div>
          <div className="blog-hero__content">
            <p className="blog-hero__label">/ 博客</p>
            <h1 className="blog-hero__title">实验笔记</h1>
            <p className="blog-hero__desc">代码实验、设计思考、影像记录</p>
          </div>
        </header>

        {/* 搜索条 */}
        <div className="blog-bar">
          <div className="container">
            <div className="search-box">
              <span className="search-box__icon">⌕</span>
              <input type="text" placeholder="搜索笔记…" />
            </div>
            <span className="blog-bar__count">共 {filtered.length} 篇</span>
          </div>
        </div>

        {/* 杂志式文章列表 */}
        <div className="blog-body">
          <div className="container blog-layout">

            <div className="article-grid">
              {filtered.map((a, i) => renderArticleCard(a, i, i === 0))}
            </div>

            {/* 侧边栏 */}
            <aside className="blog-sidebar">
              <div className="sidebar-card">
                <h3 className="sidebar-card__title">标签</h3>
                <div className="tag-cloud">
                  <Link href="/blog" className={`tag${!activeTag ? " tag--active" : ""}`}>
                    全部
                  </Link>
                  {allTags.map((t) => (
                    <Link
                      key={t}
                      href={`/blog${activeTag === t ? "" : `?tag=${encodeURIComponent(t)}`}`}
                      className={`tag${activeTag === t ? " tag--active" : ""}`}
                    >
                      {t}
                    </Link>
                  ))}
                </div>
              </div>

              <div className="sidebar-card">
                <h3 className="sidebar-card__title">归档</h3>
                <div className="sidebar-archive">
                  {archives.map((arc) => (
                    <span key={arc.label} className="sidebar-archive__item">
                      <span>{arc.label}</span>
                      <span>{arc.count} 篇</span>
                    </span>
                  ))}
                </div>
              </div>
            </aside>

          </div>

          {/* 分页 */}
          <div className="container">
            <div className="pagination">
              <button className="pagination__arrow">←</button>
              <span className="pagination__item pagination__item--active">1</span>
              <span className="pagination__item">2</span>
              <span className="pagination__item">3</span>
              <button className="pagination__arrow">→</button>
            </div>
          </div>
        </div>

      </main>

      {/* 状态 */}
      <div className="state-card blog-state-loading blog-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">加载中</div>
        <p className="state-card__desc">正在获取笔记列表…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>

      <div className="state-card blog-state-error blog-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">加载失败</div>
        <p className="state-card__desc">无法连接到服务器，请稍后重试。</p>
        <button className="btn" style={{ marginTop: "var(--sp-lg)" }} onClick={() => window.location.reload()}>重新加载</button>
      </div>

      <div className="state-card blog-state-empty blog-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">暂无笔记</div>
        <p className="state-card__desc">还没有发表任何文章，敬请期待。</p>
      </div>
    </>
  );
}
