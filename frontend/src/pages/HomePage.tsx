import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import TiltCard from '../components/ui/TiltCard';
import GlassPanel from '../components/ui/GlassPanel';

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.42, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const floatingShapes = [
  { top: '8%', left: '12%', w: 80, h: 80, rotate: 45, color: 'bg-accent/5', duration: 6 },
  { top: '15%', right: '18%', w: 120, h: 120, rotate: 0, color: 'bg-clay/5', duration: 9, borderRadius: '50%' },
  { top: '55%', left: '6%', w: 60, h: 60, rotate: 30, color: 'bg-blueprint/5', duration: 7 },
  { top: '40%', right: '10%', w: 100, h: 40, rotate: -15, color: 'bg-accent/4', duration: 11 },
  { bottom: '10%', left: '25%', w: 90, h: 90, rotate: 60, color: 'bg-clay/4', duration: 8, borderRadius: '50%' },
];

export default function HomePage() {
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0.7]);
  const heroY = useTransform(scrollY, [0, 300], [0, -40]);

  const { data: articles, loading } = useArticles(1, 3);
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((data) => setProducts(data.slice(0, 3)))
      .catch(() => {})
      .finally(() => setProductsLoading(false));
  }, []);

  return (
    <div className="space-y-24">
      {/* Hero */}
      <motion.section style={{ opacity: heroOpacity, y: heroY }} className="relative -mx-4 flex min-h-[70vh] items-center overflow-hidden rounded-lg sm:-mx-6 lg:-mx-8">
        {/* Animated gradient background */}
        <motion.div
          className="absolute inset-0"
          animate={{
            background: [
              'radial-gradient(circle at 20% 50%, rgba(37,99,235,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(14,165,233,0.06) 0%, transparent 50%), radial-gradient(circle at 40% 80%, rgba(99,102,241,0.05) 0%, transparent 50%)',
              'radial-gradient(circle at 60% 30%, rgba(37,99,235,0.08) 0%, transparent 50%), radial-gradient(circle at 20% 70%, rgba(14,165,233,0.06) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(99,102,241,0.05) 0%, transparent 50%)',
              'radial-gradient(circle at 20% 50%, rgba(37,99,235,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(14,165,233,0.06) 0%, transparent 50%), radial-gradient(circle at 40% 80%, rgba(99,102,241,0.05) 0%, transparent 50%)',
            ],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
        />

        {/* Floating shapes */}
        {floatingShapes.map((shape, i) => (
          <motion.div
            key={i}
            className={`absolute ${shape.color} rounded-lg`}
            style={{
              top: shape.top,
              left: shape.left,
              right: shape.right,
              bottom: shape.bottom,
              width: shape.w,
              height: shape.h,
              borderRadius: shape.borderRadius || '12px',
            }}
            animate={{
              y: [0, -20, 5, -15, 0],
              rotate: [shape.rotate, shape.rotate + 15, shape.rotate - 10, shape.rotate + 5, shape.rotate],
              opacity: [0.4, 0.7, 0.5, 0.8, 0.4],
            }}
            transition={{ duration: shape.duration, repeat: Infinity, ease: 'easeInOut' }}
          />
        ))}

        {/* Grid pattern */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(37,99,235,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(37,99,235,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '36px 36px',
          }}
        />

        {/* Hero glass card */}
        <TiltCard className="relative z-10 mx-auto w-full max-w-5xl px-6 py-24 sm:px-10 sm:py-32 lg:px-14 lg:py-36">
          <GlassPanel className="relative overflow-hidden p-10 sm:p-14 lg:p-16">
            {/* Floating visual elements */}
            <motion.div
              className="absolute top-0 right-12 h-40 w-40 rounded-full bg-gradient-to-br from-accent/10 to-clay/10 blur-xl"
              animate={{ scale: [1, 1.3, 0.9, 1.1, 1], x: [0, 12, -8, 5, 0], y: [0, -10, 6, -12, 0] }}
              transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
              className="absolute bottom-0 right-32 h-28 w-28 rounded-full bg-gradient-to-br from-blueprint/8 to-clay/8 blur-lg"
              animate={{ scale: [1, 1.15, 0.85, 1], x: [0, -10, 8, 0], y: [0, 8, -5, 0] }}
              transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
            />

            {/* Code editor card */}
            <motion.div
              initial={{ opacity: 0, x: 20, y: -10, rotate: -3 }}
              animate={{ opacity: 1, x: 0, y: 0, rotate: -3 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className="absolute right-16 top-6 z-10 w-48 rounded-xl border border-border/60 bg-paper/80 p-3 shadow-sm dark:border-border-dark/60 dark:bg-surface-dark/80 backdrop-blur-sm"
            >
              <div className="mb-3 flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
                <div className="h-2.5 w-2.5 rounded-full bg-yellow-400/70" />
                <div className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
              </div>
              <div className="space-y-2">
                <div className="flex gap-2"><div className="w-5 h-2 rounded-full bg-clay/40" /><div className="flex-1 h-2 rounded-full bg-border/60" /></div>
                <div className="ml-3 flex gap-2"><div className="w-3 h-2 rounded-full bg-accent/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                <div className="ml-3 flex gap-2"><div className="w-7 h-2 rounded-full bg-blueprint/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                <div className="flex gap-2"><div className="w-6 h-2 rounded-full bg-clay/40" /><div className="flex-1 h-2 rounded-full bg-border/60" /></div>
                <div className="ml-3 flex gap-2"><div className="w-4 h-2 rounded-full bg-accent/30" /><div className="w-10 h-2 rounded-full bg-border/30" /></div>
              </div>
            </motion.div>

            {/* Tag card */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotate: 5 }}
              animate={{ opacity: 1, x: 0, rotate: 5 }}
              transition={{ delay: 1, duration: 0.6 }}
              className="absolute right-6 top-36 z-10 w-36 rounded-xl border border-border/60 bg-paper/80 p-3 shadow-sm dark:border-border-dark/60 dark:bg-surface-dark/80 backdrop-blur-sm"
            >
              <div className="mb-2 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">最近标签</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="rounded-full bg-accent/10 px-2 py-0.5 text-[9px] font-bold text-accent">#React</span>
                <span className="rounded-full bg-clay/10 px-2 py-0.5 text-[9px] font-bold text-clay">#API</span>
                <span className="rounded-full bg-blueprint/10 px-2 py-0.5 text-[9px] font-bold text-blueprint">#CSS</span>
                <span className="rounded-full bg-accent/10 px-2 py-0.5 text-[9px] font-bold text-accent">#Rust</span>
                <span className="rounded-full bg-clay/10 px-2 py-0.5 text-[9px] font-bold text-clay">#Docker</span>
              </div>
            </motion.div>

            {/* Activity bar */}
            <motion.div
              initial={{ opacity: 0, y: 20, rotate: 2 }}
              animate={{ opacity: 1, y: 0, rotate: 2 }}
              transition={{ delay: 1.2, duration: 0.6 }}
              className="absolute right-8 bottom-8 z-10 flex h-16 items-end gap-1"
            >
              {[3, 5, 2, 7, 4, 6, 3].map((h, i) => (
                <motion.div
                  key={i}
                  className="w-3 rounded-sm bg-accent/20"
                  style={{ height: h * 6 }}
                  animate={{ scaleY: [1, 1.4, 0.8, 1.2, 1] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: i * 0.2 }}
                />
              ))}
            </motion.div>

            {/* Rotating ring */}
            <motion.div
              className="absolute right-[25rem] top-28 h-16 w-16 rounded-full border-[3px] border-accent/8 dark:border-accent/10"
              animate={{ rotate: 360, opacity: [0.3, 0.5, 0.3] }}
              transition={{ rotate: { duration: 20, repeat: Infinity, ease: 'linear' }, opacity: { duration: 5, repeat: Infinity } }}
            />

            {/* Dot */}
            <motion.div
              className="absolute top-20 left-1/2 h-2 w-2 rounded-full bg-accent/40"
              animate={{ y: [0, -16, 0], opacity: [0.3, 0.7, 0.3] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            />

            {/* Cross */}
            <motion.div
              className="absolute right-[23rem] bottom-16 text-2xl font-bold text-accent/15"
              animate={{ rotate: [0, 90, 180, 270, 360] }}
              transition={{ duration: 18, repeat: Infinity, ease: 'linear' }}
            >
              +
            </motion.div>

            {/* Content */}
            <div className="relative z-20 max-w-xl">
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15, duration: 0.6 }}
                className="hero-label mb-4"
              >
                Personal technical notebook
              </motion.p>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.6 }}
                className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl"
              >
                写下实验、系统和<br />
                <span className="text-gradient">那些慢慢成形的想法</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.42, duration: 0.6 }}
                className="mt-5 max-w-md text-base leading-7 text-text-secondary dark:text-text-secondary-dark"
              >
                一个记录技术探索、产品实践和长期思考的个人空间。
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.55, duration: 0.6 }}
                className="mt-8 flex flex-wrap gap-3"
              >
                <Link to="/blog" className="lab-button">
                  阅读笔记 <span aria-hidden="true">→</span>
                </Link>
                <Link to="/products" className="lab-button-secondary">
                  查看作品
                </Link>
              </motion.div>
            </div>
          </GlassPanel>
        </TiltCard>
      </motion.section>

      {/* Latest articles */}
      <section>
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-label mb-3">Latest notes</p>
            <h2 className="text-3xl font-extrabold text-text-primary dark:text-text-primary-dark">最新笔记</h2>
          </div>
          <Link to="/blog" className="lab-button-secondary w-fit">
            查看全部文章
          </Link>
        </div>

        {loading ? (
          <div className="space-y-5">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-44" />
            ))}
          </div>
        ) : articles?.items.length ? (
          <div className="space-y-5">
            {articles.items.map((article, i) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06 }}
              >
                <ArticleCard article={article} variant={i === 0 ? 'featured' : 'default'} />
              </motion.div>
            ))}
          </div>
        ) : (
          <EmptyState title="暂无文章" />
        )}
      </section>

      {/* Products */}
      <section>
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-label mb-3">Small products</p>
            <h2 className="text-3xl font-extrabold text-text-primary dark:text-text-primary-dark">作品</h2>
          </div>
          <Link to="/products" className="lab-button-secondary w-fit">
            查看作品集
          </Link>
        </div>

        {productsLoading ? (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-72" />
            ))}
          </div>
        ) : products.length ? (
          <motion.div
            variants={gridVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 gap-5 md:grid-cols-3"
          >
            {products.map((product) => (
              <motion.div key={product.id} variants={itemVariants}>
                <Link to={`/products/${product.slug}`} className="group block h-full rounded-lg focus-ring">
                  <article className="flex h-full flex-col overflow-hidden rounded-lg border border-border bg-paper/88 shadow-sm dark:border-border-dark dark:bg-surface-dark/88">
                    <div className="relative aspect-[4/3] overflow-hidden bg-paper-soft dark:bg-background-dark">
                      <img
                        src={product.cover_image || '/images/brand/fallback-product.webp'}
                        alt={product.cover_image ? product.title : ''}
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                        aria-hidden={!product.cover_image}
                      />
                      <div className="absolute right-3 top-3">
                        <StatusBadge status={product.status} />
                      </div>
                    </div>
                    <div className="flex flex-1 flex-col p-5">
                      <h3 className="text-xl font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                        {product.title}
                      </h3>
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
        ) : (
          <EmptyState title="暂无作品" />
        )}
      </section>
    </div>
  );
}
