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
    transition: { staggerChildren: 0.12, delayChildren: 0.15 },
  },
};

const heroItemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const },
  },
};

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
    transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const featureVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const features = [
  {
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
    title: '极速性能',
    desc: '毫秒级响应，丝滑的用户体验',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75l1.146-1.147a3 3 0 014.243 4.243l-2.147 2.146H3.75l2.147-2.146a3 3 0 010-4.243L9 12.75zm8.693-6.693a4.5 4.5 0 010 6.364l-2.147 2.146M15 3.75l-2.147 2.146a4.5 4.5 0 000 6.364" />
      </svg>
    ),
    title: '安全可靠',
    desc: 'JWT 认证，数据加密传输',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 01-1.622-3.395m3.42 3.42a15.995 15.995 0 004.428-1.41m-.287 2.903a16.002 16.002 0 00-2.904-4.427m2.904 4.427a15.996 15.996 0 01-1.41 4.428" />
      </svg>
    ),
    title: '优雅设计',
    desc: '极简美学，注重细节打磨',
  },
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
      {/* Hero Section */}
      <section className="relative min-h-[75vh] flex items-center justify-center overflow-hidden -mx-4 sm:-mx-6 lg:-mx-8">
        {/* Radial gradient glow */}
        <div className="absolute inset-0 hero-glow" />

        {/* Content */}
        <motion.div
          variants={heroVariants}
          initial="hidden"
          animate="visible"
          className="relative z-10 text-center px-4 max-w-4xl mx-auto"
        >
          <motion.h1
            variants={heroItemVariants}
            className="text-5xl sm:text-6xl lg:text-8xl font-extrabold tracking-tight mb-6"
          >
            <span className="text-gradient">August&apos;s Lab</span>
          </motion.h1>

          <motion.p
            variants={heroItemVariants}
            className="text-lg sm:text-xl lg:text-2xl text-zinc-500 dark:text-zinc-400 max-w-xl mx-auto mb-12 leading-relaxed"
          >
            技术探索与创造的交汇点
          </motion.p>

          <motion.div
            variants={heroItemVariants}
            className="flex flex-wrap justify-center gap-3"
          >
            <Link
              to="/blog"
              className="group inline-flex items-center gap-2 px-7 py-3 rounded-full bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-medium text-sm hover:bg-zinc-800 dark:hover:bg-zinc-100 transition-colors"
            >
              阅读博客
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <Link
              to="/products"
              className="inline-flex items-center gap-2 px-7 py-3 rounded-full border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors"
            >
              查看产品
            </Link>
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 6, 0] }}
          transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
        >
          <div className="w-6 h-10 rounded-full border-2 border-zinc-300 dark:border-zinc-700 flex items-start justify-center p-1.5">
            <motion.div
              className="w-1 h-2 rounded-full bg-zinc-400 dark:bg-zinc-500"
              animate={{ y: [0, 8, 0] }}
              transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
            />
          </div>
        </motion.div>
      </section>

      {/* Features Strip */}
      <section>
        <motion.div
          variants={gridVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              variants={featureVariants}
              transition={{ delay: i * 0.06 }}
              className="flex items-start gap-4 p-6 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 bg-white/50 dark:bg-zinc-900/30 backdrop-blur-sm"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 flex items-center justify-center text-zinc-600 dark:text-zinc-400">
                {feature.icon}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-0.5">{feature.title}</h3>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">{feature.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Latest Articles */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-10"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">最新文章</p>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-900 dark:text-white">技术分享与思考</h2>
        </motion.div>

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
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                <ArticleCard article={article} variant={i === 0 ? 'featured' : 'default'} />
              </motion.div>
            ))}
          </div>
        )}

        {articles && articles.total > 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mt-10"
          >
            <Link
              to="/blog"
              className="group inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full border border-zinc-200 dark:border-zinc-800 text-zinc-500 dark:text-zinc-400 text-sm font-medium hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors"
            >
              查看全部文章
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </motion.div>
        )}
      </section>

      {/* Latest Products */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-10"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">最新产品</p>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-900 dark:text-white">项目与产品展示</h2>
        </motion.div>

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
            className="text-zinc-400 dark:text-zinc-500 text-center py-16 text-sm"
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
                    whileHover={{ y: -4 }}
                    className="bg-white dark:bg-zinc-900/40 rounded-xl overflow-hidden border border-zinc-200/60 dark:border-zinc-800/60 shadow-sm hover:shadow-lg transition-all duration-300 h-full flex flex-col group"
                  >
                    {/* Cover image area */}
                    <div className="aspect-[4/3] overflow-hidden relative bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900">
                      {product.cover_image ? (
                        <img
                          src={product.cover_image}
                          alt={product.title}
                          className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <svg className="w-12 h-12 text-zinc-300 dark:text-zinc-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                          </svg>
                        </div>
                      )}
                      {/* Status badge overlay */}
                      <div className="absolute top-3 right-3">
                        {product.status === 'published' ? (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-white/90 dark:bg-zinc-900/90 backdrop-blur-sm text-emerald-600 dark:text-emerald-400 shadow-sm">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            已上线
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-white/90 dark:bg-zinc-900/90 backdrop-blur-sm text-zinc-500 dark:text-zinc-400 shadow-sm">
                            <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                            开发中
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-5 flex-1 flex flex-col">
                      <h3 className="text-[15px] font-semibold text-zinc-900 dark:text-white mb-1.5">
                        {product.title}
                      </h3>
                      {product.description && (
                        <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed line-clamp-2 flex-1">
                          {product.description}
                        </p>
                      )}
                      <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center text-zinc-500 dark:text-zinc-400 text-sm font-medium group-hover:text-zinc-900 dark:group-hover:text-white transition-colors">
                        查看详情
                        <svg className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </div>
                    </div>
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
            className="text-center mt-10"
          >
            <Link
              to="/products"
              className="group inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full border border-zinc-200 dark:border-zinc-800 text-zinc-500 dark:text-zinc-400 text-sm font-medium hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors"
            >
              查看全部产品
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </motion.div>
        )}
      </section>
    </div>
  );
}
