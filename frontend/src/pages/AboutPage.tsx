import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getSetting } from '../api/settings';
import type { Page } from '../types';
import { getPage } from '../api/pages';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';

const sectionVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const techStack = [
  { name: 'Python', icon: 'Python' },
  { name: 'FastAPI', icon: 'FastAPI' },
  { name: 'React', icon: 'React' },
  { name: 'TypeScript', icon: 'TypeScript' },
  { name: 'Tailwind', icon: 'Tailwind' },
  { name: 'SQLite', icon: 'SQLite' },
  { name: 'Docker', icon: 'Docker' },
  { name: 'Nginx', icon: 'Nginx' },
];

const timeline = [
  { year: '现在', event: '搭建个人博客，分享技术思考' },
  { year: '持续', event: '探索全栈开发与产品设计' },
  { year: '旅程', event: '从代码到创造，持续学习' },
];

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
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-12"
        >
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-accent-start via-accent-mid to-accent-end p-[2px]">
              <div className="w-full h-full rounded-full bg-white dark:bg-zinc-900 flex items-center justify-center text-2xl font-bold text-zinc-900 dark:text-white">
                A
              </div>
            </div>
            <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-1 tracking-tight">About Me</h1>
            <p className="text-zinc-400 dark:text-zinc-500">开发者 / 创造者 / 终身学习者</p>
          </div>
          <div className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm prose prose-zinc dark:prose-invert max-w-none">
            <div dangerouslySetInnerHTML={{ __html: bio }} />
          </div>
          <div className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-5 tracking-tight">技术栈</h2>
            <div className="flex flex-wrap gap-2">
              {techStack.map((tech) => (
                <span
                  key={tech.name}
                  className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-300 text-sm font-medium"
                >
                  {tech.name}
                </span>
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
        <article className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-6 tracking-tight">
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
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-accent-start via-accent-mid to-accent-end p-[2px]"
          >
            <div className="w-full h-full rounded-full bg-white dark:bg-zinc-900 flex items-center justify-center text-2xl font-bold text-zinc-900 dark:text-white">
              A
            </div>
          </motion.div>
          <motion.h1
            className="text-3xl font-bold text-zinc-900 dark:text-white mb-1 tracking-tight"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            About Me
          </motion.h1>
          <motion.p
            className="text-zinc-400 dark:text-zinc-500"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
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
          <div className="flex flex-wrap justify-center gap-2">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 1.746.566C10.16 9.21 11.135 9 12 9c.865 0 1.84.21 2.264.651.906-.836 1.746-.566 1.746-.566.544 1.378.202 2.396.1 2.65.64.7 1.03 1.595 1.03 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              GitHub
            </a>
            <a
              href="mailto:hello@example.com"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
              Email
            </a>
          </div>
        </motion.div>

        {/* Bio */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4 tracking-tight">简介</h2>
          <div className="prose prose-zinc dark:prose-invert max-w-none">
            <p className="text-zinc-500 dark:text-zinc-400 leading-relaxed">
              欢迎来到 August&apos;s Lab！这里是 August 的个人空间，用于分享技术心得、项目经验和对世界的思考。
            </p>
            <p className="text-zinc-500 dark:text-zinc-400 leading-relaxed mt-4">
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
          className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-5 tracking-tight">技术栈</h2>
          <div className="flex flex-wrap gap-2">
            {techStack.map((tech, i) => (
              <motion.span
                key={tech.name}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.04 }}
                className="inline-flex items-center px-3.5 py-2 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-300 text-sm font-medium"
              >
                {tech.name}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Timeline */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-6 tracking-tight">我的旅程</h2>
          <div className="space-y-6 relative before:absolute before:left-[7px] before:top-3 before:bottom-3 before:w-px before:bg-zinc-200 dark:before:bg-zinc-800">
            {timeline.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="flex items-start gap-4 relative pl-6"
              >
                <div className="absolute left-0 top-1 w-[15px] h-[15px] rounded-full bg-white dark:bg-zinc-900 border-2 border-zinc-300 dark:border-zinc-700" />
                <div>
                  <span className="text-xs font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">{item.year}</span>
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
          className="bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-8 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-3 tracking-tight">联系方式</h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
            你可以通过博客中的评论功能与我互动，或在项目中找到更多联系方式。
          </p>
        </motion.div>
      </div>
    </AnimatedPage>
  );
}
