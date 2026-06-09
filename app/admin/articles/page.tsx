import { prisma } from "@/lib/db";
import { AdminArticlesClient } from "./articles-client";

export const dynamic = "force-dynamic";

export default async function AdminArticlesPage() {
  const articles = await prisma.article.findMany({
    orderBy: { createdAt: "desc" },
    select: { id: true, slug: true, title: true, tags: true, published: true, updatedAt: true },
  });
  return <AdminArticlesClient articles={articles} />;
}
