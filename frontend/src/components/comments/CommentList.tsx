import { motion } from 'framer-motion';
import type { Comment } from '../../types';
import { formatDate } from '../../utils/formatDate';

interface CommentListProps {
  comments: Comment[];
  loading: boolean;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.25, 0.1, 0.25, 1] as const } },
};

export default function CommentList({ comments, loading }: CommentListProps) {
  if (loading) return <div className="text-zinc-500 text-sm">加载评论中...</div>;
  if (comments.length === 0) return <div className="text-zinc-500 text-sm">暂无评论</div>;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      {comments.map((comment) => (
        <motion.div
          key={comment.id}
          variants={itemVariants}
          className="border-b border-zinc-200 dark:border-zinc-800 pb-4"
        >
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium text-zinc-900 dark:text-white">{comment.author_name}</span>
            <time className="text-sm text-zinc-500 dark:text-zinc-400">{formatDate(comment.created_at)}</time>
          </div>
          <p className="text-zinc-700 dark:text-zinc-300 leading-relaxed">{comment.content}</p>
        </motion.div>
      ))}
    </motion.div>
  );
}
