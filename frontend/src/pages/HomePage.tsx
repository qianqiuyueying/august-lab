import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';
import { useEffect, useState } from 'react';
import { getProducts } from '../api/products';
import type { Product } from '../types';

const heroVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.15, delayChildren: 0.2 },
  },
};

const heroItemVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const gridVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

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
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden -mx-4 sm:-mx-6 lg:-mx-8">
      {/* Hero background image with overlay */}
        <div className="absolute inset-0 overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900">
          <img
            src="/images/hero-bg.webp"
            alt=""
            className="w-full h-full object-cover opacity-60 dark:opacity-40"
          />
          {/* Animated gradient blobs overlay */}
          <div className="absolute inset-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-indigo-200/40 dark:bg-indigo-900/20 blur-3xl animate-float-slow" />
            <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-purple-200/40 dark:bg-purple-900/20 blur-3xl animate-float-medium" />
            <div className="absolute top-1/2 left-1/2 w-64 h-64 rounded-full bg-pink-200/30 dark:bg-pink-900/10 blur-3xl animate-float-slow" style={{ animationDelay: '5s' }} />
          </div>
        </div>

        {/* Content */}
        <motion.div
          variants={heroVariants}
          initial="hidden"
          animate="visible"
          className="relative z-10 text-center px-4"
        >
          <motion.h1
            variants={heroItemVariants}
            className="text-5xl sm:text-6xl lg:text-7xl font-bold text-zinc-900 dark:text-white mb-6"
          >
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              August&apos;s Lab
            </span>
          </motion.h1>

          <motion.p
            variants={heroItemVariants}
            className="text-xl sm:text-2xl text-zinc-600 dark:text-zinc-300 max-w-2xl mx-auto mb-10"
          >
            技术探索与创造的交汇点
          </motion.p>

          <motion.div
            variants={heroItemVariants}
            className="flex flex-wrap justify-center gap-4"
          >
            <Link
              to="/blog"
              className="px-8 py-3 rounded-xl bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-medium hover:bg-zinc-800 dark:hover:bg-zinc-100 transition-colors"
            >
              阅读博客
            </Link>
            <Link
              to="/products"
              className="px-8 py-3 rounded-xl border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 font-medium hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              查看产品
            </Link>
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 6, 0] }}
          transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
        >
          <svg className="w-6 h-6 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </motion.div>
      </section>

      {/* Latest Articles */}
      <section>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-bold text-zinc-900 dark:text-white mb-2 text-center"
        >
          最新文章
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-zinc-500 dark:text-zinc-400 text-center mb-8"
        >
          探索最新的技术分享与思考
        </motion.p>

        {loading ? (
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        ) : (
          <div className="space-y-6 max-w-3xl mx-auto">
            {articles?.items.map((article, i) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <ArticleCard article={article} />
              </motion.div>
            ))}
          </div>
        )}

        {articles && articles.total > 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mt-8"
          >
            <Link
              to="/blog"
              className="inline-flex items-center px-6 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 font-medium hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              查看全部文章
              <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </motion.div>
        )}
      </section>

      {/* Latest Products */}
      <section>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-bold text-zinc-900 dark:text-white mb-2 text-center"
        >
          最新产品
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-zinc-500 dark:text-zinc-400 text-center mb-8"
        >
          探索我们的项目与产品展示
        </motion.p>

        {productsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        ) : products.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-zinc-500 dark:text-zinc-400 text-center py-12"
          >
            暂无产品
          </motion.div>
        ) : (
          <motion.div
            variants={gridVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {products.map((product) => (
              <motion.div key={product.id} variants={cardVariants}>
                <a href={`/products/${product.slug}/`} className="block h-full">
                  <motion.div
                    whileHover={{ y: -6 }}
                    className="bg-white dark:bg-zinc-900/50 rounded-2xl overflow-hidden border border-zinc-200/60 dark:border-zinc-800/60 shadow-sm hover:shadow-xl transition-all duration-300 h-full flex flex-col group"
                  >
                    {/* Cover image area */}
                    <div className="aspect-[4/3] overflow-hidden relative bg-gradient-to-br from-violet-400 to-purple-500">
                      {product.cover_image ? (
                        <img
                          src={product.cover_image}
                          alt={product.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <img
                          src="/images/cover-product.webp"
                          alt=""
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      )}
                      {/* Status badge overlay */}
                      <div className="absolute top-3 right-3">
                        {product.status === 'published' ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            已上线
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                            开发中
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-5 flex-1 flex flex-col">
                      <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-1.5">
                        {product.title}
                      </h3>
                      {product.description && (
                        <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed line-clamp-2 flex-1">
                          {product.description}
                        </p>
                      )}
                      <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center text-accent text-sm font-medium">
                        查看详情
                        <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>

                    {/* Bottom accent line */}
                    <div className="h-1 bg-gradient-to-r from-indigo-500 to-purple-500" />
                  </motion.div>
                </a>
              </motion.div>
            ))}
          </motion.div>
        )}

        {products.length > 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mt-8"
          >
            <Link
              to="/products"
              className="inline-flex items-center px-6 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 font-medium hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              查看全部产品
              <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </motion.div>
        )}
      </section>
    </div>
  );
}
