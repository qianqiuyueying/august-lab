import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const article = await prisma.article.findUnique({ where: { id: parseInt(id) } });
  if (!article) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(article);
}

export async function PUT(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const article = await prisma.article.update({
    where: { id: parseInt(id) },
    data: {
      ...body,
      publishedAt: body.published ? new Date() : body.publishedAt,
    },
  });
  return NextResponse.json(article);
}

export async function DELETE(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await prisma.article.delete({ where: { id: parseInt(id) } });
  return NextResponse.json({ success: true });
}
