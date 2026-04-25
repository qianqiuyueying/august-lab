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
        />
        <AboutVisual />
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
            <AboutVisual />
          </div>
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
          <div className="relative overflow-hidden rounded-lg border border-border bg-paper shadow-md dark:border-border-dark dark:bg-surface-dark">
            <img
              src="/images/brand/about-workbench.webp"
              alt=""
              aria-hidden="true"
              className="aspect-[4/3] w-full object-cover"
            />
            <div className="absolute left-4 top-4 rounded-lg border border-border bg-paper/86 p-3 shadow-sm backdrop-blur-md dark:border-border-dark dark:bg-surface-dark/82">
              <BrandMark compact className="h-14 w-14" />
            </div>
          </div>
        </motion.div>
        <PageIntro
          eyebrow="About"
          title="August's Lab"
        />
      </section>

      <ProfileSections />
    </AnimatedPage>
  );
}

function AboutVisual() {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-paper shadow-sm dark:border-border-dark dark:bg-surface-dark">
      <img
        src="/images/brand/about-workbench.webp"
        alt=""
        aria-hidden="true"
        className="aspect-[16/9] w-full object-cover"
      />
    </div>
  );
}

function ProfileSections() {
  return (
    <div className="grid gap-6">
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
    </div>
  );
}
