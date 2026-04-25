import { motion } from 'framer-motion';

const fadeIn = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
};

interface AnimatedPageProps {
  children: React.ReactNode;
  className?: string;
}

export default function AnimatedPage({ children, className = '' }: AnimatedPageProps) {
  return (
    <motion.section
      initial="initial"
      animate="animate"
      variants={fadeIn}
      className={className}
    >
      {children}
    </motion.section>
  );
}
