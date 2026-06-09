import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { prisma } from "@/lib/db";
import { MarkdownRenderer } from "@/lib/markdown";
import { Tags } from "@/components/tags";
import { Footer } from "@/components/footer";

interface Props { params: Promise<{ slug: string }>; }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug }, select: { title: true, excerpt: true, coverImage: true } });
  if (!article) return { title: "未找到" };
  return {
    title: `${article.title} · Atelier`,
    description: article.excerpt,
    openGraph: {
      title: article.title,
      description: article.excerpt,
      images: [article.coverImage || ""],
    },
  };
}

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params;
  const article = await prisma.article.findUnique({ where: { slug } });

  if (!article || !article.published) notFound();

  return (
    <>
      {/* Hero */}
      <header style={{ position: "relative", width: "100%", height: "60vh", minHeight: "400px", overflow: "hidden" }}>
        <img
          src={article.coverImage || "/uploads/fallback-article.webp"}
          alt={article.title}
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.5) contrast(1.15)" }}
        />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, transparent 30%, var(--c-bg) 100%)" }} />
      </header>

      {/* 正文 */}
      <article style={{ position: "relative", marginTop: "-80px", zIndex: 2, paddingBottom: "var(--sp-3xl)" }}>
        <div className="container--narrow">
          <Link href="/blog" style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginBottom: "var(--sp-lg)", display: "inline-flex", alignItems: "center", gap: "var(--sp-xs)" }}>
            ← 返回笔记列表
          </Link>

          <header style={{ marginBottom: "var(--sp-xl)" }}>
            <div style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", display: "flex", gap: "var(--sp-sm)", alignItems: "center", marginBottom: "var(--sp-md)" }}>
              <span>{article.publishedAt ? new Date(article.publishedAt).toISOString().slice(0, 10) : ""}</span>
              <span className="dot" />
              <span>{article.readingTime} 分钟阅读</span>
            </div>
            <h1 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-display)", fontWeight: 400, lineHeight: 1.15, marginBottom: "var(--sp-md)" }}>
              {article.title}
            </h1>
            <Tags tags={article.tags} />
          </header>

          <div style={{ color: "var(--c-fg-dim)", lineHeight: 1.85 }}>
            <MarkdownRenderer content={article.content} />
          </div>
        </div>
      </article>

      <Footer />
    </>
  );
}
