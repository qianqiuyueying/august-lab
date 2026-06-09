"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

export function AboutEditor({ info }: { info: any }) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [bio, setBio] = useState(info?.aboutBio ?? "");
  const [linksJson, setLinksJson] = useState(JSON.stringify((info?.aboutLinks as any[]) ?? [], null, 2));
  const [banner, setBanner] = useState("");

  const handleSave = async () => {
    setSaving(true);
    let links = [];
    try { links = JSON.parse(linksJson); } catch { alert("链接 JSON 格式错误"); setSaving(false); return; }
    const res = await fetch("/api/site-info", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ aboutBio: bio, aboutLinks: links }) });
    setSaving(false);
    if (res.ok) { setBanner("已保存"); setTimeout(() => setBanner(""), 3000); router.refresh(); }
  };

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">关于页</h1>
          <p className="admin-page-header__desc">编辑关于页的简介与联系人信息。</p>
        </div>
        <div className="admin-page-header__actions">
          <NextLink href="/about" target="_blank" className="admin-btn">前台预览 →</NextLink>
          <button className="admin-btn admin-btn--primary" onClick={handleSave} disabled={saving}>{saving ? "保存中…" : "保存"}</button>
        </div>
      </div>

      {banner && (
        <div className="msg-banner" style={{ padding: "var(--sp-sm) var(--sp-md)", borderRadius: "var(--radius-sm)", fontSize: "var(--fs-small)", marginBottom: "var(--sp-lg)", border: "1px solid oklch(0.65 0.12 160)", background: "oklch(0.65 0.12 160 / 0.1)", color: "oklch(0.72 0.12 160)" }}>{banner}</div>
      )}

      <div className="admin-section">
        <h2 className="admin-section__title">个人简介</h2>
        <div className="admin-form-group">
          <label className="admin-form-label">简介内容</label>
          <textarea className="admin-textarea" rows={5} value={bio} onChange={(e) => setBio(e.target.value)} />
        </div>
      </div>

      <div className="admin-section">
        <h2 className="admin-section__title">社交链接 (JSON)</h2>
        <div className="admin-form-group">
          <label className="admin-form-label">链接列表</label>
          <textarea className="admin-textarea" rows={8} value={linksJson} onChange={(e) => setLinksJson(e.target.value)} style={{ fontFamily: "var(--ff-mono)" }} placeholder={`[{"label": "GitHub", "url": "https://github.com/..."}]`} />
        </div>
      </div>
    </>
  );
}
