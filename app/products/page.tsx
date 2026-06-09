import { prisma } from "@/lib/db";
import { ProductsClient } from "./products-client";
import "./products.css";

export const dynamic = "force-dynamic";

export default async function ProductsPage() {
  const products = await prisma.product.findMany({
    where: { published: true },
    orderBy: { publishedAt: "desc" },
    select: { id: true, slug: true, title: true, description: true, coverImage: true, status: true, tags: true },
  });
  return <ProductsClient products={products} />;
}
