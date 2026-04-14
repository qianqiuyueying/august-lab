import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getPage } from '../api/pages';
import type { Page } from '../types';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';

const sectionVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

export default function AboutPage() {
  const [page, setPage] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPage('about')
      .then(setPage)
      .catch(() => setPage(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-10 bg-zinc-200 dark:bg-zinc-800 rounded-lg w-48" />
          <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded w-full" />
          <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded w-3/4" />
        </div>
      </div>
    );
  }

  // If there's backend-managed content, render it
  if (page) {
    return (
      <AnimatedPage className="max-w-3xl mx-auto">
        <article className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-6">
            {page.title}
          </h1>
          <ArticleContent content={page.content} />
        </article>
      </AnimatedPage>
    );
  }

  // Default built-in about page
  return (
    <AnimatedPage className="max-w-3xl mx-auto">
      <div className="space-y-12">
        {/* Hero section */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="text-center"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
            className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-3xl font-bold"
          >
            A
          </motion.div>
          <motion.h1
            className="text-4xl font-bold text-zinc-900 dark:text-white mb-3"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            About Me
          </motion.h1>
          <motion.p
            className="text-zinc-500 dark:text-zinc-400 text-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            开发者 / 创造者 / 终身学习者
          </motion.p>
        </motion.div>

        {/* Bio */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">简介</h2>
          <div className="prose prose-zinc dark:prose-invert max-w-none">
            <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
              欢迎来到 August&apos;s Lab！这里是August的个人空间，用于分享技术心得、项目经验和对世界的思考。
            </p>
            <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed mt-4">
              你可以在「博客」板块阅读技术文章，在「产品」板块查看我们的项目展示。
            </p>
          </div>
        </motion.div>

        {/* Tech stack */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">技术栈</h2>
          <div className="flex flex-wrap gap-2">
            {[
              'Python', 'FastAPI', 'React', 'TypeScript',
              'Tailwind CSS', 'SQLite', 'Docker', 'Nginx',
            ].map((tech, i) => (
              <motion.span
                key={tech}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ scale: 1.08 }}
                className="px-3 py-1.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 text-sm font-medium cursor-default"
              >
                {tech}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Contact */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">联系方式</h2>
          <p className="text-zinc-500 dark:text-zinc-400">
            你可以通过博客中的评论功能与我互动，或在项目中找到更多联系方式。
          </p>
        </motion.div>
      </div>
    </AnimatedPage>
  );
}
