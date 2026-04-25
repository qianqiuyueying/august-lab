import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import PageIntro from '../components/ui/PageIntro';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';

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
    <div className="space-y-10">
      <PageIntro
        eyebrow="Products"
        title="作品"
      />

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger dark:bg-danger-subtle-dark"
        >
          {error}
        </motion.div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-80" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState title="暂无作品" />
      ) : (
        <motion.div
          variants={gridVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
        >
          {products.map((product) => (
            <motion.div key={product.id} variants={cardVariants}>
              <Link to={`/products/${product.slug}`} className="group block h-full rounded-lg focus-ring">
                <article className="card-glow flex h-full flex-col overflow-hidden rounded-lg border border-border bg-paper/88 shadow-sm dark:border-border-dark dark:bg-surface-dark/88">
                  <div className="relative aspect-[4/3] overflow-hidden bg-paper-soft dark:bg-background-dark">
                    <img
                      src={product.cover_image || '/images/fallback-product.svg'}
                      alt={product.cover_image ? product.title : ''}
                      className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                      aria-hidden={!product.cover_image}
                    />
                    <div className="absolute right-3 top-3">
                      <StatusBadge status={product.status} />
                    </div>
                  </div>

                  <div className="flex flex-1 flex-col p-5">
                    <h2 className="text-xl font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                      {product.title}
                    </h2>
                    {product.description && (
                      <p className="mt-3 line-clamp-3 flex-1 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
                        {product.description}
                      </p>
                    )}
                    <div className="mt-5 border-t border-border pt-4 text-sm font-bold text-accent dark:border-border-dark">
                      查看
                    </div>
                  </div>
                </article>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
