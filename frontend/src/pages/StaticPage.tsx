import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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

  if (loading) return <div className="py-12 text-center text-text-muted dark:text-text-muted-dark">加载中...</div>;
  if (error) return <div className="py-12 text-center text-danger">{error}</div>;
  if (!page) return <div className="py-12 text-center text-text-muted dark:text-text-muted-dark">页面不存在</div>;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto max-w-4xl"
    >
      {page.content_type === 'html' ? (
        <div className="overflow-hidden rounded-lg border border-border shadow-sm dark:border-border-dark">
          <div dangerouslySetInnerHTML={{ __html: page.content }} />
        </div>
      ) : (
        <article className="paper-panel-strong p-6 sm:p-9">
          <h1 className="mb-8 text-4xl font-extrabold text-text-primary dark:text-text-primary-dark">{page.title}</h1>
          <ArticleContent content={page.content} />
        </article>
      )}
    </motion.div>
  );
}
