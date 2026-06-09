import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import { getProducts } from '../api/products';
import type { Product } from '../types';
import SectionNumber from '../components/ui/SectionNumber';
import TickDivider from '../components/ui/TickDivider';
import StatusDot from '../components/ui/StatusDot';
import TiltCard from '../components/ui/TiltCard';

/* ===== Combined hook: parallax + section transition ===== */
function useSectionEffects() {
  const ref = useRef<HTMLElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref as React.RefObject<HTMLElement>,
    offset: ['start end', 'end start'],
  });
  // Parallax
  const bgY = useTransform(scrollYProgress, [0, 1], ['-3%', '3%']);
  const fgFastY = useTransform(scrollYProgress, [0, 1], ['8%', '-8%']);
  const fgSlowY = useTransform(scrollYProgress, [0, 1], ['4%', '-4%']);
  // Section transition (entering → entered → leaving)
  const opacity = useTransform(scrollYProgress, [0.00, 0.06, 0.13, 0.85, 1.00], [0.00, 0.00, 1.00, 1.00, 0.30]);
  const y = useTransform(scrollYProgress, [0.00, 0.06, 0.13, 0.85, 1.00], [40.0, 40.0, 0.00, 0.00, -20.0]);
  return { ref, bgY, fgFastY, fgSlowY, opacity, y };
}

