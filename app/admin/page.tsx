import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function AdminDashboard() {
  const [articleCount, productCount, publishedArticles, recentArticles] = await Promise.all([
    prisma.article.count(),
    prisma.product.count(),
    prisma.article.count({ where: { published: true } }),
    prisma.article.findMany({
      orderBy: { createdAt: "desc" },
      take: 5,
      select: { id: true, title: true, createdAt: true, published: true },
    }),
  ]);

  return (
    <div>
      <h1 className="admin-page-title">仪表盘</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <p className="stat-card__label">文章总数</p>
          <p className="stat-card__value">{articleCount}</p>
          <p className="stat-card__sub">{publishedArticles} 已发布</p>
        </div>
        <div className="stat-card">
          <p className="stat-card__label">作品总数</p>
          <p className="stat-card__value">{productCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-card__label">发布率</p>
          <p className="stat-card__value">{articleCount > 0 ? Math.round((publishedArticles / articleCount) * 100) : 0}%</p>
        </div>
      </div>

      <div className="admin-card" style={{ marginTop: "var(--sp-xl)" }}>
        <h2 className="admin-card__title">最近创建</h2>
        {recentArticles.map((a) => (
          <div key={a.id} className="recent-item">
            <div>
              <span className="recent-item__title">{a.title}</span>
              <span className="recent-item__date">{new Date(a.createdAt).toISOString().slice(0, 10)}</span>
            </div>
            <span className={`recent-item__status${a.published ? "" : " recent-item__status--draft"}`}>
              {a.published ? "已发布" : "草稿"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
