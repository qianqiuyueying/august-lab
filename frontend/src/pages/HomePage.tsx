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
import TiltCard from '../components/ui/TiltCard';

export default function HomePage() {
  const { data: articles, loading } = useArticles(1, 3);
  const { scrollY } = useScroll();
  const panelY1 = useTransform(scrollY, [0, 500], [0, -15]);
  const panelY2 = useTransform(scrollY, [0, 500], [0, -25]);
  const panelY3 = useTransform(scrollY, [0, 500], [0, -35]);
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((data) => setProducts(data.slice(0, 3)))
      .catch(() => {})
      .finally(() => setProductsLoading(false));
  }, []);

  return (
    <>
      {/* Hero — full-width (unchanged) */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-clay/5" />

        {/* Ambient floating orbs */}
        <div
          className="absolute -top-20 -right-20 h-[400px] w-[400px] rounded-full bg-accent/[0.06] blur-[80px]"
          style={{ animation: 'orb-float-1 14s ease-in-out infinite' }}
        />
        <div
          className="absolute bottom-20 -left-20 h-[300px] w-[300px] rounded-full bg-clay/[0.05] blur-[80px]"
          style={{ animation: 'orb-float-2 18s ease-in-out infinite' }}
        />
        <div
          className="absolute top-40 right-10 h-[250px] w-[250px] rounded-full bg-blueprint/[0.04] blur-[80px]"
          style={{ animation: 'orb-float-3 16s ease-in-out infinite' }}
        />

        <div className="relative z-10 mx-auto max-w-7xl px-4 pt-14 pb-6 sm:px-6 sm:pt-20 sm:pb-8 lg:px-8">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
            {/* Left: title + CTA */}
            <div className="flex-1 space-y-6">
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
                className="text-4xl font-extrabold leading-[1.15] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl"
              >
                写下实验、系统和
                <br />
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

            {/* Right: margin notes (glass panels) — unchanged */}
            <div className="w-full max-w-sm lg:w-80 lg:max-w-none flex flex-col gap-3">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
                style={{ y: panelY1 }}
              >
                <GlassPanel accentLine className="p-3">
                  <div className="mb-2 flex items-center gap-1.5">
                    <div className="h-2 w-2 rounded-full bg-red-400/70" />
                    <div className="h-2 w-2 rounded-full bg-yellow-400/70" />
                    <div className="h-2 w-2 rounded-full bg-green-400/70" />
                  </div>
                  <div className="space-y-1.5 font-mono text-[10px] text-text-muted dark:text-text-muted-dark">
                    <div className="flex gap-2"><div className="w-5 h-2 rounded-full bg-clay/40" /><div className="flex-1 h-2 rounded-full bg-border/60" /></div>
                    <div className="ml-3 flex gap-2"><div className="w-3 h-2 rounded-full bg-accent/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                    <div className="ml-3 flex gap-2"><div className="w-7 h-2 rounded-full bg-blueprint/40" /><div className="flex-1 h-2 rounded-full bg-border/40" /></div>
                  </div>
                </GlassPanel>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1, duration: 0.6 }}
                style={{ y: panelY2 }}
              >
                <GlassPanel accentLine className="p-3">
                  <div className="mb-1.5 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">最近标签</div>
                  <div className="flex flex-wrap gap-1.5">
                    <span className="lab-chip text-[10px]">#React</span>
                    <span className="lab-chip text-[10px]">#API</span>
                    <span className="lab-chip text-[10px]">#CSS</span>
                    <span className="lab-chip text-[10px]">#Rust</span>
                  </div>
                </GlassPanel>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.6 }}
                style={{ y: panelY3 }}
              >
                <GlassPanel accentLine className="p-3">
                  <div className="mb-1.5 text-[9px] font-bold text-text-muted dark:text-text-muted-dark">活跃度</div>
                  <div className="flex items-end gap-1 h-8">
                    {[3, 5, 2, 7, 4, 6, 3].map((h, i) => (
                      <motion.div
                        key={i}
                        className="w-2.5 rounded-sm bg-accent/20"
                        style={{ height: h * 4 }}
                        animate={{ scaleY: [1, 1.4, 0.8, 1.2, 1] }}
                        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: i * 0.2 }}
                      />
                    ))}
                  </div>
                </GlassPanel>
              </motion.div>
            </div>
          </div>

          <div className="mt-6">
            <TickDivider />
          </div>
        </div>
      </section>

      {/* Latest articles — uniform 3-column grid */}
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <SectionNumber number="002" label="最新笔记" />
        </div>

        {loading ? (
          <div className="space-y-5">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-36" />
            ))}
          </div>
        ) : articles?.items.length ? (
          <div className="space-y-6">
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {articles.items.map((article, i) => (
                <motion.div
                  key={article.id}
                  initial={{ opacity: 0, y: 18 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ amount: 0.1, margin: '0px 0px -50px 0px' }}
                  transition={{ duration: 0.42, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] as const }}
                >
                  <ArticleCard article={article} />
                </motion.div>
              ))}
            </div>

            <Link to="/blog" className="lab-button-secondary w-fit mx-auto block">
              查看全部文章 <span aria-hidden="true">→</span>
            </Link>
          </div>
        ) : (
          <EmptyState title="暂无文章" />
        )}
      </section>

      {/* Products — showcase with tilt, compact cards */}
      <section className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <SectionNumber number="003" label="作品" />
        </div>

        {productsLoading ? (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-60" />
            ))}
          </div>
        ) : products.length ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product, i) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.42, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] as const }}
              >
                <Link to={`/products/${product.slug}`} className="group block h-full focus-ring">
                  <TiltCard maxRotation={12} className="h-full">
                    <article className="lab-card flex h-full flex-col overflow-hidden rounded-xl border border-border/80 bg-paper/88 shadow-sm transition-colors group-hover:border-accent/30 dark:border-border-dark/80 dark:bg-surface-dark/88">
                      <div className="relative aspect-[3/2] overflow-hidden bg-paper-soft dark:bg-background-dark">
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
                      <div className="flex flex-1 flex-col p-4">
                        <h3 className="text-base font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark">
                          {product.title}
                        </h3>
                        {product.description && (
                          <p className="mt-1.5 line-clamp-2 flex-1 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
                            {product.description}
                          </p>
                        )}
                        <div className="mt-3 border-t border-border pt-2 text-sm font-bold text-accent dark:border-border-dark">
                          查看 <span aria-hidden="true">→</span>
                        </div>
                      </div>
                    </article>
                  </TiltCard>
                </Link>
              </motion.div>
            ))}
          </div>
        ) : (
          <EmptyState title="暂无作品" />
        )}
      </section>

      {/* Signature block — unchanged */}
      <section className="signature-block mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
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
    </>
  );
}
