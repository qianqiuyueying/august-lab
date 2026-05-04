import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getAbout } from '../api/about';
import type { AboutPage } from '../types';
import ArticleContent from '../components/articles/ArticleContent';
import AnimatedPage from '../components/layout/AnimatedPage';
import { Skeleton } from '../components/ui/Skeleton';
import HeroSection from '../components/about/HeroSection';
import InfoCards from '../components/about/InfoCards';
import ContactLinks from '../components/about/ContactLinks';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';

const sectionVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.38, ease: [0.16, 1, 0.3, 1] as const },
  },
};

export default function AboutPage() {
  const [about, setAbout] = useState<AboutPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAbout()
      .then(setAbout)
      .catch((err) => {
        if (err.response?.status !== 404) {
          setError(err.response?.data?.detail || '加载失败');
        }
      })
      .finally(() => setLoading(false));
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

  if (error) {
    return (
      <AnimatedPage className="mx-auto max-w-4xl py-20 text-center">
        <p className="text-text-muted dark:text-text-muted-dark">{error}</p>
      </AnimatedPage>
    );
  }

  if (!about) {
    return (
      <AnimatedPage className="mx-auto max-w-5xl">
        <motion.div variants={sectionVariants} initial="hidden" animate="visible">
          <p className="py-20 text-center text-text-muted dark:text-text-muted-dark">
            关于页尚未配置，请到后台管理进行设置。
          </p>
        </motion.div>
      </AnimatedPage>
    );
  }

  const techStackList = (() => {
    try {
      if (!about.tech_stack) return [];
      return JSON.parse(about.tech_stack) as string[];
    } catch {
      return [];
    }
  })();

  return (
    <AnimatedPage className="mx-auto max-w-5xl space-y-10">
      {/* Hero */}
      <motion.section variants={sectionVariants} initial="hidden" animate="visible">
        <HeroSection
          avatarUrl={about.avatar_url || undefined}
          eyebrow={about.eyebrow}
          title={about.title}
          heroSubtitle={about.hero_subtitle || undefined}
          coverImage={about.cover_image || undefined}
        />
      </motion.section>

      {/* Info cards */}
      {about.info_cards?.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <InfoCards items={about.info_cards ?? []} />
        </motion.section>
      )}

      {/* Tech stack */}
      {techStackList.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel accentLine className="p-6">
            <SectionNumber number="" label="常用技术栈" />
            <div className="mt-4 flex flex-wrap gap-2">
              {techStackList.map((tech) => (
                <span key={tech} className="lab-chip">{tech}</span>
              ))}
            </div>
          </GlassPanel>
        </motion.section>
      )}

      {/* Contact links */}
      {about.contacts?.length > 0 && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel accentLine className="p-6">
            <SectionNumber number="" label="联系方式" />
            <div className="mt-4">
              <ContactLinks contacts={about.contacts ?? []} />
            </div>
          </GlassPanel>
        </motion.section>
      )}

      {/* Content (collapsed) */}
      {about.content && about.content.trim() !== '' && (
        <motion.section variants={sectionVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
          <GlassPanel className="p-6 sm:p-8">
            <details className="group">
              <summary className="cursor-pointer select-none text-lg font-semibold text-text-primary dark:text-text-primary-dark">
                更多介绍
              </summary>
              <div className="mt-4">
                <ArticleContent content={about.content} />
              </div>
            </details>
          </GlassPanel>
        </motion.section>
      )}
    </AnimatedPage>
  );
}
