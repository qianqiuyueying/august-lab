import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticles } from '../hooks/useArticles';
import ArticleCard from '../components/articles/ArticleCard';
import { Skeleton } from '../components/ui/Skeleton';

const sections = [
  {
    to: '/',
    title: '首页',
    description: '探索精选内容与最新更新',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
    gradient: 'from-indigo-500 to-blue-500',
  },
  {
    to: '/blog',
    title: '博客',
    description: '技术文章、教程与深度思考',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
      </svg>
    ),
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    to: '/products',
    title: '产品',
    description: '项目展示与静态页面托管',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.883-1.761V7.5a2.25 2.25 0 00-1.395-2.081l-6-2.618a2.25 2.25 0 00-1.796 0l-6 2.618A2.25 2.25 0 003.75 7.5v5.189c0 .703.336 1.33.883 1.761m15.746 0A2.25 2.25 0 0121 16.5v-3.35a2.25 2.25 0 00-.87-1.751M3.75 14.15V16.5a2.25 2.25 0 00.87 1.751m15.756-4.101a2.25 2.25 0 010 3.502" />
      </svg>
    ),
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    to: '/about',
    title: '关于我',
    description: '了解August和技术栈',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
      </svg>
    ),
    gradient: 'from-amber-500 to-orange-500',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.4 },
  },
};

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

export default function HomePage() {
  const { data: articles, loading } = useArticles(1, 3);

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden -mx-4 sm:-mx-6 lg:-mx-8">
      {/* Hero background image with overlay */}
        <div className="absolute inset-0 overflow-hidden">
          <img
            src="/assets/hero-bg.png"
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

      {/* Section Navigation Cards */}
      <section>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-2xl font-bold text-zinc-900 dark:text-white mb-8 text-center"
        >
          探索更多
        </motion.h2>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {sections.map((section) => (
            <motion.div
              key={section.to}
              variants={heroItemVariants}
              whileHover={{ y: -6, scale: 1.02 }}
              className="group"
            >
              <Link to={section.to}>
                <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm hover:shadow-xl transition-shadow h-full">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${section.gradient} text-white flex items-center justify-center mb-4`}>
                    {section.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
                    {section.title}
                  </h3>
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                    {section.description}
                  </p>
                  <div className="mt-4 flex items-center text-accent text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                    前往探索
                    <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Featured Articles */}
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
    </div>
  );
}
