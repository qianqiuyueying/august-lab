import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';
import TiltCard from '../ui/TiltCard';

interface ArticleCardProps {
  article: ArticleListItem;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const readingTime = estimateReadingTime(`${article.title} ${article.summary}`);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';

  return (
    <Link to={`/articles/${article.slug}`} className="group block rounded-xl focus-ring">
      <TiltCard maxRotation={6}>
        <motion.div
          whileHover={{ boxShadow: '0 18px 45px rgba(37,99,235,0.11)' }}
          className="gradient-border flex overflow-hidden rounded-xl border border-border/80 bg-paper/88 shadow-sm dark:border-border-dark/80 dark:bg-surface-dark/88"
        >
          <div className="relative w-36 shrink-0 overflow-hidden bg-paper-soft dark:bg-background-dark">
            <img
              src={cover}
              alt={article.cover_image ? article.title : ''}
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
              aria-hidden={!article.cover_image}
            />
          </div>

          <div className="flex min-w-0 flex-1 flex-col justify-between p-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold text-text-muted dark:text-text-muted-dark">
                <span>{formatDate(article.created_at) || '未标注日期'}</span>
                <span aria-hidden="true">·</span>
                <span>{readingTime} min</span>
              </div>
              <h3 className="mt-1 text-lg font-extrabold leading-tight text-text-primary transition-colors group-hover:text-accent dark:text-text-primary-dark line-clamp-2">
                {article.title}
              </h3>
              <p className="mt-1 line-clamp-2 text-sm leading-6 text-text-secondary dark:text-text-secondary-dark">
                {article.summary}
              </p>
            </div>

            <div className="mt-3 flex items-center justify-between gap-3 border-t border-border/80 pt-3 dark:border-border-dark/80">
              <div className="flex flex-wrap gap-1.5">
                {article.tags.slice(0, 3).map((tag) => (
                  <span key={tag.id} className="lab-chip text-[10px] px-1.5 py-0.5">
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
