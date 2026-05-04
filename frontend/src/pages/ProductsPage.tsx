import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import PageIntro from '../components/ui/PageIntro';
import EmptyState from '../components/ui/EmptyState';
import StatusDot from '../components/ui/StatusDot';

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const } },
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
    <div className="mx-auto max-w-7xl space-y-10">
      <section>
        <PageIntro
          eyebrow="Products"
          title="作品"
          description="从小工具到完整产品，每个都经过反复打磨"
        />
      </section>

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
        <div className="space-y-6">
          {/* Featured product (first) — full-width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Link to={`/products/${products[0].slug}`} className="group block rounded-xl focus-ring">
              <article className="lab-card grid gap-0 overflow-hidden md:grid-cols-[1.2fr_1fr]">
                <div className="relative aspect-[16/10] overflow-hidden bg-paper-soft dark:bg-background-dark md:min-h-[20rem]">
                  <img
                    src={products[0].cover_image || '/images/brand/fallback-product.webp'}
                    alt={products[0].cover_image ? products[0].title : ''}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
                    aria-hidden={!products[0].cover_image}
                  />
                  <div className="absolute right-3 top-3">
                    <StatusDot status={products[0].status} />
                  </div>
                </div>
                <div className="flex flex-col justify-center p-6 sm:p-8">
                  <h2 className="text-2xl font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                    {products[0].title}
                  </h2>
                  {products[0].description && (
                    <p className="mt-4 line-clamp-4 text-base leading-7 text-text-secondary dark:text-text-secondary-dark">
                      {products[0].description}
                    </p>
                  )}
                  <div className="mt-6 flex items-center gap-2 text-sm font-bold text-accent">
                    <span>打开作品</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                    >
                      →
                    </motion.span>
                  </div>
                </div>
              </article>
            </Link>
          </motion.div>

          {/* Remaining products — grid */}
          {products.length > 1 && (
            <motion.div
              variants={gridVariants}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
            >
              {products.slice(1).map((product) => (
                <motion.div key={product.id} variants={itemVariants}>
                  <Link to={`/products/${product.slug}`} className="group block h-full rounded-xl focus-ring">
                    <article className="lab-card flex h-full flex-col overflow-hidden transition-colors group-hover:border-accent/30">
                      <div className="relative aspect-[4/3] overflow-hidden bg-paper-soft dark:bg-background-dark">
                        <img
                          src={product.cover_image || '/images/brand/fallback-product.webp'}
                          alt={product.cover_image ? product.title : ''}
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                          aria-hidden={!product.cover_image}
                        />
                        <div className="absolute right-3 top-3">
                          <StatusDot status={product.status} />
                        </div>
                      </div>
                      <div className="flex flex-1 flex-col p-5">
                        <h3 className="text-lg font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                          {product.title}
                        </h3>
                        {product.description && (
                          <p className="mt-2 line-clamp-2 flex-1 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
                            {product.description}
                          </p>
                        )}
                        <div className="mt-4 border-t border-border pt-3 text-sm font-bold text-accent dark:border-border-dark">
                          查看 <span aria-hidden="true">→</span>
                        </div>
                      </div>
                    </article>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
