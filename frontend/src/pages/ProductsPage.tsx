import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';

function getStatusBadge(status: string) {
  if (status === 'published') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-white/90 dark:bg-zinc-900/90 backdrop-blur-sm text-emerald-600 dark:text-emerald-400 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        已上线
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-white/90 dark:bg-zinc-900/90 backdrop-blur-sm text-zinc-500 dark:text-zinc-400 shadow-sm">
      <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
      开发中
    </span>
  );
}

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
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
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mb-10"
      >
        <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1">产品</p>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-zinc-900 dark:text-white mb-1">
          项目与产品展示
        </h1>
        <p className="text-sm text-zinc-400 dark:text-zinc-500">探索我们的静态项目和产品</p>
      </motion.div>

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
          className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm"
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
              <a href={`/products/${product.slug}/`} className="block h-full">
                <motion.div
                  whileHover={{ y: -4 }}
                  className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl overflow-hidden border border-zinc-200/60 dark:border-zinc-800/60 shadow-sm hover:shadow-lg transition-all duration-300 h-full flex flex-col group card-glow"
                >
                  {/* Cover image area */}
                  <div className="aspect-[4/3] overflow-hidden relative bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900">
                    {product.cover_image ? (
                      <img
                        src={product.cover_image}
                        alt={product.title}
                        className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <svg className="w-12 h-12 text-zinc-300 dark:text-zinc-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                        </svg>
                      </div>
                    )}
                    {/* Status badge overlay */}
                    <div className="absolute top-3 right-3">
                      {getStatusBadge(product.status)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5 flex-1 flex flex-col">
                    <h3 className="text-[15px] font-semibold text-zinc-900 dark:text-white mb-1.5 tracking-tight">
                      {product.title}
                    </h3>
                    {product.description && (
                      <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed line-clamp-2 flex-1">
                        {product.description}
                      </p>
                    )}
                    <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center text-zinc-500 dark:text-zinc-400 text-sm font-medium group-hover:text-zinc-900 dark:group-hover:text-white transition-colors">
                      查看详情
                      <svg className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </div>
                  </div>
                </motion.div>
              </a>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
