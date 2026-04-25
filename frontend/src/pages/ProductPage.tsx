import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getProduct } from '../api/products';
import type { Product } from '../types';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';

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

  if (loading) return <EmptyState title="作品加载中" />;
  if (error) return <EmptyState title="作品读取失败" description={error} />;
  if (!product) return <EmptyState title="作品不存在" />;

  return (
    <div className="mx-auto max-w-5xl">
      <motion.button
        onClick={() => navigate(-1)}
        whileHover={{ x: -3 }}
        className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-text-muted transition-colors hover:text-accent dark:text-text-muted-dark"
      >
        <span aria-hidden="true">←</span>
        返回上一页
      </motion.button>

      <motion.article
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="overflow-hidden rounded-lg border border-border bg-paper shadow-sm dark:border-border-dark dark:bg-surface-dark"
      >
        <div className="relative">
          <img
            src={product.cover_image || '/images/brand/fallback-product.png'}
            alt={product.cover_image ? product.title : ''}
            className="aspect-[16/8] w-full object-cover"
            aria-hidden={!product.cover_image}
          />
          <div className="absolute right-4 top-4">
            <StatusBadge status={product.status} />
          </div>
        </div>

        <div className="p-6 sm:p-10">
          <div>
            <p className="section-label mb-3">Product note</p>
            <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl">
              {product.title}
            </h1>
            <p className="mt-6 text-lg leading-9 text-text-secondary dark:text-text-secondary-dark">
              {product.description}
            </p>
          </div>
        </div>
      </motion.article>
    </div>
  );
}
