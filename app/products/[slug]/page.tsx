import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { prisma } from "@/lib/db";
import { ProductDetailClient } from "./product-detail-client";
import "./product-detail.css";

interface Props { params: Promise<{ slug: string }>; }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const product = await prisma.product.findUnique({ where: { slug }, select: { title: true, description: true, coverImage: true } });
  if (!product) return { title: "未找到" };
  return {
    title: `${product.title} · Atelier`,
    description: product.description,
    openGraph: { title: product.title, description: product.description, images: [product.coverImage || ""] },
  };
}

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await prisma.product.findUnique({ where: { slug } });
  if (!product || !product.published) notFound();

  return <ProductDetailClient product={product} />;
}
