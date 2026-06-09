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
  if (loading) return <div className="text-sm text-text-muted">标签加载中...</div>;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-wrap gap-2"
    >
      {tags.map((tag) => (
        <motion.div key={tag.id} variants={itemVariants}>
          <Link
            to={`/blog?tag=${encodeURIComponent(tag.name)}`}
            className="lab-chip hover:border-accent-mid/50 hover:bg-blueprint/30 hover:text-paper"
          >
            #{tag.name}
          </Link>
        </motion.div>
      ))}
    </motion.div>
  );
}