export default function HomePage() {
  const { data: articles, loading } = useArticles(1, 3);
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((data) => setProducts(data.slice(0, 3)))
      .catch(() => {})
      .finally(() => setProductsLoading(false));
  }, []);

  const s2 = useSectionEffects();
  const s3 = useSectionEffects();

  return (
    <>
      {/* ===== Section 01 — Hero ===== */}
      <section className="relative flex min-h-screen items-start overflow-hidden">
        <div className="absolute inset-0 z-0" style={{ margin: '-5%' }}>
          <img
            src="/images/preview/hero_bg_00001_.webp"
            alt=""
            className="h-full w-full object-cover"
            style={{ transform: 'scale(1.1)' }}
          />
        </div>

        <div className="absolute inset-0 z-[1] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(10,15,26,.5) 100%)' }}
        />
        <div className="absolute inset-0 z-[2] pointer-events-none"
          style={{ boxShadow: 'inset 0 0 150px rgba(10,15,26,.8)' }}
        />

        <div className="a-float1 absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(120px,16vw,280px)', bottom: '10%', left: 'clamp(10px,3vw,5%)' }}>
          <img src="/images/preview/s01_notebook_00001_.webp" alt="" className="w-full h-auto" />
        </div>
        <div className="a-spin glow-amber absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(70px,10vw,160px)', top: 'clamp(40px,8vh,12%)', right: 'clamp(10px,5vw,8%)' }}>
          <img src="/images/preview/s01_compass_v2_00001_.webp" alt="" className="w-full h-auto" />
        </div>

        <div className="relative z-10 mx-auto max-w-3xl w-full px-4 pt-[clamp(60px,12vh,100px)] sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <SectionNumber number="001" label="首页" />
          </motion.div>

          <div className="overflow-hidden mt-2 mb-5">
            <motion.h1
              className="text-4xl font-extrabold leading-[1.1] sm:text-5xl lg:text-6xl"
              initial={{ opacity: 0, y: '100%' }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                background: 'linear-gradient(180deg, #f6f4ee 0%, #f6f4ee 60%, #c8843c 100%)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
              }}>
              写下实验、系统和<br />
              <span style={{ background: 'linear-gradient(135deg, #c8843c, #3ba5c4, #6b7db3)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                那些慢慢成形的想法
              </span>
            </motion.h1>
          </div>

          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7, duration: 0.8 }}
            className="max-w-md text-base leading-7 text-text-secondary sm:text-lg">
            一个记录技术探索、产品实践和长期思考的个人空间。
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.85, duration: 0.8 }}
            className="flex flex-wrap gap-3 mt-7">
            <Link to="/blog" className="lab-button">阅读笔记 <span aria-hidden="true">→</span></Link>
            <Link to="/products" className="lab-button-secondary">查看作品</Link>
          </motion.div>
        </div>
      </section>

      <TickDivider />

      {/* ===== Section 02 — 最新笔记 ===== */}
      <motion.section
        ref={s2.ref as React.RefObject<HTMLElement>}
        className="relative overflow-hidden"
        style={{ minHeight: '90vh', opacity: s2.opacity, y: s2.y }}
      >
        <motion.div className="absolute inset-0 z-0" style={{ margin: '-8%', y: s2.bgY }}>
          <img src="/images/preview/s02_desk_bg_00001_.webp" alt="" loading="lazy"
            className="h-full w-full object-cover" style={{ transform: 'scale(1.15)' }} />
        </motion.div>
        <div className="absolute inset-0 z-[1] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(10,15,26,.5) 100%)' }} />
        <div className="absolute inset-0 z-[2] pointer-events-none"
          style={{ boxShadow: 'inset 0 0 150px rgba(10,15,26,.8)' }} />

        <motion.div className="a-float1 absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(120px,16vw,280px)', top: '12%', left: '2%', y: s2.fgSlowY }}>
          <img src="/images/preview/s02_starchart_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>
        <motion.div className="a-float3 absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(40px,6vw,100px)', top: '18%', right: '7%', y: s2.fgFastY }}>
          <img src="/images/preview/s02_quartz_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>
        <motion.div className="a-float2 absolute z-[2] pointer-events-none hidden sm:block"
          style={{ width: 'clamp(35px,5vw,90px)', top: '48%', right: '3%', y: s2.fgSlowY }}>
          <img src="/images/preview/s02_leaf_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>

        <div className="relative z-10 mx-auto max-w-7xl px-4 py-[clamp(40px,8vh,80px)] sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px 0px 0px 0px' }}
            transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}>
            <SectionNumber number="002" label="最新笔记" />
          </motion.div>

          {loading ? (
            <div className="space-y-5 mt-6">{[1, 2, 3].map((i) => (<Skeleton key={i} className="h-36" />))}</div>
          ) : articles?.items.length ? (
            <div className="space-y-6 mt-6">
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {articles.items.map((article, i) => (
                  <motion.div key={article.id}
                    initial={{ opacity: 0, y: 60 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-60px 0px 0px 0px' }}
                    transition={{ duration: 0.7, delay: 0.06 + i * 0.08, ease: [0.25, 1, 0.5, 1] }}>
                    <ArticleCard article={article} />
                  </motion.div>
                ))}
              </div>
              <motion.div className="text-center mt-7"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}>
                <Link to="/blog" className="lab-button-secondary">查看全部文章 <span aria-hidden="true">→</span></Link>
              </motion.div>
            </div>
          ) : (<EmptyState title="暂无文章" />)}
        </div>
      </motion.section>

      <TickDivider />

      {/* ===== Section 03 — 作品 ===== */}
      <motion.section
        ref={s3.ref as React.RefObject<HTMLElement>}
        className="relative overflow-hidden"
        style={{ minHeight: '90vh', opacity: s3.opacity, y: s3.y }}
      >
        <motion.div className="absolute inset-0 z-0" style={{ margin: '-8%', y: s3.bgY }}>
          <img src="/images/preview/s03_shelf_bg_00001_.webp" alt="" loading="lazy"
            className="h-full w-full object-cover" style={{ transform: 'scale(1.15)' }} />
        </motion.div>
        <div className="absolute inset-0 z-[1] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(10,15,26,.5) 100%)' }} />
        <div className="absolute inset-0 z-[2] pointer-events-none"
          style={{ boxShadow: 'inset 0 0 150px rgba(10,15,26,.8)' }} />

        <motion.div className="a-pulse glow-cyan absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(80px,11vw,180px)', top: '10%', right: '5%', y: s3.fgFastY }}>
          <img src="/images/preview/s03_orb_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>
        <motion.div className="a-float1 absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(60px,8vw,140px)', top: '28%', left: '2%', y: s3.fgSlowY }}>
          <img src="/images/preview/s03_specimen_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>
        <motion.div className="a-float3 absolute z-[2] pointer-events-none"
          style={{ width: 'clamp(90px,12vw,200px)', top: '52%', right: '3%', y: s3.fgSlowY }}>
          <img src="/images/preview/s03_scroll_00001_.webp" alt="" className="w-full h-auto" />
        </motion.div>

        <div className="relative z-10 mx-auto max-w-7xl px-4 py-[clamp(40px,8vh,80px)] sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px 0px 0px 0px' }}
            transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}>
            <SectionNumber number="003" label="作品" />
          </motion.div>

          {productsLoading ? (
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3 mt-6">{[1, 2, 3].map((i) => (<Skeleton key={i} className="h-60" />))}</div>
          ) : products.length ? (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 mt-6">
              {products.map((product, i) => (
                <motion.div key={product.id}
                  initial={{ opacity: 0, y: 60 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-60px 0px 0px 0px' }}
                  transition={{ duration: 0.7, delay: i * 0.08, ease: [0.25, 1, 0.5, 1] }}>
                  <Link to={`/products/${product.slug}`} className="group block h-full focus-ring">
                    <TiltCard maxRotation={12} className="h-full">
                      <article className="lab-card flex h-full flex-col overflow-hidden transition-colors group-hover:border-accent-mid/40 group-hover:shadow-lg">
                        <div className="relative aspect-[3/2] overflow-hidden bg-background">
                          <img src={product.cover_image || '/images/brand/fallback-product.webp'}
                            alt={product.cover_image ? product.title : ''} loading="lazy" decoding="async"
                            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                            aria-hidden={!product.cover_image} />
                          <div className="absolute right-3 top-3"><StatusDot status={product.status} /></div>
                        </div>
                        <div className="flex flex-1 flex-col p-4">
                          <h3 className="text-base font-extrabold text-paper transition-colors">{product.title}</h3>
                          {product.description && (
                            <p className="mt-1.5 line-clamp-2 flex-1 text-sm leading-6 text-text-secondary">{product.description}</p>
                          )}
                          <div className="mt-3 border-t border-border pt-2 text-sm font-bold text-accent">查看 <span aria-hidden="true">→</span></div>
                        </div>
                      </article>
                    </TiltCard>
                  </Link>
                </motion.div>
              ))}
            </div>
          ) : (<EmptyState title="暂无作品" />)}
        </div>
      </motion.section>

      {/* ===== Signature ===== */}
      <motion.section className="signature-block mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.1 }}
        transition={{ duration: 0.8, ease: [0.25, 1, 0.5, 1] }}>
        <TickDivider />
        <blockquote className="mt-10">好的代码像好的实验——<br /><span style={{ color: '#c8843c' }}>每一步都值得重复。</span></blockquote>
        <p className="signature">── august ──</p>
        <div className="mt-6 flex justify-center gap-6">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-blueprint hover:text-accent transition-colors">GitHub</a>
          <a href="mailto:hello@example.com" className="text-sm font-semibold text-blueprint hover:text-accent transition-colors">Email</a>
        </div>
      </motion.section>
    </>
  );
}
