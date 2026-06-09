import { prisma } from "@/lib/db";
import { AboutClient } from "./about-client";
import "./about.css";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const siteInfo = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  const bio = siteInfo?.aboutBio ?? "一个关注光影、构图与日常物件的设计开发者。相信好的界面不是由颜色定义的，而是由对比、空间和质感定义的。";
  const links = (siteInfo?.aboutLinks as Array<{ label: string; url: string }>) ?? [];

  return <AboutClient bio={bio} links={links} />;
}
