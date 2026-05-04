import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';
import TiltCard from '../ui/TiltCard';

interface ArticleCardProps {
  article: ArticleListItem;
  variant?: 'default' | 'featured';
}

export default function ArticleCard({ article, variant = 'default' }: ArticleCardProps) {
  const isFeatured = variant === 'featured';
  const readingTime = estimateReadingTime(`${article.title} ${article.summary}`);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';

  return (
    <Link to={`/articles/${article.slug}`} className="group block rounded-lg focus-ring">
      <TiltCard maxRotation={isFeatured ? 6 : 4}>
        <motion.div
          whileHover={{ boxShadow: '0 18px 45px rgba(37,99,235,0.11)' }}
          className={`overflow-hidden rounded-2xl border border-border/80 bg-paper/88 shadow-sm dark:border-border-dark/80 dark:bg-surface-dark/88 ${
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
                <span>{formatDate(article.created_at) || '未标注日期'}</span>
                <span aria-hidden="true">/</span>
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
      </TiltCard>
    </Link>
  );
}
