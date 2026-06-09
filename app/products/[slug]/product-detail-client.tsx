"use client";
import Link from "next/link";
import { useState, useEffect } from "react";

export function ProductDetailClient({ product }: { product: any }) {
  const [panelOpen, setPanelOpen] = useState(false);

  const statusLabel = product.status === "online" ? "在线" : product.status === "developing" ? "开发中" : "已下线";

  /* ===== URL 参数状态 ===== */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get("state");
    if (state) document.body.dataset.state = state;
    return () => { document.body.dataset.state = ""; };
  }, []);

  return (
    <>
      <div className="pd-body">
        <main className="pd-state-default">
          {/* IFrame 运行环境 */}
          <div className="runtime-frame">
            {product.url ? (
              <iframe src={product.url} sandbox="allow-scripts allow-same-origin" title="作品运行环境" />
            ) : (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--c-fg-dim)", fontFamily: "var(--ff-body)", background: "#000", position: "fixed", inset: 0, zIndex: 1 }}>
                暂无可运行文件
              </div>
            )}
          </div>

          {/* 工具栏 */}
          <div className="runtime-toolbar">
            <Link href="/products" className="runtime-toolbar__back">← 返回</Link>
            <span className="runtime-toolbar__divider"></span>
            <span className="runtime-toolbar__title">{product.title}</span>
            <div className="runtime-toolbar__actions">
              {product.url && (
                <button className="runtime-toolbar__action" onClick={() => window.open(product.url, "_blank")}>新窗口</button>
              )}
              <button className="runtime-toolbar__action" onClick={() => setPanelOpen(!panelOpen)}>信息</button>
            </div>
          </div>

          {/* 信息面板 */}
          <div className={`info-panel${panelOpen ? " info-panel--open" : ""}`}>
            <div className="info-panel__handle" onClick={() => setPanelOpen(!panelOpen)}>
              <div className="info-panel__handle-bar"></div>
            </div>
            <div className="info-panel__body">
              <img src={product.coverImage || "/uploads/metal-ruler.png"} alt={product.title} className="info-panel__cover" loading="lazy" />
              <div className="info-panel__content">
                <h2 className="info-panel__title">{product.title}</h2>
                <p className="info-panel__desc">{product.description || product.content}</p>
                <div className="info-panel__meta">
                  <div className="info-panel__meta-item">
                    <span className="info-panel__meta-label">标识</span>
                    <span>{product.slug}</span>
                  </div>
                  <div className="info-panel__meta-item">
                    <span className="info-panel__meta-label">状态</span>
                    <span>{statusLabel}</span>
                  </div>
                  <div className="info-panel__meta-item">
                    <span className="info-panel__meta-label">更新</span>
                    <span>{new Date(product.updatedAt).toISOString().slice(0, 10)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* 状态 */}
        <div className="state-card pd-state-loading pd-state-override" style={{ minHeight: "100vh" }}>
          <div className="state-card__icon" style={{ animation: "pulse 1.5s ease-in-out infinite" }}>⟳</div>
          <div className="state-card__title">加载中</div>
          <p className="state-card__desc">正在加载运行环境…</p>
          <style>{`@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:0.8; } }`}</style>
        </div>
        <div className="state-card pd-state-error pd-state-override" style={{ minHeight: "100vh" }}>
          <div className="state-card__icon">!</div>
          <div className="state-card__title">加载失败</div>
          <p className="state-card__desc">运行环境不可用。</p>
          <Link href="/products" className="btn" style={{ marginTop: "var(--sp-lg)" }}>返回作品列表</Link>
        </div>
        <div className="state-card pd-state-empty pd-state-override" style={{ minHeight: "100vh" }}>
          <div className="state-card__icon">—</div>
          <div className="state-card__title">暂无可运行文件</div>
          <p className="state-card__desc">此作品已发布但尚未上传运行文件。</p>
          <Link href="/products" className="btn" style={{ marginTop: "var(--sp-lg)" }}>返回作品列表</Link>
        </div>
      </div>
    </>
  );
}
