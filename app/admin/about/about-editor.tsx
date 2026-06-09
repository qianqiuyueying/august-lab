"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function AboutEditor({ info }: { info: any }) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [bio, setBio] = useState(info?.aboutBio ?? "");
  const [linksJson, setLinksJson] = useState(JSON.stringify((info?.aboutLinks as any[]) ?? [], null, 2));

  const handleSave = async () => {
    setSaving(true);
    let links = [];
    try { links = JSON.parse(linksJson); } catch { alert("链接 JSON 格式错误"); setSaving(false); return; }

    await fetch("/api/site-info", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aboutBio: bio, aboutLinks: links }),
    });
    setSaving(false);
    router.refresh();
  };

  return (
    <div>
      <h1 className="admin-page-title">编辑关于页</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-lg)", maxWidth: 700 }}>
        <label className="form-field">
          个人简介
          <textarea style={{ width: "100%", minHeight: 120, padding: "var(--sp-sm)", background: "var(--c-bg)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", color: "var(--c-fg)", fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)", outline: "none", resize: "vertical" }}
            value={bio} onChange={(e) => setBio(e.target.value)} />
        </label>
        <label className="form-field">
          链接列表 (JSON)
          <textarea style={{ width: "100%", minHeight: 200, padding: "var(--sp-sm)", background: "var(--c-bg)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", color: "var(--c-fg)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", outline: "none", resize: "vertical" }}
            value={linksJson} onChange={(e) => setLinksJson(e.target.value)} />
        </label>
        <button className="btn" onClick={handleSave} disabled={saving} style={{ alignSelf: "flex-start" }}>
          {saving ? "保存中…" : "保存"}
        </button>
      </div>
    </div>
  );
}
