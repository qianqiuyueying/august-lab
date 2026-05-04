import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';

interface ArticleCardProps {
  article: ArticleListItem;
  variant?: 'default' | 'featured' | 'compact';
  index?: number; // for experiment numbering
}

export default function ArticleCard({ article, variant = 'default', index }: ArticleCardProps) {
  const isFeatured = variant === 'featured';
  const isCompact = variant === 'compact';
  const readingTime = estimateReadingTime(`${article.title} ${article.summary}`);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';
  const expNumber = index != null ? String(index + 1).padStart(2, '0') : '';

  // Compact variant: text-only with number column
  if (isCompact) {
    return (
      <Link to={`/articles/${article.slug}`} className="group block rounded-xl focus-ring">
        <motion.div
          whileHover={{ y: -2 }}
          className="flex gap-4 rounded-xl border border-border/80 bg-paper/88 p-4 shadow-sm transition-colors group-hover:border-accent/30 dark:border-border-dark/80 dark:bg-surface-dark/88"
        >
          {expNumber && (
            <span className="hidden sm:block font-mono text-2xl font-bold text-text-muted/15 dark:text-text-muted-dark/10 leading-none pt-1">
              {expNumber}
            </span>
          )}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 text-xs font-bold text-text-muted dark:text-text-muted-dark">
              <span>{formatDate(article.created_at) || '未标注日期'}</span>
              <span aria-hidden="true">·</span>
              <span>{readingTime} min</span>
            </div>
            <h3 className="mt-1 text-lg font-extrabold text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark truncate">
              {article.title}
            </h3>
            <p className="mt-1 line-clamp-2 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
              {article.summary}
            </p>
            {article.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {article.tags.slice(0, 3).map((tag) => (
                  <span key={tag.id} className="lab-chip text-[10px] px-1.5 py-0.5">
                    #{tag.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </Link>
    );
  }

  // Featured / Default variant
  return (
    <Link to={`/articles/${article.slug}`} className="group block rounded-xl focus-ring">
      <motion.div
        whileHover={{ boxShadow: '0 18px 45px rgba(37,99,235,0.11)' }}
        className={`lab-card overflow-hidden ${
          isFeatured ? 'grid gap-0 md:grid-cols-[0.9fr_1.1fr]' : 'grid gap-0 sm:grid-cols-[13rem_1fr]'
        }`}
      >
        <div className={`${isFeatured ? 'min-h-[16rem]' : 'min-h-[11rem]'} relative overflow-hidden bg-paper-soft dark:bg-background-dark`}>
          <img
            src={cover}
            alt={article.cover_image ? article.title : ''}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
            aria-hidden={!article.cover_image}
          />
        </div>

        <div className={`${isFeatured ? 'p-7 sm:p-8' : 'p-5 sm:p-6'} flex min-w-0 flex-col justify-between`}>
          <div>
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs font-bold text-text-muted dark:text-text-muted-dark">
              {expNumber && (
                <span className="font-mono text-[10px] text-accent/70 dark:text-accent/50">
                  EXP-{expNumber}
                </span>
              )}
              <span>{formatDate(article.created_at) || '未标注日期'}</span>
              <span aria-hidden="true">·</span>
              <span>{readingTime} min read</span>
            </div>
            <h2 className={`${isFeatured ? 'text-2xl sm:text-3xl' : 'text-xl'} font-extrabold leading-tight text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark`}>
              {article.title}
            </h2>
            <p className="mt-3 line-clamp-3 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
              {article.summary}
            </p>
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-border/80 pt-4 dark:border-border-dark/80">
            <div className="flex flex-wrap gap-2">
              {article.tags.slice(0, 3).map((tag) => (
                <span key={tag.id} className="lab-chip">
                  #{tag.name}
                </span>
              ))}
            </div>
            <span className="text-sm font-bold text-accent">阅读</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
