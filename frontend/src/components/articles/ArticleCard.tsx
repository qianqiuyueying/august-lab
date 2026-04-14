import { Link } from 'react-router-dom';
import type { ArticleListItem } from '../../types';
import { formatDate } from '../../utils/formatDate';

interface ArticleCardProps {
  article: ArticleListItem;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  return (
    <article className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow p-6">
      <Link to={`/articles/${article.slug}`} className="block">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 mb-2">
          {article.title}
        </h2>
      </Link>
      <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">{article.summary}</p>
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-2">
          {article.tags.map((tag) => (
            <Link
              key={tag.id}
              to={`/?tag=${tag.name}`}
              className="bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-xs px-2 py-1 rounded hover:bg-indigo-200 dark:hover:bg-indigo-800"
            >
              #{tag.name}
            </Link>
          ))}
        </div>
        <time className="text-sm text-gray-500 dark:text-gray-400">
          {formatDate(article.created_at)}
        </time>
      </div>
    </article>
  );
}
