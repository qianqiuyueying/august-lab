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

  if (loading) return <div className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-16 text-sm">{error}</div>;
  if (!product) return <div className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm">产品不存在</div>;

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
        {/* Cover image */}
        {product.cover_image ? (
          <div className="w-full aspect-[21/9] overflow-hidden">
            <img
              src={product.cover_image}
              alt={product.title}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="w-full aspect-[21/9] bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900 flex items-center justify-center">
            <svg className="w-16 h-16 text-zinc-300 dark:text-zinc-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={0.75}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
            </svg>
          </div>
        )}

        {/* Content */}
        <div className="p-6 sm:p-10">
          {/* Status badge */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.05 }}
            className="mb-4"
          >
            {product.status === 'published' ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                已上线
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                开发中
              </span>
            )}
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-2xl sm:text-3xl lg:text-4xl font-bold text-zinc-900 dark:text-white mb-5 leading-tight tracking-tight"
          >
            {product.title}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="text-zinc-500 dark:text-zinc-400 leading-relaxed text-base"
          >
            {product.description}
          </motion.p>
        </div>
      </motion.article>
    </div>
  );
}
