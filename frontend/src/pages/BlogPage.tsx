import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticles } from '../hooks/useArticles';
import { useTags } from '../hooks/useTags';
import ArticleCard from '../components/articles/ArticleCard';
import TagList from '../components/tags/TagList';
import SearchBar from '../components/search/SearchBar';
import { Skeleton } from '../components/ui/Skeleton';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] as const } },
};

export default function BlogPage() {
  const [searchParams] = useSearchParams();
  const [page, setPage] = useState(1);
  const tag = searchParams.get('tag') || undefined;
  const search = searchParams.get('search') || undefined;

  const { data, loading, error } = useArticles(page, 10, tag, search);
  const { data: tags, loading: tagsLoading } = useTags();

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main content */}
      <div className="lg:col-span-3">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="mb-8"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1">
            博客
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-zinc-900 dark:text-white mb-1">
            {tag ? `标签: ${tag}` : search ? `搜索: ${search}` : '技术文章与思考'}
          </h1>
          {data && !tag && !search && (
            <p className="text-sm text-zinc-400 dark:text-zinc-500">{data.total} 篇文章</p>
          )}
        </motion.div>

        {/* Search */}
        <div className="mb-6">
          <SearchBar />
        </div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-red-600 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6 text-sm"
          >
            {error}
          </motion.div>
        )}

        {/* Article list */}
        {loading ? (
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        ) : (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-5"
          >
            {data?.items.map((article, index) => (
              <motion.div key={article.id} variants={itemVariants}>
                <ArticleCard
                  article={article}
                  variant={page === 1 && index === 0 ? 'featured' : 'default'}
                />
              </motion.div>
            ))}

            {data?.items.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm"
              >
                暂无文章
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Pagination */}
        {data && data.total > data.page_size && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex justify-center items-center gap-3 mt-10"
          >
            <motion.button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              whileTap={{ scale: page === 1 ? 1 : 0.96 }}
              className="px-4 py-2 rounded-full border border-zinc-200 dark:border-zinc-800 text-sm font-medium text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              上一页
            </motion.button>
            <span className="text-sm text-zinc-400 dark:text-zinc-500 tabular-nums">
              {data.page} / {totalPages}
            </span>
            <motion.button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * data.page_size >= data.total}
              whileTap={{ scale: page * data.page_size >= data.total ? 1 : 0.96 }}
              className="px-4 py-2 rounded-full border border-zinc-200 dark:border-zinc-800 text-sm font-medium text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              下一页
            </motion.button>
          </motion.div>
        )}
      </div>

      {/* Sidebar */}
      <aside>
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
          className="sticky top-20 bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-5 shadow-sm"
        >
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-4">
            标签
          </h2>
          <TagList tags={tags} loading={tagsLoading} />
        </motion.div>
      </aside>
    </div>
  );
}
