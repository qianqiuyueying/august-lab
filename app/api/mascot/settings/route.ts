import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  let settings = await prisma.mascotSettings.findFirst({ where: { id: 1 } });
  if (!settings) {
    settings = await prisma.mascotSettings.create({
      data: { id: 1 },
    });
  }
  return NextResponse.json(settings);
}

export async function PUT(req: Request) {
  const body = await req.json();
  const settings = await prisma.mascotSettings.upsert({
    where: { id: 1 },
    update: body,
    create: { id: 1, ...body },
  });
  return NextResponse.json(settings);
}
