import { Link } from 'react-router-dom';
import { useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';

interface ArticleCardProps {
  article: ArticleListItem;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const readingTime = estimateReadingTime(`${article.title} ${article.summary}`);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';
  const ref = useRef<HTMLDivElement>(null);
  const rx = useSpring(useMotionValue(0), { stiffness: 350, damping: 30 });
  const ry = useSpring(useMotionValue(0), { stiffness: 350, damping: 30 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    rx.set(-y * 6);
    ry.set(x * 6);
  };

  const handleMouseLeave = () => {
    rx.set(0);
    ry.set(0);
  };

  return (
    <Link to={`/articles/${article.slug}`} className="group block focus-ring" style={{ perspective: '800px', transformStyle: 'preserve-3d' }}>
      <motion.div
        ref={ref}
        style={{
          rotateX: rx as any,
          rotateY: ry as any,
          transformStyle: 'preserve-3d',
        }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="overflow-hidden rounded-[14px] border border-border bg-paper-soft backdrop-blur-xl transition-all duration-500 ease-[cubic-bezier(.16,1,.3,1)] hover:-translate-y-1 hover:border-accent-mid/40 hover:shadow-[0_20px_60px_rgba(0,0,0,.3),0_0_0_1px_rgba(59,165,196,.4)]"
      >
        {/* Cover image */}
        <div className="relative aspect-[16/10] overflow-hidden bg-background">
          <img
            src={cover}
            alt={article.cover_image ? article.title : ''}
            loading="lazy"
            decoding="async"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
            aria-hidden={!article.cover_image}
          />
        </div>

        {/* Body */}
        <div className="p-[16px_18px_14px]">
          <div className="text-xs text-text-muted">
            {formatDate(article.created_at) || '未标注日期'} · {readingTime} min
          </div>
          <h3 className="my-[6px] text-base font-[740] text-paper transition-colors group-hover:text-accent line-clamp-2">
            {article.title}
          </h3>
          <p className="line-clamp-2 text-[13px] leading-relaxed text-text-muted">
            {article.summary}
          </p>
          <div className="mt-2 flex flex-wrap gap-[6px]">
            {article.tags.slice(0, 3).map((tag) => (
              <span key={tag.id} className="rounded-full bg-blueprint/15 px-[11px] py-[3px] text-[11px] font-bold text-blueprint">
                #{tag.name}
              </span>
            ))}
          </div>
          <div className="mt-[10px] border-t border-border pt-2 text-[13px] font-bold text-accent opacity-60 transition-opacity group-hover:opacity-100">
            阅读
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
