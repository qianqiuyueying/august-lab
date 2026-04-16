import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getProduct } from '../api/products';
import type { Product } from '../types';

export default function ProductPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    getProduct(slug)
      .then(setProduct)
      .catch((err) => setError(err.response?.data?.detail || '产品不存在'))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="text-zinc-500 text-center py-12">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-12">{error}</div>;
  if (!product) return <div className="text-zinc-500 text-center py-12">产品不存在</div>;

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
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 overflow-hidden shadow-sm"
      >
        {/* Cover image */}
        {product.cover_image ? (
          <img
            src={product.cover_image}
            alt={product.title}
            className="w-full aspect-video object-cover"
          />
        ) : (
          <div className="w-full aspect-video bg-gradient-to-br from-violet-400 to-purple-500" />
        )}

        {/* Content */}
        <div className="p-6 sm:p-8">
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl font-bold text-zinc-900 dark:text-white mb-3"
          >
            {product.title}
          </motion.h1>

          {/* Status badge */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="mb-4"
          >
            {product.status === 'published' ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                已上线
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                开发中
              </span>
            )}
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-zinc-600 dark:text-zinc-400 leading-relaxed text-lg"
          >
            {product.description}
          </motion.p>
        </div>
      </motion.article>
    </div>
  );
}
