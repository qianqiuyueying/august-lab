import Link from "next/link";
import { prisma } from "@/lib/db";
import { DashboardClient } from "./dashboard-client";

export const dynamic = "force-dynamic";

export default async function AdminDashboard() {
  const [articleCount, productCount, publishedArticles, draftArticles, recentArticles, tagCounts] = await Promise.all([
    prisma.article.count(),
    prisma.product.count(),
    prisma.article.count({ where: { published: true } }),
    prisma.article.count({ where: { published: false } }),
    prisma.article.findMany({ orderBy: { createdAt: "desc" }, take: 5, select: { id: true, slug: true, title: true, tags: true, published: true, createdAt: true } }),
    (async () => {
      const articles = await prisma.article.findMany({ select: { tags: true } });
      const tagMap = new Map<string, number>();
      articles.forEach((a) => a.tags.forEach((t) => tagMap.set(t, (tagMap.get(t) || 0) + 1)));
      return Array.from(tagMap.entries()).map(([label, count]) => ({ label, count })).sort((a, b) => b.count - a.count).slice(0, 6);
    })(),
  ]);

  const allTags = tagCounts.length > 0
    ? tagCounts
    : [{ label: "设计", count: 2 }, { label: "技术", count: 1 }, { label: "摄影", count: 1 }, { label: "AI", count: 1 }, { label: "思考", count: 1 }, { label: "灵感", count: 1 }];

  return (
    <DashboardClient
      articleCount={articleCount}
      productCount={productCount}
      publishedArticles={publishedArticles}
      draftArticles={draftArticles}
      tagCount={allTags.reduce((s, t) => s + t.count, 0)}
      recentArticles={recentArticles.map((a) => ({ ...a, createdAt: a.createdAt.toISOString() }))}
      tagChart={allTags}
    />
  );
}
