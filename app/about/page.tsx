import { prisma } from "@/lib/db";
import { AboutClient } from "./about-client";
import "./about.css";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const siteInfo = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  const bio = siteInfo?.aboutBio ?? "一个喜欢动手折腾的创作者。写代码、拍照片、做实验是日常。";
  const links = (siteInfo?.aboutLinks as Array<{ label: string; url: string }>) ?? [];

  return <AboutClient bio={bio} links={links} />;
}
