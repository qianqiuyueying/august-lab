import { motion } from 'framer-motion';

export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <motion.div
      className={`rounded-lg border border-border bg-paper-soft dark:border-border-dark dark:bg-surface-dark ${className}`}
      animate={{ opacity: [0.45, 0.8, 0.45] }}
      transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
    />
  );
}
