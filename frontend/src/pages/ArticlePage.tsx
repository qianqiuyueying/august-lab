import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticle } from '../hooks/useArticles';
import ArticleContent from '../components/articles/ArticleContent';
import { formatDate } from '../utils/formatDate';

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data: article, loading, error } = useArticle(slug!);

  if (loading) return <div className="text-zinc-500 text-center py-12">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-12">{error}</div>;
  if (!article) return <div className="text-zinc-500 text-center py-12">文章不存在</div>;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button */}
      <motion.button
        onClick={() => navigate(-1)}
        whileHover={{ x: -4 }}
        className="mb-6 inline-flex items-center gap-1 text-accent hover:text-accent-hover transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        返回
      </motion.button>

      <motion.article
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 sm:p-8 shadow-sm"
      >
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-white mb-3"
        >
          {article.title}
        </motion.h1>

        <motion.div
          variants={{
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.05, delayChildren: 0.2 } },
          }}
          initial="hidden"
          animate="visible"
          className="flex flex-wrap gap-2 mb-4"
        >
          {article.tags.map((tag) => (
            <motion.span
              key={tag.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 text-xs px-2.5 py-1 rounded-full"
            >
              #{tag.name}
            </motion.span>
          ))}
        </motion.div>

        <motion.time
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-sm text-zinc-500 dark:text-zinc-400 mb-6 block"
        >
          {formatDate(article.created_at)}
        </motion.time>

        <ArticleContent content={article.content} />
      </motion.article>
    </div>
  );
}
