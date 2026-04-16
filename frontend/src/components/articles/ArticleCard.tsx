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
        whileHover={{ y: -4 }}
        className={`group bg-white dark:bg-zinc-900/50 rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-zinc-200/60 dark:border-zinc-800/60 ${
          isFeatured ? 'grid grid-cols-1 md:grid-cols-2' : ''
        }`}
      >
        {/* Cover image or default fallback */}
        <div className={`${isFeatured ? '' : 'aspect-video'} overflow-hidden bg-gradient-to-br from-indigo-400 to-purple-500`}>
          {article.cover_image ? (
            <img
              src={article.cover_image}
              alt={article.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <img
              src="/images/cover-blog.webp"
              alt=""
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          )}
        </div>

        {/* Content */}
        <div className={`p-5 sm:p-6 ${isFeatured ? 'flex flex-col justify-center' : ''}`}>
          <h2
            className={`${
              isFeatured ? 'text-2xl sm:text-3xl' : 'text-lg sm:text-xl'
            } font-semibold text-zinc-900 dark:text-white group-hover:text-accent transition-colors leading-tight`}
          >
            {article.title}
          </h2>

          <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed mt-2 line-clamp-2">
            {article.summary}
          </p>

          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1.5">
            {readingTime} min read
          </p>

          {/* Divider + footer */}
          <div className="border-t border-zinc-100 dark:border-zinc-800 mt-4 pt-4 flex items-center justify-between">
            <div className="flex flex-wrap gap-1.5">
              {article.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="text-xs px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400"
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
