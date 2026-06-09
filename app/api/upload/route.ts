import { NextResponse } from "next/server";
import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  const formData = await req.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return NextResponse.json({ error: "No file" }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  const uploadsDir = join(process.cwd(), "public", "uploads");
  await mkdir(uploadsDir, { recursive: true });

  const filename = `${Date.now()}-${file.name}`;
  const filepath = join(uploadsDir, filename);
  await writeFile(filepath, buffer);

  const url = `/uploads/${filename}`;

  const media = await prisma.media.create({
    data: { filename: file.name, url, alt: "", width: 0, height: 0 },
  });

  return NextResponse.json({ url, id: media.id });
}
