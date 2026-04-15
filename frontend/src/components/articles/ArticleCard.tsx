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
    <motion.article
      whileHover={{ y: -4 }}
      className={`group bg-white dark:bg-zinc-900/50 rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-zinc-200/60 dark:border-zinc-800/60 ${
        isFeatured ? 'grid grid-cols-1 md:grid-cols-2' : ''
      }`}
    >
      {/* Cover image or default fallback */}
      <div className={`${isFeatured ? '' : 'aspect-video'} overflow-hidden`}>
        {article.cover_image ? (
          <img
            src={article.cover_image}
            alt={article.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <img
            src="/assets/cover-blog.png"
            alt=""
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        )}
      </div>

      {/* Content */}
      <div className={`p-5 sm:p-6 ${isFeatured ? 'flex flex-col justify-center' : ''}`}>
        <Link to={`/articles/${article.slug}`} className="block">
          <h2
            className={`${
              isFeatured ? 'text-2xl sm:text-3xl' : 'text-lg sm:text-xl'
            } font-semibold text-zinc-900 dark:text-white group-hover:text-accent transition-colors leading-tight`}
          >
            {article.title}
          </h2>
        </Link>

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
              <Link
                key={tag.id}
                to={`/?tag=${tag.name}`}
                className="text-xs px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                #{tag.name}
              </Link>
            ))}
          </div>
          <time className="text-xs text-zinc-400 dark:text-zinc-500 whitespace-nowrap ml-3">
            {formatDate(article.created_at)}
          </time>
        </div>
      </div>
    </motion.article>
  );
}
