import { prisma } from "@/lib/db";
import { HomeClient } from "./home-client";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [articles, products] = await Promise.all([
    prisma.article.findMany({
      where: { published: true, featured: true },
      orderBy: { publishedAt: "desc" },
      take: 3,
      select: { id: true, slug: true, title: true, excerpt: true, tags: true, readingTime: true, publishedAt: true },
    }),
    prisma.product.findMany({
      where: { published: true, featured: true },
      orderBy: { publishedAt: "desc" },
      take: 3,
      select: { id: true, slug: true, title: true, description: true, coverImage: true, status: true },
    }),
  ]);

  return <HomeClient articles={articles} products={products} />;
}
