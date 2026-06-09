import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  const articles = await prisma.article.findMany({
    orderBy: { createdAt: "desc" },
    select: { id: true, slug: true, title: true, excerpt: true, tags: true, published: true, featured: true, readingTime: true, createdAt: true, updatedAt: true },
  });
  return NextResponse.json(articles);
}

export async function POST(req: Request) {
  const body = await req.json();
  const article = await prisma.article.create({
    data: {
      ...body,
      publishedAt: body.published ? new Date() : null,
    },
  });
  return NextResponse.json(article, { status: 201 });
}
