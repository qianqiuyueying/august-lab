"use client";
import { useEffect } from "react";
import Link from "next/link";
import { MarkdownRenderer } from "@/lib/markdown";

interface ArticleClientProps {
  article: {
    slug: string;
    title: string;
    excerpt: string;
    content: string;
    coverImage: string;
    tags: string[];
    readingTime: number;
    publishedAt: string | null;
  };
  prev: { slug: string; title: string } | null;
  next: { slug: string; title: string } | null;
}

export function ArticleClient({ article, prev, next }: ArticleClientProps) {
  const date = article.publishedAt ? new Date(article.publishedAt).toISOString().slice(0, 10) : "";

  /* ===== 导航滚动 solid ===== */
  useEffect(() => {
    const nav = document.getElementById("mainNav");
    const hero = document.querySelector(".article-hero");
    if (!nav || !hero) return;

    const updateNav = () => {
      nav.classList.toggle("nav-v2--solid", hero.getBoundingClientRect().bottom < 60);
    };

    window.addEventListener("scroll", updateNav, { passive: true });
    updateNav();
    return () => window.removeEventListener("scroll", updateNav);
  }, []);

  /* ===== URL 参数状态 ===== */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get("state");
    if (state) document.body.dataset.state = state;
    return () => { document.body.dataset.state = ""; };
  }, []);

  return (
    <>
      {/* 文章专属导航 */}
      <nav className="article-nav">
        <Link href="/blog" className="article-nav__back">← 返回博客</Link>
      </nav>

      <main className="article-state-default">
        {/* Hero */}
        <div className="article-hero">
          <img src={article.coverImage || "/uploads/venetian-blind-shadow.png"} alt={article.title} loading="eager" />
          <div className="photo-hero__overlay"></div>
        </div>

        <article className="article-body">
          <div className="container--narrow">
            <header className="article-header">
              <div className="article-header__meta">
                <span>{date}</span>
                <span className="article-header__dot"></span>
                <span>{article.readingTime} 分钟阅读</span>
              </div>
              <h1 className="article-header__title">{article.title}</h1>
              <p className="article-header__desc">{article.excerpt}</p>
              <div className="article-header__tags">
                {(article.tags || []).map((t) => (
                  <span key={t} className="tag">{t}</span>
                ))}
              </div>
            </header>

            <div className="article-content">
              <MarkdownRenderer content={article.content} />
            </div>

            <footer className="article-footer">
              <div className="article-footer__nav">
                {prev && (
                  <Link href={`/blog/${prev.slug}`} className="article-footer__link">← 上一篇</Link>
                )}
                {!prev && <span className="article-footer__link" style={{ visibility: "hidden" }}>← 上一篇</span>}
                {next && (
                  <Link href={`/blog/${next.slug}`} className="article-footer__link">下一篇 →</Link>
                )}
                {!next && <span className="article-footer__link" style={{ visibility: "hidden" }}>下一篇 →</span>}
              </div>
            </footer>
          </div>
        </article>
      </main>

      {/* 状态 */}
      <div className="state-card article-state-loading article-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">加载中</div>
        <p className="state-card__desc">正在加载文章…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>

      <div className="state-card article-state-error article-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">加载失败</div>
        <p className="state-card__desc">无法获取文章内容。</p>
        <Link href="/blog" className="btn" style={{ marginTop: "var(--sp-lg)" }}>返回博客列表</Link>
      </div>

      <div className="state-card article-state-empty article-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">文章不存在</div>
        <p className="state-card__desc">这篇笔记可能已被删除。</p>
        <Link href="/blog" className="btn" style={{ marginTop: "var(--sp-lg)" }}>返回博客列表</Link>
      </div>
    </>
  );
}
