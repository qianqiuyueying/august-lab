"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface ArticleFormData {
  slug: string; title: string; excerpt: string; content: string;
  coverImage: string; tags: string; readingTime: number;
  featured: boolean; published: boolean;
}

const emptyForm: ArticleFormData = {
  slug: "", title: "", excerpt: "", content: "",
  coverImage: "", tags: "", readingTime: 3,
  featured: false, published: false,
};

export function ArticleForm({ initial }: { initial?: any }) {
  const router = useRouter();
  const [form, setForm] = useState<ArticleFormData>(emptyForm);
  const [saving, setSaving] = useState(false);
  const isEdit = !!initial;

  useEffect(() => {
    if (initial) {
      setForm({
        slug: initial.slug ?? "",
        title: initial.title ?? "",
        excerpt: initial.excerpt ?? "",
        content: initial.content ?? "",
        coverImage: initial.coverImage ?? "",
        tags: (initial.tags ?? []).join(", "),
        readingTime: initial.readingTime ?? 3,
        featured: initial.featured ?? false,
        published: initial.published ?? false,
      });
    }
  }, [initial]);

  const handleChange = (field: keyof ArticleFormData, value: string | number | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const payload = {
      ...form,
      tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
    };

    const url = isEdit ? `/api/articles/${initial.id}` : "/api/articles";
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method, headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    setSaving(false);

    if (res.ok) {
      router.push("/admin/articles");
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

  const textareaStyle: React.CSSProperties = {
    ...inputStyle, height: 280, resize: "vertical", fontFamily: "var(--ff-mono)",
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)", maxWidth: 800 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--sp-md)" }}>
        <label className="form-field">
          标识 (slug)
          <input style={inputStyle} value={form.slug} onChange={(e) => handleChange("slug", e.target.value)} required />
        </label>
        <label className="form-field">
          阅读时长 (分钟)
          <input style={inputStyle} type="number" value={form.readingTime} onChange={(e) => handleChange("readingTime", parseInt(e.target.value) || 3)} />
        </label>
      </div>

      <label className="form-field">
        标题
        <input style={inputStyle} value={form.title} onChange={(e) => handleChange("title", e.target.value)} required />
      </label>

      <label className="form-field">
        摘要
        <textarea style={{ ...inputStyle, height: 60, resize: "vertical" }} value={form.excerpt} onChange={(e) => handleChange("excerpt", e.target.value)} />
      </label>

      <label className="form-field">
        正文 (Markdown)
        <textarea style={textareaStyle} value={form.content} onChange={(e) => handleChange("content", e.target.value)} />
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
        {saving ? "保存中…" : isEdit ? "更新文章" : "创建文章"}
      </button>
    </form>
  );
}
