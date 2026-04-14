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
    transition: { staggerChildren: 0.08, delayChildren: 0.15 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] as const } },
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
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-8"
        >
          <motion.h1
            className="text-4xl font-bold text-zinc-900 dark:text-white mb-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            博客
          </motion.h1>
          <motion.p
            className="text-zinc-500 dark:text-zinc-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {tag ? `标签: ${tag}` : search ? `搜索: ${search}` : '技术文章与思考'}
          </motion.p>
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
            className="text-red-600 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6"
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
            className="space-y-6"
          >
            {data?.items.map((article) => (
              <motion.div key={article.id} variants={itemVariants}>
                <ArticleCard article={article} />
              </motion.div>
            ))}

            {data?.items.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-zinc-500 dark:text-zinc-400 text-center py-12"
              >
                暂无文章
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Pagination */}
        {data && data.total > data.page_size && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex justify-center items-center gap-3 mt-8"
          >
            <motion.button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              whileTap={{ scale: page === 1 ? 1 : 0.95 }}
              className="px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              上一页
            </motion.button>
            <span className="text-sm text-zinc-500 dark:text-zinc-400">
              第 {data.page} 页 / 共 {totalPages} 页
            </span>
            <motion.button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * data.page_size >= data.total}
              whileTap={{ scale: page * data.page_size >= data.total ? 1 : 0.95 }}
              className="px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              下一页
            </motion.button>
          </motion.div>
        )}
      </div>

      {/* Sidebar */}
      <aside>
        <motion.div
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="sticky top-24 bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-5 shadow-sm"
        >
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-4">
            标签
          </h2>
          <TagList tags={tags} loading={tagsLoading} />
        </motion.div>
      </aside>
    </div>
  );
}
