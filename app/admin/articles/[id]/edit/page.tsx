import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { ArticleForm } from "@/components/admin/article-form";

interface Props { params: Promise<{ id: string }>; }

export default async function EditArticlePage({ params }: Props) {
  const { id } = await params;
  const article = await prisma.article.findUnique({ where: { id: parseInt(id) } });
  if (!article) notFound();

  return (
    <div>
      <h1 className="admin-page-title">编辑文章</h1>
      <ArticleForm initial={article} />
    </div>
  );
}
