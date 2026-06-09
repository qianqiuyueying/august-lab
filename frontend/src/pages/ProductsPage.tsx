import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import StatusDot from '../components/ui/StatusDot';
import TiltCard from '../components/ui/TiltCard';

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
      {/* ===== Page header ===== */}
      <section className="relative mb-6 overflow-hidden rounded-2xl" style={{ minHeight: '40vh' }}>
        <div className="absolute inset-0 z-0" style={{ margin: '-5%' }}>
          <img
            src="/images/preview/s05_luggage_bg_00001_.webp"
            alt=""
            loading="lazy"
            className="h-full w-full object-cover"
            style={{ transform: 'scale(1.1)' }}
          />
        </div>
        <div className="absolute inset-0 z-1 pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(10,15,26,.5) 100%)' }}
        />

        {/* Foreground */}
        <div className="a-float2 absolute z-2 pointer-events-none" style={{ width: 'clamp(60px,8vw,140px)', top: '10%', right: '5%' }}>
          <img src="/images/preview/s05_compass2_00001_.webp" alt="" className="w-full h-auto" />
        </div>
        <div className="a-float1 glow-cyan absolute z-2 pointer-events-none hidden sm:block" style={{ width: 'clamp(50px,7vw,120px)', top: '16%', left: '3%' }}>
          <img src="/images/preview/s05_mineral_00001_.webp" alt="" className="w-full h-auto" />
        </div>
        <div className="a-float3 absolute z-2 pointer-events-none hidden sm:block" style={{ width: 'clamp(80px,11vw,180px)', top: '42%', right: '3%' }}>
          <img src="/images/preview/s05_map_00001_.webp" alt="" className="w-full h-auto" />
        </div>

        {/* Content */}
        <div className="relative z-10 text-center px-4 py-[clamp(60px,12vh,100px)]">
          <p className="text-xs font-extrabold text-accent tracking-wider uppercase mb-2">Products</p>
          <h1 className="text-paper mb-3">作品</h1>
          <p className="text-text-muted max-w-md mx-auto text-sm sm:text-base">从小工具到完整产品，每个都经过反复打磨</p>
        </div>
      </section>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger"
        >
          {error}
        </motion.div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-72" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState title="暂无作品" />
      ) : (
        <motion.div
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
        >
          {products.map((product, i) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px 0px 0px 0px' }}
              transition={{ duration: 0.7, delay: i * 0.08, ease: [0.25, 1, 0.5, 1] }}
            >
              <Link to={`/products/${product.slug}`} className="group block h-full rounded-lg focus-ring">
                <TiltCard maxRotation={12}>
                  <article className="lab-card flex h-full flex-col overflow-hidden transition-colors group-hover:border-accent-mid/40 group-hover:shadow-lg">
                    <div className="relative aspect-[3/2] overflow-hidden bg-background">
                      <img
                        src={product.cover_image || '/images/brand/fallback-product.webp'}
                        alt={product.cover_image ? product.title : ''}
                        loading="lazy"
                        decoding="async"
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                        aria-hidden={!product.cover_image}
                      />
                      <div className="absolute right-3 top-3">
                        <StatusDot status={product.status} />
                      </div>
                    </div>
                    <div className="flex flex-1 flex-col p-5">
                      <h2 className="text-xl font-extrabold text-paper transition-colors">
                        {product.title}
                      </h2>
                      {product.description && (
                        <p className="mt-3 line-clamp-3 flex-1 text-sm leading-7 text-text-secondary">
                          {product.description}
                        </p>
                      )}
                      <div className="mt-5 flex items-center gap-2 text-sm font-bold text-accent">
                        <span>查看</span>
                        <motion.span
                          animate={{ x: [0, 4, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                        >
                          →
                        </motion.span>
                      </div>
                    </div>
                  </article>
                </TiltCard>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
