import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { prisma } from "@/lib/db";
import { ArticleClient } from "./article-client";
import "./article.css";

interface Props { params: Promise<{ slug: string }>; }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug }, select: { title: true, excerpt: true, coverImage: true } });
  if (!article) return { title: "未找到" };
  return {
    title: `${article.title} · Atelier`,
    description: article.excerpt,
    openGraph: { title: article.title, description: article.excerpt, images: [article.coverImage || ""] },
  };
}

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug } });
  if (!article || !article.published) notFound();

  // 前后篇
  const [prev, next] = await Promise.all([
    prisma.article.findFirst({
      where: { published: true, publishedAt: { lt: article.publishedAt ?? undefined } },
      orderBy: { publishedAt: "desc" },
      select: { slug: true, title: true },
    }),
    prisma.article.findFirst({
      where: { published: true, publishedAt: { gt: article.publishedAt ?? undefined } },
      orderBy: { publishedAt: "asc" },
      select: { slug: true, title: true },
    }),
  ]);

  return (
    <ArticleClient
      article={{
        ...article,
        publishedAt: article.publishedAt ? article.publishedAt.toISOString() : null,
      }}
      prev={prev}
      next={next}
    />
  );
}
