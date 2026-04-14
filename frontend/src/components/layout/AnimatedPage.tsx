import { motion } from 'framer-motion';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
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
