import type { Comment } from '../../types';
import { formatDate } from '../../utils/formatDate';

interface CommentListProps {
  comments: Comment[];
  loading: boolean;
}

export default function CommentList({ comments, loading }: CommentListProps) {
  if (loading) return <div className="text-gray-500">加载评论中...</div>;
  if (comments.length === 0) return <div className="text-gray-500">暂无评论</div>;

  return (
    <div className="space-y-4">
      {comments.map((comment) => (
        <div key={comment.id} className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium text-gray-900 dark:text-white">{comment.author_name}</span>
            <time className="text-sm text-gray-500 dark:text-gray-400">{formatDate(comment.created_at)}</time>
          </div>
          <p className="text-gray-700 dark:text-gray-300">{comment.content}</p>
        </div>
      ))}
    </div>
  );
}
