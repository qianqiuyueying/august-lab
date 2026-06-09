"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

interface ArticleFormData {
  slug: string; title: string; excerpt: string; content: string;
  coverImage: string; tags: string; readingTime: number;
  featured: boolean; published: boolean;
}

const empty: ArticleFormData = { slug: "", title: "", excerpt: "", content: "", coverImage: "", tags: "", readingTime: 3, featured: false, published: false };

export function ArticleForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ArticleFormData>(empty);
  const [preview, setPreview] = useState("");
  const [tab, setTab] = useState<"edit" | "preview">("edit");
  const [saving, setSaving] = useState(false);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "", title: initial.title ?? "", excerpt: initial.excerpt ?? "",
        content: initial.content ?? "", coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "), readingTime: initial.readingTime ?? 3,
        featured: initial.featured ?? false, published: initial.published ?? false,
      });
      setPreview(initial.content ?? "");
    }
  }, [initial]);

  const set = (f: keyof ArticleFormData, v: string | number | boolean) => setForm((p) => ({ ...p, [f]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true);
    const payload = { ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) };
    const url = isEdit ? `/api/articles/${initial.id}` : "/api/articles";
    const res = await fetch(url, { method: isEdit ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    setSaving(false);
    if (res.ok) { router.push("/admin/articles"); router.refresh(); } else { alert("保存失败"); }
  };

  const updatePreview = (content: string) => { setPreview(content); set("content", content); };

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">{isEdit ? "编辑文章" : "新建文章"}</h1>
          <p className="admin-page-header__desc">{isEdit ? "修改文章内容与属性。" : "创建一篇新的文章。"}</p>
        </div>
        <div className="admin-page-header__actions">
          <NextLink href="/admin/articles" className="admin-btn">← 返回列表</NextLink>
          <button className="admin-btn admin-btn--primary" onClick={handleSubmit} disabled={saving}>{saving ? "保存中…" : "保存"}</button>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-sm)" }}>
        <div className="admin-section">
          <h2 className="admin-section__title">基本信息</h2>
          <div className="admin-form-grid">
            <div className="admin-form-group">
              <label className="admin-form-label">标识 (slug)</label>
              <input className="admin-input" value={form.slug} onChange={(e) => set("slug", e.target.value)} required />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">阅读时长（分钟）</label>
              <input className="admin-input" type="number" value={form.readingTime} onChange={(e) => set("readingTime", parseInt(e.target.value) || 3)} />
            </div>
          </div>
          <div className="admin-form-group">
            <label className="admin-form-label">标题</label>
            <input className="admin-input" value={form.title} onChange={(e) => set("title", e.target.value)} required />
          </div>
          <div className="admin-form-group">
            <label className="admin-form-label">摘要</label>
            <textarea className="admin-textarea" rows={3} value={form.excerpt} onChange={(e) => set("excerpt", e.target.value)} />
          </div>
          <div className="admin-form-grid">
            <div className="admin-form-group">
              <label className="admin-form-label">封面图 URL</label>
              <div style={{ display: "flex", gap: "var(--sp-sm)", alignItems: "flex-start" }}>
                {form.coverImage && <img src={form.coverImage} alt="" style={{ width: 60, height: 40, objectFit: "cover", borderRadius: 1, background: "var(--c-surf-2)" }} />}
                <input className="admin-input" style={{ flex: 1 }} value={form.coverImage} onChange={(e) => set("coverImage", e.target.value)} />
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">标签（逗号分隔）</label>
              <input className="admin-input" value={form.tags} onChange={(e) => set("tags", e.target.value)} />
            </div>
          </div>
          <div style={{ display: "flex", gap: "var(--sp-lg)", marginTop: "var(--sp-sm)" }}>
            <label className="admin-toggle"><input type="checkbox" checked={form.published} onChange={(e) => set("published", e.target.checked)} />发布</label>
            <label className="admin-toggle"><input type="checkbox" checked={form.featured} onChange={(e) => set("featured", e.target.checked)} />精选</label>
          </div>
        </div>

        <div className="admin-section">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--sp-md)" }}>
            <h2 className="admin-section__title" style={{ marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>正文 (Markdown)</h2>
            <div style={{ display: "flex", gap: "var(--sp-xs)" }}>
              <button type="button" className={`editor-tab${tab === "edit" ? " editor-tab--active" : ""}`} onClick={() => setTab("edit")}
                style={{ padding: "4px 12px", fontFamily: "var(--ff-mono)", fontSize: 11, border: "1px solid var(--c-border)", background: "transparent", color: tab === "edit" ? "var(--c-accent)" : "var(--c-fg-dim)", cursor: "pointer", borderRadius: "var(--radius-sm)" }}>编辑</button>
              <button type="button" className={`editor-tab${tab === "preview" ? " editor-tab--active" : ""}`} onClick={() => setTab("preview")}
                style={{ padding: "4px 12px", fontFamily: "var(--ff-mono)", fontSize: 11, border: "1px solid var(--c-border)", background: "transparent", color: tab === "preview" ? "var(--c-accent)" : "var(--c-fg-dim)", cursor: "pointer", borderRadius: "var(--radius-sm)" }}>预览</button>
            </div>
          </div>
          {tab === "edit" ? (
            <textarea className="admin-textarea" rows={18} value={form.content} onChange={(e) => updatePreview(e.target.value)} />
          ) : (
            <div style={{ minHeight: 280, padding: "var(--sp-sm)", background: "var(--c-surf-2)", border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)", fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)", color: "var(--c-fg)", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{preview}</div>
          )}
        </div>
      </form>
    </>
  );
}
