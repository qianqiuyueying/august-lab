import type { CSSProperties } from 'react';
import GlassPanel from '../ui/GlassPanel';

interface HeroSectionProps {
  avatarUrl?: string;
  eyebrow?: string | null;
  title?: string | null;
  heroSubtitle?: string | null;
  coverImage?: string | null;
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
    <GlassPanel className="relative overflow-hidden" accentLine>
      <div className="absolute inset-0" style={bgStyle} />
      {coverImage && <div className="absolute inset-0 bg-black/50" />}

      <div className="relative z-10 flex flex-col items-center text-center py-12 sm:py-16 px-6">
        {avatarUrl && (
          <img
            src={avatarUrl}
            alt=""
            loading="lazy"
            decoding="async"
            className="w-24 h-24 sm:w-[120px] sm:h-[120px] rounded-full object-cover border-4 border-border/50 shadow-lg mb-6"
          />
        )}
        <p className="section-label mb-2">{eyebrow}</p>
        <h1 className="text-4xl font-extrabold leading-[1.08] text-paper sm:text-5xl">
          {title}
        </h1>
        {heroSubtitle && (
          <p className="mt-4 text-base leading-8 text-text-secondary sm:text-lg">
            {heroSubtitle}
          </p>
        )}
      </div>
    </GlassPanel>
  );
}
