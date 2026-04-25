import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { Tag } from '../../types';

interface TagListProps {
  tags: Tag[];
  loading: boolean;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.85 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: 'spring' as const, stiffness: 400, damping: 25 },
  },
};

export default function TagList({ tags, loading }: TagListProps) {
  if (loading) return <div className="text-zinc-400 dark:text-zinc-500 text-sm">加载中...</div>;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-wrap gap-1.5"
    >
      {tags.map((tag) => (
        <motion.div key={tag.id} variants={itemVariants}>
          <Link
            to={`/?tag=${tag.name}`}
            className="inline-block bg-zinc-100/80 dark:bg-zinc-800/80 text-zinc-500 dark:text-zinc-400 px-2.5 py-1 rounded-full text-xs font-medium hover:bg-zinc-200/80 dark:hover:bg-zinc-700/80 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
          >
            #{tag.name}
          </Link>
        </motion.div>
      ))}
    </motion.div>
  );
}
