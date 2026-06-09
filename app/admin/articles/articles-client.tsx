"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function AdminArticlesClient({ articles }: { articles: any[] }) {
  const router = useRouter();

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`确定删除「${title}」？`)) return;
    await fetch(`/api/articles/${id}`, { method: "DELETE" });
    router.refresh();
  };

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">文章管理</h1>
          <p className="admin-page-header__desc">创建、编辑和管理所有文章内容。</p>
        </div>
        <div className="admin-page-header__actions">
          <Link href="/admin/articles/new" className="admin-btn admin-btn--primary">新建文章</Link>
        </div>
      </div>

      <div className="admin-panel">
        <div className="admin-panel__body" style={{ padding: 0 }}>
          {articles.map((a) => (
            <div key={a.id} className="admin-list-item" style={{ gridTemplateColumns: "minmax(0, 1.2fr) 180px 100px 120px 120px" }}>
              <div>
                <div className="admin-list-item__title">{a.title}</div>
                <div className="admin-list-item__meta" style={{ marginTop: 2 }}>{a.slug}</div>
              </div>
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                {(a.tags || []).map((t: string) => <span key={t} className="recent-item__tag">{t}</span>)}
              </div>
              <span className="admin-list-item__meta" style={a.published ? { color: "oklch(0.65 0.12 160)" } : {}}>
                {a.published ? "已发布" : "草稿"}
              </span>
              <span className="admin-list-item__meta">{new Date(a.updatedAt).toISOString().slice(0, 10)}</span>
              <div className="admin-list-item__actions">
                <Link href={`/admin/articles/${a.id}/edit`} className="admin-btn" style={{ padding: "4px 12px", fontSize: "var(--fs-meta)", height: 28 }}>编辑</Link>
                <button onClick={() => handleDelete(a.id, a.title)} className="admin-btn" style={{ padding: "4px 12px", fontSize: "var(--fs-meta)", height: 28, color: "oklch(0.7 0.15 30)", borderColor: "oklch(0.55 0.15 20 / 0.3)" }}>删除</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
