import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getPages } from '../api/pages';
import type { Page } from '../types';
import { Skeleton } from '../components/ui/Skeleton';

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

export default function ProductsPage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getPages()
      .then((data) => {
        setPages(data.filter((p) => p.status === 'published'));
      })
      .catch((err) => setError(err.response?.data?.detail || '加载失败'))
      .finally(() => setLoading(false));
  }, []);

  const extractSummary = (content: string) => {
    // eslint-disable-next-line no-useless-escape
    const plain = content.replace(/[#*`_~>!()\[\]]/g, '').trim();
    return plain.length > 150 ? plain.slice(0, 150) + '...' : plain;
  };

  return (
    <div>
      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-12"
      >
        <motion.h1
          className="text-4xl font-bold text-zinc-900 dark:text-white mb-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          产品
        </motion.h1>
        <motion.p
          className="text-zinc-500 dark:text-zinc-400 text-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          探索我们的静态页面和产品展示
        </motion.p>
      </motion.div>

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

      {/* Loading */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : pages.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-zinc-500 dark:text-zinc-400 text-center py-16"
        >
          暂无产品页面
        </motion.div>
      ) : (
        <motion.div
          variants={gridVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {pages.map((page) => (
            <motion.div key={page.id} variants={cardVariants}>
              <Link to={`/${page.slug}`}>
                <motion.div
                  whileHover={{ y: -6 }}
                  className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 h-full flex flex-col shadow-sm hover:shadow-lg transition-shadow"
                >
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
                      {page.title}
                    </h3>
                    <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed line-clamp-3">
                      {extractSummary(page.content)}
                    </p>
                  </div>
                  <div className="mt-4 flex items-center text-accent text-sm font-medium">
                    查看详情
                    <motion.svg
                      className="w-4 h-4 ml-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                      animate={{ x: [0, 4, 0] }}
                      transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </motion.svg>
                  </div>
                </motion.div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
