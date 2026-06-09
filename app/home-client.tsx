"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { Tags } from "@/components/tags";
import { StateCard } from "@/components/state-card";

export function HomeClient({ articles, products }: { articles: any[]; products: any[] }) {
  const [activeSection, setActiveSection] = useState(0);
  const sectionsRef = useRef<(HTMLElement | null)[]>([]);

  const updateScene = useCallback(() => {
    const winH = window.innerHeight;
    let maxVis = 0;
    let newIdx = 0;

    sectionsRef.current.forEach((sec, i) => {
      if (!sec) return;
      const r = sec.getBoundingClientRect();
      const secH = sec.offsetHeight;
      const visibleInView = Math.min(r.bottom, winH) - Math.max(r.top, 0);
      const visibility = Math.max(0, Math.min(1, visibleInView / secH));
      if (visibility > maxVis) { maxVis = visibility; newIdx = i; }

      // 内容动画：戏剧性叠化
      const content = sec.querySelector(".anim-content") as HTMLElement;
      if (content) {
        const raw = Math.max(0, Math.min(1, (visibility - 0.05) / 0.65));
        const eased = raw === 1 ? 1 : 1 - Math.pow(2, -10 * raw);
        content.style.opacity = String(eased);
        content.style.transform = `translateY(${(1 - eased) * 100}px) scale(${0.82 + 0.18 * eased})`;
        content.style.filter = `blur(${14 * (1 - eased)}px)`;
      }

      // 背景视差
      const bg = sec.querySelector(".section__bg") as HTMLElement;
      if (bg) {
        const parallaxSpeed = parseFloat(bg.dataset.parallax || "0.25");
        const offset = r.top * Math.max(parallaxSpeed * 1.6, 0.35);
        bg.style.transform = `translateY(${offset}px)`;
      }

      // 叠化幕布
      const scrim = sec.querySelector(".section__scrim") as HTMLElement;
      if (scrim) {
        const leaving = Math.max(0, Math.min(1, -r.top / secH));
        const entering = Math.max(0, Math.min(1, (r.bottom - winH) / secH));
        scrim.style.opacity = String(Math.max(leaving * 0.92, entering * 0.72));
      }
    });

    setActiveSection(newIdx);
  }, []);

  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => { updateScene(); ticking = false; });
        ticking = true;
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [updateScene]);

  useEffect(() => { updateScene(); }, [updateScene]);

  const sectionImages = [
    "/uploads/lab-hero.webp",
    "/uploads/blog-field-notes.webp",
    "/uploads/products-bench.webp",
    "/uploads/about-workbench.webp",
  ];

  const sections = ["hero", "articles", "works", "quote"];

  return (
    <>
      {/* 右侧导航点 */}
      <nav className="section-nav">
        {sections.map((s, i) => (
          <span
            key={s}
            className={`section-nav__dot${i === activeSection ? " active" : ""}`}
            onClick={() => document.querySelector(`[data-section="${s}"]`)?.scrollIntoView({ behavior: "smooth" })}
          />
        ))}
      </nav>

      <div>
        {/* Section 1: Hero */}
        <section
          ref={(el) => { sectionsRef.current[0] = el; }}
          className="section" data-section="hero"
        >
          <div className="section__bg" data-parallax="0.3">
            <img src={sectionImages[0]} alt="" loading="eager" />
          </div>
          <div className="section__overlay" style={{ background: "linear-gradient(180deg, oklch(0 0 0 / 0.65) 0%, oklch(0 0 0 / 0.3) 35%, oklch(0 0 0 / 0.35) 50%, oklch(0 0 0 / 0.5) 75%, oklch(0 0 0 / 0.7) 100%)" }} />
          <div className="section__spot" />
          <div className="section__scrim" />

          <div className="section__content section__content--center anim-content" style={{ paddingTop: "5vh" }}>
            <p className="hero__label">光影之间</p>
            <h1 className="hero__title">
              August&apos;s
              <span className="thin">Atelier</span>
            </h1>
            <p className="hero__desc">
              用光影与图像驱动的创作空间<br />
              记录灵感、实验与作品
            </p>
          </div>

          <div className="hero__scroll">
            <span>向下探索</span>
            <div className="hero__scroll-line" />
          </div>
        </section>

        {/* Section 2: 最新笔记 */}
        <section ref={(el) => { sectionsRef.current[1] = el; }} className="section" data-section="articles">
          <div className="section__bg" data-parallax="0.3">
            <img src={sectionImages[1]} alt="" loading="lazy" />
          </div>
          <div className="section__overlay" style={{ background: "linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.2) 25%, oklch(0 0 0 / 0.2) 75%, oklch(0 0 0 / 0.55) 100%)" }} />
          <div className="section__spot" />
          <div className="section__scrim" />

          <div className="section__content anim-content">
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="section__number">/ 01</p>
                <h2 className="section__heading">最新笔记</h2>
              </div>
              <Link href="/blog" className="section__link">查看全部 →</Link>
            </div>

            {articles.length === 0 ? (
              <StateCard type="empty" minHeight="200px" />
            ) : (
              <div className="articles-grid">
                {articles.map((a, i) => (
                  <Link key={a.id} href={`/blog/${a.slug}`} className="articles-card-hover"
                    style={{
                      position: "relative", padding: "var(--sp-xl) var(--sp-lg)",
                      display: "flex", flexDirection: "column", gap: "var(--sp-md)",
                      border: "1px solid rgb(255 255 255 / 0.04)", minHeight: "260px", overflow: "hidden",
                    }}>
                    <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", gap: "var(--sp-md)", flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "oklch(0.75 0.015 270 / 0.65)" }}>
                        <span>{String(i + 1).padStart(2, "0")}</span>
                        <span className="dot" />
                        <span>{a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : ""}</span>
                        <span className="dot" />
                        <span>{a.readingTime} 分钟</span>
                      </div>
                      <h3 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, lineHeight: 1.3, color: "#fff" }}>{a.title}</h3>
                      <p style={{ color: "oklch(0.82 0.015 270 / 0.78)", fontSize: "var(--fs-small)" }}>{a.excerpt}</p>
                      <Tags tags={a.tags} />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Section 3: 精选作品 */}
        <section ref={(el) => { sectionsRef.current[2] = el; }} className="section" data-section="works">
          <div className="section__bg" data-parallax="0.25">
            <img src={sectionImages[2]} alt="" loading="lazy" />
          </div>
          <div className="section__overlay" style={{ background: "linear-gradient(180deg, oklch(0 0 0 / 0.55) 0%, oklch(0 0 0 / 0.15) 25%, oklch(0 0 0 / 0.15) 75%, oklch(0 0 0 / 0.55) 100%)" }} />
          <div className="section__spot" />
          <div className="section__scrim" />

          <div className="section__content anim-content">
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="section__number">/ 02</p>
                <h2 className="section__heading">精选作品</h2>
              </div>
              <Link href="/products" className="section__link">查看全部 →</Link>
            </div>

            {products.length === 0 ? (
              <StateCard type="empty" minHeight="200px" />
            ) : (
              <div className="works-grid">
                {products.map((p, i) => (
                  <Link key={p.id} href={`/products/${p.slug}`}
                    style={{
                      position: "relative", overflow: "hidden", cursor: "pointer",
                      ...(i === 0 ? { gridRow: "1 / -1" } : {}),
                    }}>
                    <img src={p.coverImage || "/uploads/fallback-product.webp"} alt={p.title}
                      style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.4) contrast(1.2)" }} />
                    <div className="works-card-info">
                      <h3 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, color: "#fff" }}>{p.title}</h3>
                      <p style={{ fontSize: "var(--fs-small)", color: "oklch(0.68 0.01 270 / 0.5)" }}>{p.description}</p>
                    </div>
                    <span className="works-card-status">
                      {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Section 4: 引用 */}
        <section ref={(el) => { sectionsRef.current[3] = el; }} className="section" data-section="quote">
          <div className="section__bg" data-parallax="0.2">
            <img src={sectionImages[3]} alt="" loading="lazy" />
          </div>
          <div className="section__overlay" style={{ background: "linear-gradient(180deg, oklch(0 0 0 / 0.6) 0%, oklch(0 0 0 / 0.2) 30%, oklch(0 0 0 / 0.2) 70%, oklch(0 0 0 / 0.6) 100%)" }} />
          <div className="section__spot" />
          <div className="section__scrim" />
          <div className="section__content section__content--center anim-content">
            <figure className="quote__text">
              &ldquo;光影不是装饰，<br />它是空间的骨架。&rdquo;
            </figure>
            <p className="quote__attribution">— 2026 · Atelier</p>
          </div>
        </section>
      </div>
    </>
  );
}
