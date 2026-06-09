"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

interface ProductFormData {
  slug: string; title: string; description: string; content: string;
  coverImage: string; tags: string; status: string;
  featured: boolean; published: boolean;
  runtimePath: string; fileSize: number; runtimeEntry: string;
}

const empty: ProductFormData = {
  slug: "", title: "", description: "", content: "",
  coverImage: "", tags: "", status: "online",
  featured: false, published: false,
  runtimePath: "", fileSize: 0, runtimeEntry: "index.html",
};

export function ProductForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ProductFormData>(empty);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "", title: initial.title ?? "",
        description: initial.description ?? "", content: initial.content ?? "",
        coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "), status: initial.status ?? "online",
        featured: initial.featured ?? false, published: initial.published ?? false,
        runtimePath: initial.runtimePath ?? "",
        fileSize: initial.fileSize ?? 0,
        runtimeEntry: initial.runtimeEntry ?? "index.html",
      });
    }
  }, [initial]);

  const set = (f: keyof ProductFormData, v: string | number | boolean) =>
    setForm((p) => ({ ...p, [f]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true);
    const payload = { ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) };
    const apiUrl = isEdit ? `/api/products/${initial.id}` : "/api/products";
    const res = await fetch(apiUrl, {
      method: isEdit ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setSaving(false);
    if (res.ok) { router.push("/admin/products"); router.refresh(); }
    else { alert("保存失败"); }
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file || !initial) return;
    if (!file.name.endsWith(".zip")) { setUploadMsg("只接受 .zip 文件"); return; }
    setUploading(true); setUploadMsg("上传中...");
    const fd = new FormData(); fd.append("file", file);
    const res = await fetch(`/api/products/upload/${initial.id}`, { method: "POST", body: fd });
    setUploading(false);
    if (res.ok) {
      const data = await res.json();
      set("runtimePath", data.runtimePath);
      set("fileSize", data.fileSize);
      setUploadMsg(`上传成功 (${(data.fileSize / 1024 / 1024).toFixed(1)}MB)`);
    } else {
      const err = await res.json();
      setUploadMsg(err.error || "上传失败");
    }
  };

  const fmtSize = (b: number) => b > 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(1)}MB` : `${(b / 1024).toFixed(0)}KB`;

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">{isEdit ? "编辑作品" : "新建作品"}</h1>
          {isEdit && form.runtimePath && (
            <p className="admin-page-header__desc" style={{ color: "oklch(0.65 0.12 160)" }}>
              运行时路径: {form.runtimePath} | {fmtSize(form.fileSize)}
            </p>
          )}
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
          <div className="admin-form-group"><label className="admin-form-label">封面图 URL</label><input className="admin-input" value={form.coverImage} onChange={(e) => set("coverImage", e.target.value)} /></div>
          <div className="admin-form-group"><label className="admin-form-label">标签（逗号分隔）</label><input className="admin-input" value={form.tags} onChange={(e) => set("tags", e.target.value)} /></div>
          <div style={{ display: "flex", gap: "var(--sp-lg)" }}><label className="admin-toggle"><input type="checkbox" checked={form.published} onChange={(e) => set("published", e.target.checked)} />发布</label><label className="admin-toggle"><input type="checkbox" checked={form.featured} onChange={(e) => set("featured", e.target.checked)} />精选</label></div>
        </div>
        <div className="admin-section">
          <h2 className="admin-section__title">正文 (Markdown)</h2>
          <textarea className="admin-textarea" rows={10} value={form.content} onChange={(e) => set("content", e.target.value)} />
        </div>

        {isEdit && (
          <div className="admin-section">
            <h2 className="admin-section__title">上传运行时文件</h2>
            <p style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginBottom: "var(--sp-sm)" }}>
              打包为 .zip（根目录需 index.html），支持 HTML/CSS/JS/图片/字体/音频/视频/WebAssembly，最大 50MB。
            </p>
            <div style={{ display: "flex", gap: "var(--sp-sm)", alignItems: "center" }}>
              <input ref={fileRef} type="file" accept=".zip" style={{ flex: 1 }} />
              <button type="button" className="admin-btn admin-btn--primary" onClick={handleUpload} disabled={uploading}>
                {uploading ? "上传中…" : "上传"}
              </button>
            </div>
            {uploadMsg && (
              <div style={{ marginTop: "var(--sp-sm)", fontSize: "var(--fs-small)", color: uploadMsg.includes("失败") ? "oklch(0.7 0.15 30)" : "oklch(0.65 0.12 160)", fontFamily: "var(--ff-mono)" }}>
                {uploadMsg}
              </div>
            )}
            {form.runtimePath && (
              <div style={{ marginTop: "var(--sp-sm)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)" }}>
                当前托管: <code style={{ fontFamily: "var(--ff-mono)", color: "var(--c-fg)" }}>{form.runtimePath}/{form.runtimeEntry}</code>{" "}({fmtSize(form.fileSize)})
              </div>
            )}
          </div>
        )}
      </form>
    </>
  );
}
