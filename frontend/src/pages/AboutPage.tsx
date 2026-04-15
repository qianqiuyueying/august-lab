import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getSetting } from '../api/settings';
import type { Page } from '../types';
import { getPage } from '../api/pages';
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

const techStack = [
  { name: 'Python', icon: '🐍' },
  { name: 'FastAPI', icon: '⚡' },
  { name: 'React', icon: '⚛️' },
  { name: 'TypeScript', icon: '📘' },
  { name: 'Tailwind CSS', icon: '🎨' },
  { name: 'SQLite', icon: '🗄️' },
  { name: 'Docker', icon: '🐳' },
  { name: 'Nginx', icon: '🌐' },
];

const timeline = [
  { year: '现在', event: '搭建个人博客，分享技术思考', icon: '📝' },
  { year: '持续', event: '探索全栈开发与产品设计', icon: '🔧' },
  { year: '旅程', event: '从代码到创造，持续学习', icon: '🚀' },
];

function SocialLink({ href, icon, label }: { href: string; icon: string; label: string }) {
  return (
    <motion.a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      whileHover={{ y: -2, scale: 1.02 }}
      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors text-sm font-medium"
    >
      <span className="text-lg">{icon}</span>
      {label}
    </motion.a>
  );
}

export default function AboutPage() {
  const [page, setPage] = useState<Page | null>(null);
  const [bio, setBio] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getSetting('about_bio').then((d) => setBio(d.value)).catch(() => {}),
      getPage('about').then(setPage).catch(() => {}),
    ]).finally(() => setLoading(false));
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

  // Use the bio from settings if available
  if (bio) {
    return (
      <AnimatedPage className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-12"
        >
          <div className="text-center">
            <div className="w-28 h-28 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 p-[3px]">
              <div className="w-full h-full rounded-full bg-white dark:bg-zinc-900 flex items-center justify-center text-3xl font-bold text-zinc-900 dark:text-white">
                A
              </div>
            </div>
            <h1 className="text-4xl font-bold text-zinc-900 dark:text-white mb-2">About Me</h1>
            <p className="text-zinc-500 dark:text-zinc-400 text-lg">开发者 / 创造者 / 终身学习者</p>
          </div>
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm prose prose-zinc dark:prose-invert max-w-none">
            <div dangerouslySetInnerHTML={{ __html: bio }} />
          </div>
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">技术栈</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {techStack.map((tech) => (
                <motion.div
                  key={tech.name}
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 text-zinc-700 dark:text-zinc-300 text-sm font-medium cursor-default"
                >
                  <span className="text-base">{tech.icon}</span>
                  {tech.name}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </AnimatedPage>
    );
  }

  // Fallback to page content from API
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
        {/* Hero */}
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
            className="w-28 h-28 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 p-[3px]"
          >
            <div className="w-full h-full rounded-full bg-white dark:bg-zinc-900 flex items-center justify-center text-3xl font-bold text-zinc-900 dark:text-white">
              A
            </div>
          </motion.div>
          <motion.h1
            className="text-4xl font-bold text-zinc-900 dark:text-white mb-2"
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

        {/* Social Links */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="flex flex-wrap justify-center gap-3">
            <SocialLink href="https://github.com" icon="🐙" label="GitHub" />
            <SocialLink href="mailto:hello@example.com" icon="📧" label="Email" />
          </div>
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

        {/* Tech Stack */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">技术栈</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {techStack.map((tech, i) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 text-zinc-700 dark:text-zinc-300 text-sm font-medium cursor-default"
              >
                <span className="text-base">{tech.icon}</span>
                {tech.name}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Timeline */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-6">我的旅程</h2>
          <div className="space-y-6 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-[2px] before:bg-gradient-to-b before:from-indigo-500 before:to-purple-500 before:opacity-30">
            {timeline.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -16 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-4 relative"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center text-base flex-shrink-0 z-10">
                  {item.icon}
                </div>
                <div>
                  <span className="text-xs font-medium text-accent">{item.year}</span>
                  <p className="text-zinc-600 dark:text-zinc-400 text-sm mt-0.5">{item.event}</p>
                </div>
              </motion.div>
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
