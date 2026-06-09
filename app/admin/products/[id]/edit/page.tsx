import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { ProductForm } from "@/components/admin/product-form";

interface Props { params: Promise<{ id: string }>; }

export default async function EditProductPage({ params }: Props) {
  const { id } = await params;
  const product = await prisma.product.findUnique({ where: { id: parseInt(id) } });
  if (!product) notFound();

  return (
    <div>
      <h1 className="admin-page-title">编辑作品</h1>
      <ProductForm initial={product} />
    </div>
  );
}
