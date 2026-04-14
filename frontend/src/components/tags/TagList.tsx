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
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: 'spring' as const, stiffness: 400, damping: 25 },
  },
};

export default function TagList({ tags, loading }: TagListProps) {
  if (loading) return <div className="text-zinc-500 text-sm">加载中...</div>;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-wrap gap-2"
    >
      {tags.map((tag) => (
        <motion.div key={tag.id} variants={itemVariants}>
          <motion.div whileHover={{ scale: 1.1 }}>
            <Link
              to={`/?tag=${tag.name}`}
              className="block bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 px-3 py-1 rounded-full text-sm hover:bg-indigo-100 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              #{tag.name}
            </Link>
          </motion.div>
        </motion.div>
      ))}
    </motion.div>
  );
}
