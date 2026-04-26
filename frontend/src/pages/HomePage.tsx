import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';
import { getProducts } from '../api/products';
import type { Product } from '../types';

const heroTextVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const heroItemVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] as const },
  },
};

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

const heroPills = [
  { label: '实验笔记', description: '拆解技术决策、架构取舍和踩坑记录' },
  { label: '产品记录', description: '把小工具从想法打磨到可用' },
  { label: '长期思考', description: '关注工程、写作和创造之间的连接' },
];

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

  return (
    <div className="space-y-24">
      <section className="hero-banner relative -mx-4 flex min-h-[60vh] items-center overflow-hidden rounded-lg sm:-mx-6 lg:-mx-8">
        <div className="absolute inset-0 z-0">
          <img
            src="/images/brand/lab-hero.webp"
            alt=""
            aria-hidden="true"
            className="h-full w-full object-cover"
          />
          <div className="hero-overlay absolute inset-0" />
        </div>
        <motion.div
          className="relative z-10 w-full px-6 py-14 sm:px-10 sm:py-20 lg:px-14"
          variants={heroTextVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.p variants={heroItemVariants} className="hero-label mb-4">
            Personal technical notebook
          </motion.p>
          <motion.h1
            variants={heroItemVariants}
            className="max-w-4xl text-4xl font-extrabold leading-[1.08] text-white sm:text-6xl lg:text-7xl"
          >
            写下实验、系统和那些慢慢成形的想法。
          </motion.h1>
          <motion.div variants={heroItemVariants} className="mt-6 flex flex-wrap gap-3">
            {heroPills.map((pill) => (
              <span
                key={pill.label}
                className="rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-bold text-white backdrop-blur-sm"
                title={pill.description}
              >
                {pill.label}
              </span>
            ))}
          </motion.div>
          <motion.div variants={heroItemVariants} className="mt-9 flex flex-wrap gap-3">
            <Link to="/blog" className="hero-button">
              阅读笔记
              <span aria-hidden="true">→</span>
            </Link>
            <Link to="/products" className="hero-button-outline">
              查看作品
            </Link>
          </motion.div>
        </motion.div>
      </section>

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
                  <article className="card-glow flex h-full flex-col overflow-hidden rounded-lg border border-border bg-paper/88 shadow-sm dark:border-border-dark dark:bg-surface-dark/88">
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
