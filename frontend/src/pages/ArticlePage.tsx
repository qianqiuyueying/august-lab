import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticle } from '../hooks/useArticles';
import ArticleContent from '../components/articles/ArticleContent';
import { formatDate } from '../utils/formatDate';
import { estimateReadingTime } from '../utils/readingTime';

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data: article, loading, error } = useArticle(slug!);

  if (loading) return <div className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-16 text-sm">{error}</div>;
  if (!article) return <div className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm">文章不存在</div>;

  const readingTime = estimateReadingTime(article.summary);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button */}
      <motion.button
        onClick={() => navigate(-1)}
        whileHover={{ x: -4 }}
        className="mb-8 inline-flex items-center gap-1.5 text-sm text-zinc-400 dark:text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        返回
      </motion.button>

      <motion.article
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 shadow-sm overflow-hidden"
      >
        {/* Cover image (if exists) */}
        {article.cover_image && (
          <div className="w-full aspect-[21/9] overflow-hidden">
            <img
              src={article.cover_image}
              alt={article.title}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        {/* Content */}
        <div className="p-6 sm:p-10">
          {/* Tags */}
          {article.tags.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-wrap gap-2 mb-4"
            >
              {article.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400"
                >
                  #{tag.name}
                </span>
              ))}
            </motion.div>
          )}

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.05 }}
            className="text-2xl sm:text-3xl lg:text-4xl font-bold text-zinc-900 dark:text-white mb-5 leading-tight tracking-tight"
          >
            {article.title}
          </motion.h1>

          {/* Meta info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="flex flex-wrap items-center gap-4 text-sm text-zinc-400 dark:text-zinc-500 mb-8 pb-8 border-b border-zinc-100 dark:border-zinc-800"
          >
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
              </svg>
              {formatDate(article.created_at)}
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {readingTime} min read
            </span>
          </motion.div>

          {/* Article body */}
          <div className="border-l-2 border-zinc-100 dark:border-zinc-800 pl-6 sm:pl-8">
            <ArticleContent content={article.content} />
          </div>
        </div>
      </motion.article>
    </div>
  );
}
