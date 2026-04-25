import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getSetting } from '../api/settings';
import type { Page } from '../types';
import { getPage } from '../api/pages';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';
import PageIntro from '../components/ui/PageIntro';
import BrandMark from '../components/ui/BrandMark';
import { Skeleton } from '../components/ui/Skeleton';

const sectionVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.38, ease: [0.16, 1, 0.3, 1] as const },
  },
};

const techStack = ['Python', 'FastAPI', 'React', 'TypeScript', 'Tailwind', 'SQLite', 'Docker', 'Nginx'];

const timeline = [
  { year: '现在', event: '持续打磨个人博客，把写作、工程和产品实验放在同一个系统里。' },
  { year: '长期', event: '关注全栈开发、工具体验、设计细节和可维护系统。' },
  { year: '下一步', event: '把更多项目的构建过程整理成可复盘的实验记录。' },
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
      <div className="mx-auto max-w-4xl space-y-5">
        <Skeleton className="h-14 w-72" />
        <Skeleton className="h-28" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (bio) {
    return (
      <AnimatedPage className="mx-auto max-w-4xl space-y-10">
        <PageIntro
          eyebrow="About"
          title="关于 August's Lab"
          description="这里是一个把技术探索、产品实验和长期写作放在一起的个人空间。"
        />
        <section className="paper-panel-strong p-6 sm:p-8">
          <div className="markdown-body" dangerouslySetInnerHTML={{ __html: bio }} />
        </section>
        <ProfileSections />
      </AnimatedPage>
    );
  }

  if (page) {
    return (
      <AnimatedPage className="mx-auto max-w-4xl">
        <article className="paper-panel-strong p-6 sm:p-9">
          <PageIntro eyebrow="About" title={page.title} />
          <div className="mt-8">
            <ArticleContent content={page.content} />
          </div>
        </article>
      </AnimatedPage>
    );
  }

  return (
    <AnimatedPage className="mx-auto max-w-5xl space-y-12">
      <section className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
        <motion.div variants={sectionVariants} initial="hidden" animate="visible">
          <div className="paper-panel-strong inline-flex p-4">
            <BrandMark compact className="h-20 w-20" />
          </div>
        </motion.div>
        <PageIntro
          eyebrow="About"
          title="我是 August，这里是我的技术实验笔记。"
          description="我用这个站点记录开发过程里的判断、问题和小成果。比起把项目包装成完成品，我更关心每一次从混乱到清晰的过程。"
        />
      </section>

      <ProfileSections />
    </AnimatedPage>
  );
}

function ProfileSections() {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }} className="paper-panel p-6">
        <p className="section-label mb-4">Stack</p>
        <h2 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">常用技术栈</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {techStack.map((tech) => (
            <span key={tech} className="lab-chip">
              {tech}
            </span>
          ))}
        </div>
      </motion.section>

      <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }} className="paper-panel p-6">
        <p className="section-label mb-4">Timeline</p>
        <h2 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">正在发生的事</h2>
        <div className="mt-6 space-y-5">
          {timeline.map((item) => (
            <div key={item.year} className="border-l-2 border-accent pl-4">
              <p className="text-sm font-extrabold text-text-primary dark:text-text-primary-dark">{item.year}</p>
              <p className="mt-1 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">{item.event}</p>
            </div>
          ))}
        </div>
      </motion.section>

      <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }} className="paper-panel p-6 lg:col-span-2">
        <p className="section-label mb-4">Contact</p>
        <h2 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">联系与反馈</h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
          如果某篇文章或某个作品对你有帮助，可以通过评论或项目页面里的联系方式交流。我也会把反馈继续写回这些笔记里。
        </p>
      </motion.section>
    </div>
  );
}
