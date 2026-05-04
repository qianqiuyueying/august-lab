import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';
import TickDivider from '../components/ui/TickDivider';
import StatusDot from '../components/ui/StatusDot';

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

export default function HomePage() {
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0.7]);
  const heroY = useTransform(scrollY, [0, 300], [0, -40]);

  const { data: articles, loading } = useArticles(1, 5);
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
      {/* Hero — split layout */}
      <motion.section
        style={{ opacity: heroOpacity, y: heroY }}
        className="relative -mx-4 min-h-[75vh] overflow-hidden rounded-lg sm:-mx-6 lg:-mx-8"
      >
        {/* Dot grid + halos background */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-clay/5" />

        {/* Content — split */}
        <div className="relative z-10 mx-auto flex max-w-7xl flex-col gap-10 px-6 py-16 lg:flex-row lg:items-center lg:px-8 lg:py-24">
          {/* Left: title + CTA */}
          <div className="flex-1 space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <SectionNumber number="001" label="首页" />
            </motion.div>

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
              className="max-w-md text-base leading-7 text-text-secondary dark:text-text-secondary-dark"
            >
              一个记录技术探索、产品实践和长期思考的个人空间。
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55, duration: 0.6 }}
              className="flex flex-wrap gap-3"
            >
              <Link to="/blog" className="lab-button">
                阅读笔记 <span aria-hidden="true">→</span>
              </Link>
              <Link to="/products" className="lab-button-secondary">
                查看作品
              </Link>
            </motion.div>
          </div>

          {/* Right: margin notes (glass panels) */}
          <div className="flex flex-col gap-4 lg:w-96">
            {/* Code preview card */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotate: -2 }}
              animate={{ opacity: 1, x: 0, rotate: -2 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-3 flex items-center gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-red-400/70" />
                  <div className="h-2 w-2 rounded-full bg-yellow-400/70" />
                  <div className="h-2 w-2 rounded-full bg-green-400/70" />
                </div>
                <div className="space-y-2 font-mono text-[10px] text-text-muted dark:text-text-muted-dark">
                  <div className="flex gap-2"><div className="w-5 h-2 rounded-full bg-clay/40" /><div className="flex-1 h-2 rounded-full bg-border/60" /></div>
                  <div className="ml-3 flex gap-2"><div className="w-3 h-2 rounded-full bg-accent/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                  <div className="ml-3 flex gap-2"><div className="w-7 h-2 rounded-full bg-blueprint/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                </div>
              </GlassPanel>
            </motion.div>

            {/* Tags card */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotate: 2 }}
              animate={{ opacity: 1, x: 0, rotate: 2 }}
              transition={{ delay: 1, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-2 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">最近标签</div>
                <div className="flex flex-wrap gap-1.5">
                  <span className="lab-chip text-[10px]">#React</span>
                  <span className="lab-chip text-[10px]">#API</span>
                  <span className="lab-chip text-[10px]">#CSS</span>
                  <span className="lab-chip text-[10px]">#Rust</span>
                </div>
              </GlassPanel>
            </motion.div>

            {/* Activity bar */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.6 }}
            >
              <GlassPanel accentLine className="p-4">
                <div className="mb-2 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">活跃度</div>
                <div className="flex items-end gap-1 h-10">
                  {[3, 5, 2, 7, 4, 6, 3].map((h, i) => (
                    <motion.div
                      key={i}
                      className="w-2.5 rounded-sm bg-accent/20"
                      style={{ height: h * 5 }}
                      animate={{ scaleY: [1, 1.4, 0.8, 1.2, 1] }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: i * 0.2 }}
                    />
                  ))}
                </div>
              </GlassPanel>
            </motion.div>
          </div>
        </div>

        {/* Tick divider at bottom */}
        <div className="absolute bottom-0 left-0 right-0 px-8">
          <TickDivider />
        </div>
      </motion.section>

      {/* Latest articles — editorial grid */}
      <section>
        <div className="mb-8">
          <SectionNumber number="002" label="最新笔记" />
        </div>

        {loading ? (
          <div className="space-y-5">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-44" />
            ))}
          </div>
        ) : articles?.items.length ? (
          <div className="space-y-6">
            {/* Featured + second article side by side */}
            <div className="grid gap-6 md:grid-cols-[1fr_auto]">
              <ArticleCard article={articles.items[0]} variant="featured" index={0} />
              {articles.items[1] && (
                <ArticleCard article={articles.items[1]} variant="default" index={1} />
              )}
            </div>

            {/* Compact cards row */}
            {articles.items.length > 2 && (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {articles.items.slice(2).map((article, i) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    variant="compact"
                    index={i + 2}
                  />
                ))}
              </div>
            )}

            <Link to="/blog" className="lab-button-secondary w-fit mx-auto block">
              查看全部文章 <span aria-hidden="true">→</span>
            </Link>
          </div>
        ) : (
          <EmptyState title="暂无文章" />
        )}
      </section>

      {/* Products — showcase */}
      <section>
        <div className="mb-8">
          <SectionNumber number="003" label="作品" />
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
            className="space-y-6"
          >
            {products.map((product) => (
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
                        <StatusDot status={product.status} showLabel={false} />
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
                        查看 <span aria-hidden="true">→</span>
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

      {/* Signature block */}
      <section className="signature-block">
        <blockquote>
          好的代码像好的实验——<br />每一步都值得重复。
        </blockquote>
        <p className="signature">── august ──</p>
        <div className="mt-6 flex justify-center gap-6">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-text-muted hover:text-accent dark:text-text-muted-dark dark:hover:text-accent transition-colors">
            GitHub
          </a>
          <a href="mailto:hello@example.com" className="text-sm font-semibold text-text-muted hover:text-accent dark:text-text-muted-dark dark:hover:text-accent transition-colors">
            Email
          </a>
        </div>
      </section>
    </div>
  );
}
