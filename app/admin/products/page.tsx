import { prisma } from "@/lib/db";
import { AdminProductsClient } from "./products-client";

export const dynamic = "force-dynamic";

export default async function AdminProductsPage() {
  const products = await prisma.product.findMany({
    orderBy: { createdAt: "desc" },
    select: { id: true, slug: true, title: true, status: true, published: true, updatedAt: true },
  });
  return <AdminProductsClient products={products} />;
}
