"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function AdminProductsClient({ products }: { products: any[] }) {
  const router = useRouter();

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`确定删除「${title}」？`)) return;
    await fetch(`/api/products/${id}`, { method: "DELETE" });
    router.refresh();
  };

  return (
    <div>
      <div className="admin-list-header">
        <h1 className="admin-page-title">产品管理</h1>
        <Link href="/admin/products/new" className="btn">新建作品</Link>
      </div>

      <div className="admin-card">
        {products.map((p) => (
          <div key={p.id} className="admin-list-item">
            <div>
              <div className="admin-list-item__title">{p.title}</div>
              <div className="admin-list-item__meta" style={{ marginTop: 2 }}>{p.slug}</div>
            </div>
            <span className="admin-list-item__meta">
              {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"} · {new Date(p.updatedAt).toISOString().slice(0, 10)}
            </span>
            <div className="admin-list-item__actions">
              <Link href={`/admin/products/${p.id}/edit`} className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)" }}>编辑</Link>
              <button onClick={() => handleDelete(p.id, p.title)}
                className="btn" style={{ padding: "var(--sp-2xs) var(--sp-sm)", fontSize: "var(--fs-meta)", borderColor: "oklch(0.5 0.15 30 / 0.3)", color: "oklch(0.7 0.12 30)" }}>删除</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
