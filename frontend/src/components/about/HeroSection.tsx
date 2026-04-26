import type { CSSProperties } from 'react';

interface HeroSectionProps {
  avatarUrl?: string;
  eyebrow: string;
  title: string;
  heroSubtitle?: string;
  coverImage?: string;
}

export default function HeroSection({
  avatarUrl,
  eyebrow,
  title,
  heroSubtitle,
  coverImage,
}: HeroSectionProps) {
  const hasContent = avatarUrl || heroSubtitle;
  if (!hasContent && !eyebrow && !title) return null;

  const bgStyle: CSSProperties = coverImage
    ? { backgroundImage: `url(${coverImage})`, backgroundSize: 'cover', backgroundPosition: 'center' }
    : {};

  return (
    <section className="relative rounded-2xl overflow-hidden border border-border bg-paper shadow-md dark:border-border-dark dark:bg-surface-dark" style={bgStyle}>
      {coverImage && <div className="absolute inset-0 bg-black/40 dark:bg-black/50" />}

      <div className="relative z-10 flex flex-col items-center text-center py-12 sm:py-16 px-6">
        {avatarUrl && (
          <img
            src={avatarUrl}
            alt=""
            className="w-24 h-24 sm:w-[120px] sm:h-[120px] rounded-full object-cover border-4 border-white/80 shadow-lg mb-6 dark:border-zinc-700/80"
          />
        )}
        <p className="section-label mb-2">{eyebrow}</p>
        <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl">
          {title}
        </h1>
        {heroSubtitle && (
          <p className="mt-4 text-base leading-8 text-text-secondary dark:text-text-secondary-dark sm:text-lg">
            {heroSubtitle}
          </p>
        )}
      </div>
    </section>
  );
}
