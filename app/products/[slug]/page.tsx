import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { ProductDetailClient } from "./product-detail-client";

interface Props { params: Promise<{ slug: string }>; }

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await prisma.product.findUnique({ where: { slug } });
  if (!product || !product.published) notFound();

  return <ProductDetailClient product={product} />;
}
