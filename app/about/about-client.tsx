"use client";
import { useEffect, useRef } from "react";
import Link from "next/link";

export function AboutClient({ bio, links }: { bio: string; links: Array<{ label: string; url: string }> }) {
  const heroRef = useRef<HTMLElement>(null);

  /* ===== 导航滚动 solid ===== */
  useEffect(() => {
    const nav = document.getElementById("mainNav");
    const hero = heroRef.current;
    if (!nav || !hero) return;
    const update = () => nav.classList.toggle("nav-v2--solid", hero.getBoundingClientRect().bottom < 60);
    window.addEventListener("scroll", update, { passive: true });
    update();
    return () => window.removeEventListener("scroll", update);
  }, []);

  /* ===== Hero 视差 ===== */
  useEffect(() => {
    const heroBg = document.getElementById("aboutHeroBg");
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

  return (
    <>
      <main className="about-state-default">
        {/* Hero */}
        <header className="about-hero" ref={heroRef}>
          <div className="about-hero__bg" id="aboutHeroBg">
            <img src="/uploads/prism-light.png" alt="棱镜折射" loading="eager" />
          </div>
          <div className="about-hero__overlay"></div>
          <div className="about-hero__spot"></div>
          <div className="about-hero__content">
            <p className="about-hero__label">/ 关于</p>
            <h1 className="about-hero__title">关于我</h1>
          </div>
        </header>

        <div className="about-body">
          <div className="container">
            {/* 简介 */}
            <div className="about-intro">
              <div className="about-intro__avatar">
                <img src="/uploads/grid-shadow.png" alt="头像" loading="lazy" />
              </div>
              <div className="about-intro__text">
                <p className="about-intro__numbered">EXP-ABOUT-01</p>
                <p className="about-intro__eyebrow">August</p>
                <h2 className="about-intro__name">开发者 · 实验者</h2>
                <div className="about-intro__rule"></div>
                <p className="about-intro__bio">{bio}</p>
              </div>
            </div>

            {/* 统计 */}
            <div className="about-stats">
              <div className="about-stat">
                <span className="about-stat__label">位置</span>
                <span className="about-stat__value">中国</span>
              </div>
              <div className="about-stat">
                <span className="about-stat__label">方向</span>
                <span className="about-stat__value">前端 · 设计</span>
              </div>
              <div className="about-stat">
                <span className="about-stat__label">状态</span>
                <span className="about-stat__value">正在创作</span>
              </div>
              <div className="about-stat">
                <span className="about-stat__label">经验</span>
                <span className="about-stat__value">5+ 年</span>
              </div>
            </div>

            {/* 双栏 */}
            <div className="about-double">
              <div className="about-double__col">
                <h3 className="about-double__title">技术栈</h3>
                <div className="tech-list">
                  <span className="tag">React</span>
                  <span className="tag">TypeScript</span>
                  <span className="tag">Next.js</span>
                  <span className="tag">Tailwind</span>
                  <span className="tag">Node.js</span>
                  <span className="tag">Prisma</span>
                  <span className="tag">ComfyUI</span>
                </div>
              </div>
              <div className="about-double__col">
                <h3 className="about-double__title">联系方式</h3>
                <div className="contact-list">
                  {links.map((link, i) => (
                    <a key={i} href={link.url} target="_blank" rel="noopener noreferrer" className="contact-list__item">
                      <span className="contact-list__icon">{link.label.slice(0, 2).toUpperCase()}</span>
                      {link.label}
                    </a>
                  ))}
                </div>
              </div>
            </div>

            {/* 了解更多 */}
            <div className="about-details">
              <details>
                <summary>了解更多</summary>
                <div className="about-details__content">
                  <p>一个喜欢动手折腾的创作者。写代码、拍照片、做实验是日常。</p>
                  <p>工具不拘，想法先行。只要灵光一闪，就搭个东西出来看看。</p>
                </div>
              </details>
            </div>
          </div>
        </div>
      </main>

      {/* 状态 */}
      <div className="state-card about-state-loading about-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
        <div className="state-card__title">加载中</div>
        <p className="state-card__desc">正在获取个人信息…</p>
        <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
      </div>
      <div className="state-card about-state-error about-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">!</div>
        <div className="state-card__title">加载失败</div>
        <p className="state-card__desc">无法获取个人信息。</p>
        <button className="btn" style={{ marginTop: "var(--sp-lg)" }} onClick={() => window.location.reload()}>重新加载</button>
      </div>
      <div className="state-card about-state-empty about-state-override" style={{ minHeight: "100vh" }}>
        <div className="state-card__icon">—</div>
        <div className="state-card__title">尚未配置</div>
        <p className="state-card__desc">个人页面尚未设置内容。</p>
      </div>
    </>
  );
}
