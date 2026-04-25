import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';
import { estimateReadingTime } from '../../utils/readingTime';

interface ArticleCardProps {
  article: ArticleListItem;
  variant?: 'default' | 'featured';
}

export default function ArticleCard({ article, variant = 'default' }: ArticleCardProps) {
  const isFeatured = variant === 'featured';
  const readingTime = estimateReadingTime(article.summary);

  return (
    <Link to={`/articles/${article.slug}`} className="block">
      <motion.article
        whileHover={{ y: isFeatured ? -4 : -2 }}
        className={`group rounded-xl overflow-hidden border border-zinc-200/60 dark:border-zinc-800/60 bg-white/60 dark:bg-zinc-900/40 backdrop-blur-sm shadow-sm hover:shadow-lg transition-all duration-300 card-glow ${
          isFeatured ? 'grid grid-cols-1 md:grid-cols-2' : ''
        }`}
      >
        {/* Cover image or default fallback */}
        <div className={`${isFeatured ? '' : 'hidden md:block'} aspect-video overflow-hidden bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900`}>
          {article.cover_image ? (
            <img
              src={article.cover_image}
              alt={article.title}
              className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <svg className="w-10 h-10 text-zinc-300 dark:text-zinc-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            </div>
          )}
        </div>

        {/* Content */}
        <div className={`p-5 sm:p-6 ${isFeatured ? 'flex flex-col justify-center' : ''}`}>
          <h2
            className={`${
              isFeatured ? 'text-xl sm:text-2xl' : 'text-base sm:text-lg'
            } font-semibold text-zinc-900 dark:text-white leading-tight tracking-tight group-hover:text-accent-start dark:group-hover:text-accent-mid transition-colors`}
          >
            {article.title}
          </h2>

          <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed mt-2.5 line-clamp-2">
            {article.summary}
          </p>

          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1.5">
            {readingTime} min read
          </p>

          {/* Divider + footer */}
          <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
            <div className="flex flex-wrap gap-1.5">
              {article.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag.id}
                  className="text-xs px-2 py-0.5 rounded-full bg-zinc-100/80 dark:bg-zinc-800/80 text-zinc-500 dark:text-zinc-400"
                >
                  #{tag.name}
                </span>
              ))}
            </div>
            <time className="text-xs text-zinc-400 dark:text-zinc-500 whitespace-nowrap ml-3">
              {formatDate(article.created_at)}
            </time>
          </div>
        </div>
      </motion.article>
    </Link>
  );
}
