"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

interface ProductFormData {
  slug: string; title: string; description: string; content: string;
  coverImage: string; tags: string; status: string; url: string;
  featured: boolean; published: boolean;
}

const empty: ProductFormData = { slug: "", title: "", description: "", content: "", coverImage: "", tags: "", status: "online", url: "", featured: false, published: false };

export function ProductForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ProductFormData>(empty);
  const [saving, setSaving] = useState(false);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "", title: initial.title ?? "", description: initial.description ?? "",
        content: initial.content ?? "", coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "), status: initial.status ?? "online",
        url: initial.url ?? "", featured: initial.featured ?? false, published: initial.published ?? false,
      });
    }
  }, [initial]);

  const set = (f: keyof ProductFormData, v: string | boolean) => setForm((p) => ({ ...p, [f]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true);
    const payload = { ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) };
    const url = isEdit ? `/api/products/${initial.id}` : "/api/products";
    const res = await fetch(url, { method: isEdit ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    setSaving(false);
    if (res.ok) { router.push("/admin/products"); router.refresh(); } else { alert("保存失败"); }
  };

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">{isEdit ? "编辑作品" : "新建作品"}</h1>
        </div>
        <div className="admin-page-header__actions">
          <NextLink href="/admin/products" className="admin-btn">← 返回列表</NextLink>
          <button className="admin-btn admin-btn--primary" onClick={handleSubmit} disabled={saving}>{saving ? "保存中…" : "保存"}</button>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-sm)" }}>
        <div className="admin-section">
          <h2 className="admin-section__title">基本信息</h2>
          <div className="admin-form-grid">
            <div className="admin-form-group"><label className="admin-form-label">标识 (slug)</label><input className="admin-input" value={form.slug} onChange={(e) => set("slug", e.target.value)} required /></div>
            <div className="admin-form-group"><label className="admin-form-label">状态</label>
              <select className="admin-select" value={form.status} onChange={(e) => set("status", e.target.value)} style={{ width: "100%" }}>
                <option value="online">在线</option><option value="developing">开发中</option><option value="offline">已下线</option>
              </select>
            </div>
          </div>
          <div className="admin-form-group"><label className="admin-form-label">标题</label><input className="admin-input" value={form.title} onChange={(e) => set("title", e.target.value)} required /></div>
          <div className="admin-form-group"><label className="admin-form-label">简介</label><textarea className="admin-textarea" rows={3} value={form.description} onChange={(e) => set("description", e.target.value)} /></div>
          <div className="admin-form-grid">
            <div className="admin-form-group"><label className="admin-form-label">封面图 URL</label><input className="admin-input" value={form.coverImage} onChange={(e) => set("coverImage", e.target.value)} /></div>
            <div className="admin-form-group"><label className="admin-form-label">外部 URL</label><input className="admin-input" value={form.url} onChange={(e) => set("url", e.target.value)} placeholder="https://..." /></div>
          </div>
          <div className="admin-form-group"><label className="admin-form-label">标签（逗号分隔）</label><input className="admin-input" value={form.tags} onChange={(e) => set("tags", e.target.value)} /></div>
          <div style={{ display: "flex", gap: "var(--sp-lg)" }}><label className="admin-toggle"><input type="checkbox" checked={form.published} onChange={(e) => set("published", e.target.checked)} />发布</label><label className="admin-toggle"><input type="checkbox" checked={form.featured} onChange={(e) => set("featured", e.target.checked)} />精选</label></div>
        </div>
        <div className="admin-section">
          <h2 className="admin-section__title">正文 (Markdown)</h2>
          <textarea className="admin-textarea" rows={10} value={form.content} onChange={(e) => set("content", e.target.value)} />
        </div>
      </form>
    </>
  );
}
