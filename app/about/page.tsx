import { prisma } from "@/lib/db";
import { ParallaxHero } from "@/components/parallax-hero";
import { Footer } from "@/components/footer";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const siteInfo = await prisma.siteInfo.findFirst({ where: { id: 1 } });

  const bio = siteInfo?.aboutBio ?? "光影之间的创作者。";
  const links = (siteInfo?.aboutLinks as Array<{ label: string; url: string }>) ?? [];

  return (
    <>
      <ParallaxHero
        image="/uploads/about-workbench.webp"
        label="关于"
        title="光影之间"
        description="记录、实验与创作"
      />

      <section style={{ padding: "var(--sp-2xl) 0 var(--sp-3xl)" }}>
        <div className="container--narrow">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--sp-2xl)" }}>
            <div>
              <p style={{ fontSize: "var(--fs-body)", lineHeight: 1.85, color: "var(--c-fg-dim)", whiteSpace: "pre-line" }}>
                {bio}
              </p>
            </div>

            <div>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-sm)" }}>
                {links.map((link, i) => (
                  <a key={i} href={link.url} target="_blank" rel="noopener noreferrer"
                    style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--sp-sm) 0", borderBottom: "1px solid var(--c-border)" }}>
                    <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-small)", color: "var(--c-fg-dim)" }}>{link.label}</span>
                    <span style={{ fontFamily: "var(--ff-mono)", fontSize: "var(--fs-meta)", color: "var(--c-muted)" }}>→</span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
