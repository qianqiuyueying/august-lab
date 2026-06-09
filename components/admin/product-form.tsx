"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface ProductFormData {
  slug: string; title: string; description: string; content: string;
  coverImage: string; tags: string; status: string; url: string;
  featured: boolean; published: boolean;
}

const emptyForm: ProductFormData = {
  slug: "", title: "", description: "", content: "",
  coverImage: "", tags: "", status: "draft", url: "",
  featured: false, published: false,
};

export function ProductForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ProductFormData>(emptyForm);
  const [saving, setSaving] = useState(false);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "",
        title: initial.title ?? "",
        description: initial.description ?? "",
        content: initial.content ?? "",
        coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "),
        status: initial.status ?? "draft",
        url: initial.url ?? "",
        featured: initial.featured ?? false,
        published: initial.published ?? false,
      });
    }
  }, [initial]);

  const handleChange = (field: keyof ProductFormData, value: string | number | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const payload = {
      ...form,
      tags: form.tags.split(",").map((t: string) => t.trim()).filter(Boolean),
    };

    const url = isEdit ? `/api/products/${initial.id}` : "/api/products";
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method, headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    setSaving(false);
    if (res.ok) {
      router.push("/admin/products");
      router.refresh();
    } else {
      alert("保存失败");
    }
  };

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "var(--sp-sm)", background: "var(--c-bg)",
    border: "1px solid var(--c-border)", borderRadius: "var(--radius-sm)",
    color: "var(--c-fg)", fontFamily: "var(--ff-body)", fontSize: "var(--fs-small)", outline: "none",
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)", maxWidth: 800 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "var(--sp-md)" }}>
        <label className="form-field">
          标识 (slug)
          <input style={inputStyle} value={form.slug} onChange={(e) => handleChange("slug", e.target.value)} required />
        </label>
        <label className="form-field">
          状态
          <select style={inputStyle} value={form.status} onChange={(e) => handleChange("status", e.target.value)}>
            <option value="draft">草稿</option>
            <option value="online">在线</option>
            <option value="developing">开发中</option>
            <option value="offline">已下线</option>
          </select>
        </label>
        <label className="form-field">
          外链 URL
          <input style={inputStyle} value={form.url} onChange={(e) => handleChange("url", e.target.value)} />
        </label>
      </div>

      <label className="form-field">
        标题
        <input style={inputStyle} value={form.title} onChange={(e) => handleChange("title", e.target.value)} required />
      </label>

      <label className="form-field">
        简介
        <textarea style={{ ...inputStyle, height: 60, resize: "vertical" }} value={form.description} onChange={(e) => handleChange("description", e.target.value)} />
      </label>

      <label className="form-field">
        正文 (Markdown)
        <textarea style={{ ...inputStyle, height: 280, resize: "vertical", fontFamily: "var(--ff-mono)" }} value={form.content} onChange={(e) => handleChange("content", e.target.value)} />
      </label>

      <label className="form-field">
        封面图 URL
        <input style={inputStyle} value={form.coverImage} onChange={(e) => handleChange("coverImage", e.target.value)} />
      </label>

      <label className="form-field">
        标签 (逗号分隔)
        <input style={inputStyle} value={form.tags} onChange={(e) => handleChange("tags", e.target.value)} />
      </label>

      <div style={{ display: "flex", gap: "var(--sp-lg)" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", cursor: "pointer" }}>
          <input type="checkbox" checked={form.published} onChange={(e) => handleChange("published", e.target.checked)} /> 发布
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "var(--sp-sm)", fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", cursor: "pointer" }}>
          <input type="checkbox" checked={form.featured} onChange={(e) => handleChange("featured", e.target.checked)} /> 精选
        </label>
      </div>

      <button type="submit" className="btn" disabled={saving} style={{ alignSelf: "flex-start" }}>
        {saving ? "保存中…" : isEdit ? "更新作品" : "创建作品"}
      </button>
    </form>
  );
}
