import Link from "next/link";
import { prisma } from "@/lib/db";
import { BlogClient } from "./blog-client";
import "./blog.css";

export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const articles = await prisma.article.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, coverImage: true, tags: true, readingTime: true, publishedAt: true },
  });

  // Aggregate all tags
  const allTags = Array.from(new Set(articles.flatMap((a) => a.tags || [])));

  // Monthly archive
  const monthMap = new Map<string, number>();
  articles.forEach((a) => {
    if (a.publishedAt) {
      const key = `${a.publishedAt.getFullYear()} 年 ${a.publishedAt.getMonth() + 1} 月`;
      monthMap.set(key, (monthMap.get(key) || 0) + 1);
    }
  });
  const archives = Array.from(monthMap.entries()).map(([label, count]) => ({ label, count }));

  return (
    <BlogClient
      articles={articles.map((a) => ({
        ...a,
        publishedAt: a.publishedAt ? a.publishedAt.toISOString() : null,
      }))}
      allTags={allTags}
      archives={archives}
    />
  );
}
