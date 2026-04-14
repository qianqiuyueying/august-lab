import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';

interface ArticleCardProps {
  article: ArticleListItem;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  return (
    <motion.article
      whileHover={{ y: -2 }}
      className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 hover:shadow-lg transition-shadow p-6"
    >
      <Link to={`/articles/${article.slug}`} className="block">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white hover:text-accent dark:hover:text-accent mb-2 transition-colors">
          {article.title}
        </h2>
      </Link>
      <p className="text-zinc-600 dark:text-zinc-400 mb-4 line-clamp-3 leading-relaxed">
        {article.summary}
      </p>
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-2">
          {article.tags.map((tag) => (
            <motion.div key={tag.id} whileHover={{ scale: 1.08 }}>
              <Link
                to={`/?tag=${tag.name}`}
                className="bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 text-xs px-2.5 py-1 rounded-full hover:bg-indigo-100 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                #{tag.name}
              </Link>
            </motion.div>
          ))}
        </div>
        <time className="text-sm text-zinc-400 dark:text-zinc-500">
          {formatDate(article.created_at)}
        </time>
      </div>
    </motion.article>
  );
}
