"use client";
import { useState } from "react";

export default function MascotPage() {
  const [persona, setPersona] = useState("你是一位名叫「小光」的看板娘，性格温柔亲切，擅长用简洁温暖的语言介绍这个站点的内容和设计师的创作思路。");
  const [apiKey, setApiKey] = useState("sk-demo-key-xxxxxxxx");
  const [baseUrl, setBaseUrl] = useState("https://api.openai.com/v1");
  const [model, setModel] = useState("gpt-4o-mini");
  const [temp, setTemp] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(256);
  const [greeting, setGreeting] = useState(true);
  const [greetingDelay, setGreetingDelay] = useState(3);
  const [actionInterval, setActionInterval] = useState(60);
  const [contextAware, setContextAware] = useState(true);
  const [draggable, setDraggable] = useState(true);
  const [enabled, setEnabled] = useState(true);
  const [visible, setVisible] = useState(true);
  const [mobile, setMobile] = useState(false);
  const [scale, setScale] = useState(1.0);
  const [banner, setBanner] = useState("");

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setBanner("设置已保存");
    setTimeout(() => setBanner(""), 3000);
  };

  return (
    <div className="mascot-layout" style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "var(--sp-lg)", alignItems: "start" }}>
      <div className="mascot-main" style={{ minWidth: 0 }}>
        <form id="mascotForm" onSubmit={handleSave}>
          <div className="admin-page-header">
            <div>
              <div className="admin-page-header__label">Console</div>
              <h1 className="admin-page-header__title">看板娘设置</h1>
              <p className="admin-page-header__desc">配置 AI 看板娘的角色人设、API 连接与行为表现。</p>
            </div>
            <div className="admin-page-header__actions">
              <button className="admin-btn admin-btn--primary" type="submit">保存设置</button>
            </div>
          </div>

          {banner && (
            <div className="msg-banner" style={{ padding: "var(--sp-sm) var(--sp-md)", borderRadius: "var(--radius-sm)", fontSize: "var(--fs-small)", marginBottom: "var(--sp-lg)", border: "1px solid oklch(0.65 0.12 160)", background: "oklch(0.65 0.12 160 / 0.1)", color: "oklch(0.72 0.12 160)" }}>{banner}</div>
          )}

          <div className="admin-section">
            <h2 className="admin-section__title">人设（System Prompt）</h2>
            <div className="admin-form-group"><label className="admin-form-label">角色提示词</label><textarea className="admin-textarea" rows={5} value={persona} onChange={(e) => setPersona(e.target.value)} /></div>
          </div>

          <div className="admin-section">
            <h2 className="admin-section__title">API 配置</h2>
            <div className="admin-form-group"><label className="admin-form-label">API Key</label><input className="admin-input" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} /></div>
            <div className="admin-form-group"><label className="admin-form-label">Base URL</label><input className="admin-input" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} /></div>
            <div className="admin-form-group"><label className="admin-form-label">Model</label><input className="admin-input" value={model} onChange={(e) => setModel(e.target.value)} /></div>
            <div className="admin-form-grid">
              <div className="admin-form-group"><label className="admin-form-label">Temperature ({temp})</label><input type="range" min="0" max="2" step="0.1" value={temp} onChange={(e) => setTemp(parseFloat(e.target.value))} /></div>
              <div className="admin-form-group"><label className="admin-form-label">Max Tokens</label><input className="admin-input" type="number" value={maxTokens} onChange={(e) => setMaxTokens(parseInt(e.target.value))} /></div>
            </div>
          </div>

          <div className="admin-section">
            <h2 className="admin-section__title">行为设置</h2>
            <div className="admin-form-grid">
              <label className="admin-toggle"><input type="checkbox" checked={greeting} onChange={(e) => setGreeting(e.target.checked)} />启用问候语</label>
              <div className="admin-form-group"><label className="admin-form-label">问候延迟（秒）</label><input className="admin-input" type="number" value={greetingDelay} onChange={(e) => setGreetingDelay(parseInt(e.target.value))} /></div>
            </div>
            <div className="admin-form-group"><label className="admin-form-label">随机动作间隔（秒）</label><input className="admin-input" type="number" value={actionInterval} onChange={(e) => setActionInterval(parseInt(e.target.value))} /></div>
            <div style={{ display: "flex", gap: "var(--sp-lg)", flexWrap: "wrap" }}>
              <label className="admin-toggle"><input type="checkbox" checked={contextAware} onChange={(e) => setContextAware(e.target.checked)} />上下文感知</label>
              <label className="admin-toggle"><input type="checkbox" checked={draggable} onChange={(e) => setDraggable(e.target.checked)} />允许拖拽</label>
            </div>
          </div>
        </form>
      </div>

      {/* 右栏 */}
      <div>
        <div className="admin-section">
          <h2 className="admin-section__title">开关</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)" }}>
            <label className="admin-toggle" style={{ justifyContent: "space-between" }}><span>启用看板娘</span><input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} /></label>
            <label className="admin-toggle" style={{ justifyContent: "space-between" }}><span>显示形象</span><input type="checkbox" checked={visible} onChange={(e) => setVisible(e.target.checked)} /></label>
            <label className="admin-toggle" style={{ justifyContent: "space-between" }}><span>移动端显示</span><input type="checkbox" checked={mobile} onChange={(e) => setMobile(e.target.checked)} /></label>
          </div>
        </div>
        <div className="admin-section" style={{ marginTop: "var(--sp-sm)" }}>
          <h2 className="admin-section__title">外观</h2>
          <div className="admin-form-group"><label className="admin-form-label">缩放比例 ({scale.toFixed(1)})</label><input type="range" min="0.5" max="3" step="0.1" value={scale} onChange={(e) => setScale(parseFloat(e.target.value))} /></div>
          <div className="mascot-preview" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--sp-sm)", padding: "var(--sp-md)", background: "var(--c-bg)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", marginTop: "var(--sp-sm)", overflow: "hidden" }}>
            <div style={{ transform: `scale(${scale})`, transition: "transform 0.15s var(--ease-expo)", transformOrigin: "center", width: 192, height: 208 }}>
              <img src="/mascot/spritesheet.webp" alt="看板娘预览"
                style={{ display: "block", width: 192, height: 208, objectFit: "none", objectPosition: "0px 0px" }} />
            </div>
            <span className="mascot-preview__hint" style={{ fontSize: 10, color: "var(--c-muted)", fontFamily: "var(--ff-mono)" }}>外观实时预览 · 拖动滑条查看缩放效果</span>
          </div>
        </div>
      </div>
    </div>
  );
}
