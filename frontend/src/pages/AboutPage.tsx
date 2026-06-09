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

  const techStackList = (() => {
    try {
      if (!about?.tech_stack) return [];
      return JSON.parse(about.tech_stack) as string[];
    } catch {
      return [];
    }
  })();

  return (
    <div className="relative">
      {/* ===== Full-page background ===== */}
      <div className="fixed inset-0 z-0">
        <img
          src="/images/preview/s06_tent_bg_00001_.png"
          alt=""
          loading="lazy"
          className="h-full w-full object-cover"
        />
      </div>

      {/* Foreground elements */}
      <div className="a-pulse glow-amber fixed z-1 pointer-events-none" style={{ width: 'clamp(90px,11vw,180px)', top: '6%', left: '50%', transform: 'translateX(-50%)' }}>
        <img src="/images/preview/s06_lantern_00001_.png" alt="" className="w-full h-auto" />
      </div>
      <div className="a-float1 fixed z-1 pointer-events-none" style={{ width: 'clamp(90px,12vw,200px)', top: '48%', left: '3%' }}>
        <img src="/images/preview/s06_telescope_00001_.png" alt="" className="w-full h-auto" />
      </div>
      <div className="a-float2 fixed z-1 pointer-events-none" style={{ width: 'clamp(70px,9vw,150px)', top: '42%', right: '4%' }}>
        <img src="/images/preview/s06_diary_v2_00001_.png" alt="" className="w-full h-auto" />
      </div>

      <AnimatedPage className="relative z-10 mx-auto max-w-5xl space-y-10">
        {error ? (
          <div className="py-20 text-center">
            <p className="text-text-muted">{error}</p>
          </div>
        ) : !about ? (
          <div className="py-20 text-center">
            <p className="text-text-muted">关于页尚未配置，请到后台管理进行设置。</p>
          </div>
        ) : (
          <>
            {/* Page header */}
            <div className="text-center pt-[clamp(80px,14vh,140px)]">
              <p className="text-xs font-extrabold text-accent tracking-wider uppercase mb-2">About</p>
              <h1 className="text-paper mb-3">august&apos; lab</h1>
              <p className="text-text-muted max-w-md mx-auto text-sm sm:text-base">
                一个记录技术探索、产品实践和长期思考的个人空间。
              </p>
            </div>

            {/* Hero section */}
            <motion.section
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}
            >
              <HeroSection
                avatarUrl={about.avatar_url || undefined}
                eyebrow={about.eyebrow}
                title={about.title}
                heroSubtitle={about.hero_subtitle || undefined}
                coverImage={about.cover_image || undefined}
              />
            </motion.section>

            {/* Info cards */}
            {about.info_cards && about.info_cards.length > 0 && (
              <motion.section
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}
              >
                <InfoCards items={about.info_cards ?? []} />
              </motion.section>
            )}

            {/* Tech stack */}
            {techStackList.length > 0 && (
              <motion.section
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}
              >
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
            {about.contacts && about.contacts.length > 0 && (
              <motion.section
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}
              >
                <GlassPanel accentLine className="p-6">
                  <SectionNumber number="" label="联系方式" />
                  <div className="mt-4">
                    <ContactLinks contacts={about.contacts ?? []} />
                  </div>
                </GlassPanel>
              </motion.section>
            )}

            {/* Collapsible content */}
            {about.content && about.content.trim() !== '' && (
              <motion.section
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: [0.25, 1, 0.5, 1] }}
              >
                <GlassPanel className="p-6 sm:p-8">
                  <details className="group">
                    <summary className="cursor-pointer select-none text-lg font-semibold text-accent">
                      更多介绍
                    </summary>
                    <div className="mt-4">
                      <ArticleContent content={about.content} />
                    </div>
                  </details>
                </GlassPanel>
              </motion.section>
            )}
          </>
        )}
      </AnimatedPage>
    </div>
  );
}
