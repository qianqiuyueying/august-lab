import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';

function getStatusBadge(status: string) {
  if (status === 'published') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        已上线
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">
      <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
      开发中
    </span>
  );
}

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
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((err) => setError(err.response?.data?.detail || '加载失败'))
      .finally(() => setLoading(false));
  }, []);

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
          探索我们的静态项目和产品展示
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
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-zinc-500 dark:text-zinc-400 text-center py-16"
        >
          暂无产品
        </motion.div>
      ) : (
        <motion.div
          variants={gridVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {products.map((product) => (
            <motion.div key={product.id} variants={cardVariants}>
              <Link to={`/products/${product.slug}/`}>
                <motion.div
                  whileHover={{ y: -6 }}
                  className="bg-white dark:bg-zinc-900/50 rounded-2xl overflow-hidden border border-zinc-200/60 dark:border-zinc-800/60 shadow-sm hover:shadow-xl transition-all duration-300 h-full flex flex-col group"
                >
                  {/* Cover image area */}
                  <div className="aspect-[4/3] overflow-hidden relative">
                    {product.cover_image ? (
                      <img
                        src={product.cover_image}
                        alt={product.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <img
                        src="/images/cover-product.png"
                        alt=""
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    )}
                    {/* Status badge overlay */}
                    <div className="absolute top-3 right-3">
                      {getStatusBadge(product.status)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5 flex-1 flex flex-col">
                    <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-1.5">
                      {product.title}
                    </h3>
                    {product.description && (
                      <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed line-clamp-2 flex-1">
                        {product.description}
                      </p>
                    )}
                    <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center text-accent text-sm font-medium">
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
                  </div>

                  {/* Bottom accent line */}
                  <div className="h-1 bg-gradient-to-r from-indigo-500 to-purple-500" />
                </motion.div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
