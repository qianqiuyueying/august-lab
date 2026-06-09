"use client";
import Link from "next/link";
import { useState } from "react";

export function ProductDetailClient({ product }: { product: any }) {
  const [panelOpen, setPanelOpen] = useState(false);

  const statusLabel = product.status === "online" ? "在线" : product.status === "developing" ? "开发中" : "已下线";

  return (
    <main style={{ height: "100vh", overflow: "hidden", background: "#000", position: "relative" }}>
      {/* IFrame 全屏 */}
      <div style={{ position: "fixed", inset: 0, zIndex: 1 }}>
        {product.url ? (
          <iframe src={product.url} style={{ width: "100%", height: "100%", border: 0 }} sandbox="allow-scripts allow-same-origin" title={product.title} />
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--c-fg-dim)", fontFamily: "var(--ff-body)" }}>
            暂无运行文件
          </div>
        )}
      </div>

      {/* 浮动工具栏 */}
      <div className="runtime-toolbar">
        <Link href="/products" className="runtime-toolbar__back">← 返回</Link>
        <span className="runtime-toolbar__divider" />
        <span className="runtime-toolbar__title">{product.title}</span>
        <div className="runtime-toolbar__actions">
          {product.url && (
            <button onClick={() => window.open(product.url, "_blank")} className="runtime-toolbar__action">新窗口</button>
          )}
          <button onClick={() => setPanelOpen(!panelOpen)} className="runtime-toolbar__action">信息</button>
        </div>
      </div>

      {/* 信息面板 */}
      <div className={`info-panel${panelOpen ? " info-panel--open" : ""}`}>
        <div className="info-panel__handle" onClick={() => setPanelOpen(!panelOpen)}>
          <div className="info-panel__handle-bar" />
        </div>
        <div className="info-panel__body">
          <img src={product.coverImage || "/uploads/fallback-product.webp"} alt={product.title} className="info-panel__cover" />
          <div className="info-panel__content">
            <h1 className="info-panel__title">{product.title}</h1>
            <p className="info-panel__desc">{product.description}</p>
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
  );
}
