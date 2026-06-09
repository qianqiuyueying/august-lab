import { prisma } from "@/lib/db";
import { AboutEditor } from "./about-editor";

export const dynamic = "force-dynamic";

export default async function AdminAboutPage() {
  const info = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  return <AboutEditor info={info} />;
}
