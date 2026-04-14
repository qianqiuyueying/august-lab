import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getPage } from '../api/pages';
import type { Page } from '../types';
import ArticleContent from '../components/articles/ArticleContent';

export default function StaticPage() {
  const { slug } = useParams<{ slug: string }>();
  const [page, setPage] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    getPage(slug)
      .then(setPage)
      .catch((err) => setError(err.response?.data?.detail || '页面不存在'))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="text-gray-500 text-center py-12">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-12">{error}</div>;
  if (!page) return <div className="text-gray-500 text-center py-12">页面不存在</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <article className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 sm:p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">{page.title}</h1>
        <ArticleContent content={page.content} />
      </article>
    </div>
  );
}
