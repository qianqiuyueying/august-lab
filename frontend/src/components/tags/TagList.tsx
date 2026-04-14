import { Link } from 'react-router-dom';
import type { Tag } from '../../types';

interface TagListProps {
  tags: Tag[];
  loading: boolean;
}

export default function TagList({ tags, loading }: TagListProps) {
  if (loading) return <div className="text-gray-500">加载中...</div>;

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <Link
          key={tag.id}
          to={`/?tag=${tag.name}`}
          className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-full text-sm hover:bg-indigo-100 dark:hover:bg-indigo-900 hover:text-indigo-700 dark:hover:text-indigo-300"
        >
          #{tag.name}
        </Link>
      ))}
    </div>
  );
}
