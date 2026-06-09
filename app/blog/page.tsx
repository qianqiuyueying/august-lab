import Link from "next/link";
import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { Tags } from "@/components/tags";
import { StateCard } from "@/components/state-card";

export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const articles = await prisma.article.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, coverImage: true, tags: true, readingTime: true, publishedAt: true },
  });

  return (
    <>
      <ParallaxHero
        image="/uploads/blog-field-notes.webp"
        label="笔记"
        title="阅读 · 思考 · 记录"
        description="关于设计、技术与摄影的个人笔记"
      />

      <section style={{ padding: "var(--sp-xl) 0 var(--sp-3xl)" }}>
        <div className="container">
          {articles.length === 0 ? (
            <StateCard type="empty" />
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "2px" }}>
              {articles.map((a) => (
                <Link key={a.id} href={`/blog/${a.slug}`}
                  style={{
                    display: "block", padding: "var(--sp-xl) var(--sp-lg)",
                    border: "1px solid var(--c-border)", transition: "border-color 0.3s var(--ease-expo)",
                  }}>
                  <article style={{ display: "flex", flexDirection: "column", gap: "var(--sp-md)" }}>
                    <div style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", display: "flex", gap: "var(--sp-sm)", alignItems: "center" }}>
                      <span>{a.publishedAt ? new Date(a.publishedAt).toISOString().slice(0, 10) : ""}</span>
                      <span className="dot" />
                      <span>{a.readingTime} 分钟</span>
                    </div>
                    <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, lineHeight: 1.3 }}>{a.title}</h2>
                    <p style={{ color: "var(--c-fg-dim)", fontSize: "var(--fs-small)", lineHeight: 1.7 }}>{a.excerpt}</p>
                    <Tags tags={a.tags} />
                  </article>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
