"use client";
import { useEffect, useRef } from "react";
import Link from "next/link";

type Product = {
  id: number; slug: string; title: string; description: string;
  coverImage: string; status: string; tags: string[];
};

const STATUS_LABELS: Record<string, { label: string; live?: boolean }> = {
  online: { label: "在线", live: true },
  developing: { label: "开发中" },
  offline: { label: "已下线" },
  draft: { label: "研究" },
};

/* 画廊卡片尺寸模板（循环模式：大 / 普通 / 普通 / 宽 / 普通 / 普通 / 宽 ...） */
const CARD_SIZES = ["large", "normal", "normal", "wide", "normal", "normal", "wide"];

export function ProductsClient({ products }: { products: Product[] }) {
  const heroRef = useRef<HTMLElement>(null);

  /* ===== 导航栏滚动 solid ===== */
  useEffect(() => {
    const nav = document.getElementById("productsNav");
    const hero = heroRef.current;
    if (!nav || !hero) return;
    const update = () => nav.classList.toggle("nav-v2--solid", hero.getBoundingClientRect().bottom < 60);
    window.addEventListener("scroll", update, { passive: true });
    update();
    return () => window.removeEventListener("scroll", update);
  }, []);

  /* ===== Hero 视差 ===== */
  useEffect(() => {
    const heroBg = document.getElementById("productsHeroBg");
    const hero = heroRef.current;
    if (!heroBg || !hero) return;
    const onScroll = () => {
      heroBg.style.transform = `translateY(${(window.scrollY - hero.offsetTop) * 0.25}px)`;
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

  const getSizeClass = (i: number) => {
    const size = CARD_SIZES[i % CARD_SIZES.length];
    if (size === "large") return "gallery-card--large";
    if (size === "wide") return "gallery-card--wide";
    return "";
  };

  return (
    <>
      <nav className="nav-v2" id="productsNav">
        <Link href="/" className="nav-v2__brand">Atelier</Link>
        <div className="nav-v2__links">
          <Link href="/" className="nav-v2__link">首页</Link>
          <Link href="/blog" className="nav-v2__link">笔记</Link>
          <Link href="/products" className="nav-v2__link active">作品</Link>
          <Link href="/about" className="nav-v2__link">关于</Link>
        </div>
      </nav>

      <main className="products-state-default">
        <header className="products-hero" ref={heroRef}>
          <div className="products-hero__bg" id="productsHeroBg">
            <img src="/uploads/plaster-geometric.png" alt="几何石膏体" loading="eager" />
          </div>
          <div className="products-hero__overlay"></div>
          <div className="products-hero__content">
            <p className="products-hero__label">/ 作品</p>
            <h1 className="products-hero__title">项目与实验</h1>
            <p className="products-hero__desc">从工具到创意项目，每一个都经过反复打磨</p>
          </div>
        </header>

        <section className="gallery">
          <div className="container">
            <div className="gallery-grid">
              {products.map((p, i) => {
                const st = STATUS_LABELS[p.status] || { label: p.status };
                return (
                  <Link key={p.id} href={`/products/${p.slug}`} className={`gallery-card ${getSizeClass(i)}`}>
                    <div className="gallery-card__img">
                      <img src={p.coverImage || "/uploads/metal-ruler.png"} alt={p.title} loading="lazy" />
                    </div>
                    <span className={`gallery-card__status${st.live ? " gallery-card__status--live" : ""}`}>
                      {st.label}
                    </span>
                    <div className="gallery-card__info">
                      <h2 className="gallery-card__title">{p.title}</h2>
                      <p className="gallery-card__desc">{p.description}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      {/* 状态 */}
      <div className="state-card products-state-loading products-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">加载中</div>
        <p className="state-card__desc">正在获取作品列表…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>
      <div className="state-card products-state-error products-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">加载失败</div>
        <p className="state-card__desc">无法连接到服务器，请稍后重试。</p>
        <button className="btn" style={{ marginTop: "var(--sp-lg)" }} onClick={() => window.location.reload()}>重新加载</button>
      </div>
      <div className="state-card products-state-empty products-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">暂无作品</div>
        <p className="state-card__desc">还没有发布任何作品。</p>
      </div>
    </>
  );
}
