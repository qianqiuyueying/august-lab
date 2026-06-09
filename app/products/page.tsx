import Link from "next/link";
import type { Metadata } from "next";
import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { StateCard } from "@/components/state-card";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "作品 · Atelier",
    description: "个人项目和实验性的数字作品",
  };
}

export default async function ProductsPage() {
  const products = await prisma.product.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, description: true, coverImage: true, status: true, tags: true },
  });

  return (
    <>
      <ParallaxHero
        image="/uploads/plaster-geometric.png"
        label="作品"
        title="创作 · 实验 · 工具"
        description="个人项目和实验性的数字作品"
      />

      <section style={{ padding: "var(--sp-xl) 0 var(--sp-3xl)" }}>
        <div className="container">
          {products.length === 0 ? (
            <StateCard type="empty" />
          ) : (
            <div className="gallery-grid" style={{ display: "grid", gridTemplateColumns: "1.4fr 0.7fr 1fr", gridAutoRows: "240px", gap: "2px" }}>
              {products.map((p) => (
                <Link key={p.id} href={`/products/${p.slug}`}
                  style={{ position: "relative", overflow: "hidden", background: "var(--c-bg)", cursor: "pointer" }}>
                  <img src={p.coverImage || "/uploads/metal-ruler.png"} alt={p.title}
                    style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.35) contrast(1.2)", transition: "transform 0.7s var(--ease-expo)" }} />
                  <div className="works-card-info">
                    <h2 style={{ fontFamily: "var(--ff-display)", fontSize: "var(--fs-h3)", fontWeight: 400, color: "#fff" }}>{p.title}</h2>
                    <p style={{ fontSize: "var(--fs-small)", color: "oklch(0.65 0.01 270 / 0.55)" }}>{p.description}</p>
                  </div>
                  <span className="works-card-status">
                    {p.status === "online" ? "在线" : p.status === "developing" ? "开发中" : "已下线"}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
