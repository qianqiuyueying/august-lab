import { motion } from 'framer-motion';

export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <motion.div
      className={`rounded-lg bg-zinc-200 dark:bg-zinc-800 ${className}`}
      animate={{ opacity: [0.4, 0.7, 0.4] }}
      transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
    />
  );
}
