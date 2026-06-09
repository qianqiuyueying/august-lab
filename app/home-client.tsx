"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";

/* ==========================================
   Atelier Home — 1:1 复刻原型 home.html
   叠化视差滚动 · 电影级
   ========================================== */

export function HomeClient({
  articles,
  products,
}: {
  articles: any[];
  products: any[];
}) {
  const [activeSection, setActiveSection] = useState(0);
  const sectionsRef = useRef<(HTMLElement | null)[]>([]);
  const navRef = useRef<HTMLElement | null>(null);

  /* ——— 核心更新（1:1 复刻原型 JS 逻辑）——— */
  const updateScene = useCallback(() => {
    const winH = window.innerHeight;
    let maxVis = 0;
    let newIdx = 0;

    sectionsRef.current.forEach((sec, i) => {
      if (!sec) return;
      const r = sec.getBoundingClientRect();
      const secH = sec.offsetHeight;

      // 可见比例
      const visibleInView = Math.min(r.bottom, winH) - Math.max(r.top, 0);
      const visibility = Math.max(0, Math.min(1, visibleInView / secH));

      if (visibility > maxVis) {
        maxVis = visibility;
        newIdx = i;
      }

      // ——— 内容动画：加强叠化 ———
      const content = sec.querySelector(".home-anim-content") as HTMLElement;
      if (content) {
        // 8% 开始出现，63% 完全可见 — 更紧凑，变化更骤烈
        const raw = Math.max(0, Math.min(1, (visibility - 0.08) / 0.55));
        // easeOutExpo 加倍火力 — 指数从 10 → 12
        const eased = raw === 1 ? 1 : 1 - Math.pow(2, -12 * raw);
        const sc = 0.70 + 0.30 * eased;       // 从 70% 缩小开始（原来 82%）
        const blr = 22 * (1 - eased);          // 最大模糊 22px（原来 14px）
        const tilt = 14 * (1 - eased);         // 最大倾斜 14deg（原来 10deg）
        content.style.opacity = String(eased);
        content.style.transform = `translateY(${(1 - eased) * 150}px) scale(${sc}) rotateX(${tilt}deg)`;
        content.style.filter = `blur(${blr}px)`;
      }

      // ——— 背景视差 + 加强 Ken Burns 缩放 ———
      const bg = sec.querySelector(".home-section__bg") as HTMLElement;
      if (bg) {
        const parallaxSpeed = parseFloat(bg.dataset.parallax || "0.15");
        const offset = r.top * Math.max(parallaxSpeed * 1.6, 0.35);
        // 放大到 1.10，缩小到 0.90 — 更明显的呼吸感
        const scale = 1.0 + 0.12 * Math.max(0, Math.sin(visibility * Math.PI - 0.25));
        bg.style.transform = `translateY(${offset}px) scale(${scale})`;
      }

      // ——— 动态幕布（叠化过渡）— 更深黑 ———
      const scrim = sec.querySelector(".home-section__scrim") as HTMLElement;
      if (scrim) {
        const leaving = Math.max(0, Math.min(1, -r.top / secH));
        const entering = Math.max(0, Math.min(1, (r.bottom - winH) / secH));
        // 幕布最高 95% 黑 — 过渡更厚重
        const scrimO = Math.max(leaving * 0.95, entering * 0.78);
        scrim.style.opacity = String(scrimO);
      }

      // 活跃状态标记
      sec.classList.toggle("active", visibility > 0.3);
    });

    const prevIdx = activeSection;
    setActiveSection(newIdx);

    // ——— 导航点 ———
    const dots = document.querySelectorAll(".home-dots__dot");
    dots.forEach((dot, i) => {
      dot.classList.toggle("active", i === newIdx);
    });

    // ——— 导航 solid 状态 ———
    const heroSec = sectionsRef.current[0];
    if (heroSec && navRef.current) {
      const heroR = heroSec.getBoundingClientRect();
      navRef.current.classList.toggle("home-nav--solid", heroR.bottom < 60);
    }
  }, [activeSection]);

  /* ——— rAF 节流 ——— */
  useEffect(() => {
    let ticking = false;
    const scrollHandler = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          updateScene();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", scrollHandler, { passive: true });

    // ——— 导航点点击 ———
    const dots = document.querySelectorAll(".home-dots__dot");
    const clickHandlers: Array<() => void> = [];
    dots.forEach((dot) => {
      const handler = () => {
        const target = (dot as HTMLElement).dataset.target;
        const sec = document.querySelector(`[data-section="${target}"]`);
        if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
      };
      dot.addEventListener("click", handler);
      clickHandlers.push(handler);
    });

    // ——— resize ———
    let rt: ReturnType<typeof setTimeout>;
    const resizeHandler = () => {
      clearTimeout(rt);
      rt = setTimeout(updateScene, 100);
    };
    window.addEventListener("resize", resizeHandler, { passive: true });

    // ——— 初始调用 ———
    updateScene();

    return () => {
      window.removeEventListener("scroll", scrollHandler);
      dots.forEach((dot, i) => {
        dot.removeEventListener("click", clickHandlers[i]);
      });
      window.removeEventListener("resize", resizeHandler);
      clearTimeout(rt);
    };
  }, [updateScene]);

  /* ——— URL 参数状态 ——— */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get("state");
    if (state) document.body.dataset.state = state;
    return () => { document.body.dataset.state = ""; };
  }, []);

  const navLinks = [
    { href: "/", label: "首页" },
    { href: "/blog", label: "笔记" },
    { href: "/products", label: "作品" },
    { href: "/about", label: "关于" },
  ];

  const secImages = [
    "/uploads/venetian-blind-shadow.png",
    "/uploads/perforated-metal-shadow.png",
    "/uploads/plaster-geometric.png",
    "/uploads/glass-shadow.png",
  ];

  const secIds = ["hero", "articles", "works", "quote"];

  return (
    <>
      {/* ====== 导航 ====== */}
      <nav className="home-nav" ref={navRef}>
        <div className="home-nav__brand">
          <span className="home-nav__mark"></span>
          <span className="home-nav__name">Atelier</span>
        </div>
        <div className="home-nav__links">
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className={`home-nav__link${l.href === "/" ? " active" : ""}`}>
              {l.label}
            </Link>
          ))}
        </div>
      </nav>

      {/* Section 导航点 */}
      <nav className="home-dots">
        {secIds.map((id) => (
          <span key={id} className="home-dots__dot" data-target={id} />
        ))}
      </nav>

      {/* 主体 */}
      <div className="home-dissolve-body">

        {/* ====== 场景 1 — Hero ====== */}
        <section
          ref={(el) => { sectionsRef.current[0] = el; }}
          className="home-section" data-section="hero"
        >
          <div className="home-section__bg" data-parallax="0.3">
            <img src={secImages[0]} alt="百叶窗光影" loading="eager" />
          </div>
          <div className="home-section__overlay home-hero__overlay"></div>
          <div className="home-section__spot"></div>
          <div className="home-section__scrim"></div>

          <div className="home-section__content home-section__content--center home-anim-content" style={{ paddingTop: "5vh" }}>
            <p className="home-hero__label">光影之间</p>
            <h1 className="home-hero__title">
              August&apos;s
              <span className="thin">Atelier</span>
            </h1>
            <p className="home-hero__desc">
              用光影与图像驱动的创作空间<br />
              记录灵感、实验与作品
            </p>
          </div>

          <div className="home-hero__scroll">
            <span>向下探索</span>
            <div className="home-hero__scroll-line"></div>
          </div>
        </section>

        {/* ====== 场景 2 — 最新笔记 ====== */}
        <section
          ref={(el) => { sectionsRef.current[1] = el; }}
          className="home-section" data-section="articles"
        >
          <div className="home-section__bg" data-parallax="0.3">
            <img src={secImages[1]} alt="穿孔金属板光影" loading="lazy" />
          </div>
          <div className="home-section__overlay home-articles__overlay"></div>
          <div className="home-section__spot"></div>
          <div className="home-section__scrim"></div>

          <div className="home-section__content home-anim-content">
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="home-section__number">/ 01</p>
                <h2 className="home-section__heading">最新笔记</h2>
              </div>
              <Link href="/blog" className="home-section__link">查看全部 →</Link>
            </div>

            <div className="home-articles__grid">
              {articles.map((a, i) => (
                <Link key={a.id} href={`/blog/${a.slug}`} className="home-articles__card">
                  <div className="home-articles__card-content">
                    <div className="home-articles__card-meta">
                      <span className="home-articles__card-index">{String(i + 1).padStart(2, "0")}</span>
                      <span className="home-articles__card-dot"></span>
                      <span>{a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : ""}</span>
                      <span className="home-articles__card-dot"></span>
                      <span>{a.readingTime} 分钟</span>
                    </div>
                    <h3 className="home-articles__card-title">{a.title}</h3>
                    <p className="home-articles__card-excerpt">{a.excerpt}</p>
                    <div className="home-articles__card-tags">
                      {(a.tags || []).map((t: string) => (
                        <span key={t} className="tag">{t}</span>
                      ))}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ====== 场景 3 — 精选作品 ====== */}
        <section
          ref={(el) => { sectionsRef.current[2] = el; }}
          className="home-section" data-section="works"
        >
          <div className="home-section__bg" data-parallax="0.25">
            <img src={secImages[2]} alt="几何石膏体" loading="lazy" />
          </div>
          <div className="home-section__overlay home-works__overlay"></div>
          <div className="home-section__spot"></div>
          <div className="home-section__scrim"></div>

          <div className="home-section__content home-anim-content">
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "var(--sp-xl)" }}>
              <div>
                <p className="home-section__number">/ 02</p>
                <h2 className="home-section__heading">精选作品</h2>
              </div>
              <Link href="/products" className="home-section__link">查看全部 →</Link>
            </div>

            <div className="home-works__grid">
              {products.map((p, i) => (
                <Link
                  key={p.id}
                  href={`/products/${p.slug}`}
                  className={`home-works__card${i === 0 ? " home-works__card--featured" : ""}`}
                >
                  <img src={p.coverImage || "/uploads/metal-ruler.png"} alt={p.title} loading="lazy" />
                  <div className="home-works__card-info">
                    <h3 className="home-works__card-title">{p.title}</h3>
                    <p className="home-works__card-sub">{p.description}</p>
                  </div>
                  <span className="home-works__card-status">
                    {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ====== 场景 4 — 引用 ====== */}
        <section
          ref={(el) => { sectionsRef.current[3] = el; }}
          className="home-section" data-section="quote"
        >
          <div className="home-section__bg" data-parallax="0.2">
            <img src={secImages[3]} alt="玻璃杯阴影" loading="lazy" />
          </div>
          <div className="home-section__overlay home-quote__overlay"></div>
          <div className="home-section__spot"></div>
          <div className="home-section__scrim"></div>

          <div className="home-section__content home-section__content--center home-anim-content">
            <div className="home-quote__body">
              <figure className="home-quote__text">
                &quot;光影不是装饰，<br />它是空间的骨架。&quot;
              </figure>
              <p className="home-quote__attribution">— 2026 · Atelier</p>
            </div>
          </div>
        </section>

      </div>{/* /home-dissolve-body */}

      {/* 状态: Loading */}
      <div className="state-card home-state-loading home-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">加载中</div>
        <p className="state-card__desc">正在获取内容…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>

      {/* 状态: Error */}
      <div className="state-card home-state-error home-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">加载失败</div>
        <p className="state-card__desc">无法连接到服务器，请稍后重试。</p>
        <button className="btn" style={{ marginTop: "var(--sp-lg)" }} onClick={() => window.location.reload()}>重新加载</button>
      </div>

      {/* 状态: Empty */}
      <div className="state-card home-state-empty home-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">暂无内容</div>
        <p className="state-card__desc">还没有发布任何内容，敬请期待。</p>
      </div>
    </>
  );
}
