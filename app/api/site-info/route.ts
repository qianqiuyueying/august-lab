import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  const info = await prisma.siteInfo.findFirst({ where: { id: 1 } });
  if (!info) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(info);
}

export async function PUT(req: Request) {
  const body = await req.json();
  const info = await prisma.siteInfo.upsert({
    where: { id: 1 },
    update: body,
    create: { id: 1, ...body },
  });
  return NextResponse.json(info);
}
