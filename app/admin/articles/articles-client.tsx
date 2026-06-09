"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Tags } from "@/components/tags";

export function AdminArticlesClient({ articles }: { articles: any[] }) {
  const router = useRouter();

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`确定删除「${title}」？`)) return;
    await fetch(`/api/articles/${id}`, { method: "DELETE" });
    router.refresh();
  };

  return (
    <div>
      <div className="admin-list-header">
        <h1 className="admin-page-title">文章管理</h1>
        <Link href="/admin/articles/new" className="btn">新建文章</Link>
      </div>

      <div className="admin-card">
        {articles.map((a) => (
          <div key={a.id} className="admin-list-item">
            <div>
              <div className="admin-list-item__title">{a.title}</div>
              <div style={{ marginTop: 4 }}><Tags tags={a.tags} /></div>
            </div>
            <span className="admin-list-item__meta">
              {a.published ? "已发布" : "草稿"} · {new Date(a.updatedAt).toISOString().slice(0, 10)}
            </span>
            <div className="admin-list-item__actions">
              <Link href={`/admin/articles/${a.id}/edit`} className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)" }}>编辑</Link>
              <button onClick={() => handleDelete(a.id, a.title)}
                className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)", borderColor: "oklch(0.5 0.15 30 / 0.3)", color: "oklch(0.7 0.12 30)" }}>删除</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
