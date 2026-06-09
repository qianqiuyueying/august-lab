import { NextResponse } from "next/server";
import { mkdir } from "fs/promises";
import { join } from "path";
import { prisma } from "@/lib/db";
import { validatePackage, extractPackage, MAX_ZIP_SIZE } from "@/lib/upload-validator";

export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const product = await prisma.product.findUnique({ where: { id: parseInt(id) } });
  if (!product) {
    return NextResponse.json({ error: "作品不存在" }, { status: 404 });
  }

  const formData = await req.formData();
  const file = formData.get("file") as File | null;

  if (!file) {
    return NextResponse.json({ error: "请选择文件" }, { status: 400 });
  }

  if (!file.name.endsWith(".zip")) {
    return NextResponse.json({ error: "请上传 .zip 文件" }, { status: 400 });
  }

  if (file.size > MAX_ZIP_SIZE) {
    return NextResponse.json({
      error: `文件大小 ${(file.size / 1024 / 1024).toFixed(1)}MB 超过限制 ${MAX_ZIP_SIZE / 1024 / 1024}MB`,
    }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  const validation = validatePackage(buffer, product.slug);
  if (!validation.ok) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  const targetDir = join(process.cwd(), "public", "products", product.slug);
  await mkdir(targetDir, { recursive: true });
  extractPackage(buffer, targetDir);

  await prisma.product.update({
    where: { id: parseInt(id) },
    data: {
      runtimePath: `products/${product.slug}`,
      fileSize: file.size,
      runtimeEntry: "index.html",
    },
  });

  return NextResponse.json({
    success: true,
    runtimePath: `products/${product.slug}`,
    fileSize: file.size,
  });
}
