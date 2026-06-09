import { type ReactNode } from 'react';
import { motion } from 'framer-motion';

interface AnimatedSectionProps {
  children: ReactNode;
  className?: string;
  /** Content elements stagger delay per item (seconds) */
  staggerDelay?: number;
  /** Whether to animate only once */
  once?: boolean;
}

/**
 * Section wrapper that replicates the preview's section entrance/exit transitions:
 * - Slides in from below on enter
 * - Fades and moves up slightly on exit
 * - Uses spring easing matching preview's cubic-bezier(.25,1,.5,1)
 */
export default function AnimatedSection({
  children,
  className = '',
  staggerDelay = 0.06,
  once = false,
}: AnimatedSectionProps) {
  return (
    <motion.section
      className={className}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.8,
          ease: [0.25, 1, 0.5, 1],
          staggerChildren: staggerDelay,
          delayChildren: 0.05,
        },
      }}
      viewport={{
        once,
        amount: 0.08,
        margin: '0px 0px -60px 0px',
      }}
    >
      {children}
    </motion.section>
  );
}

/**
 * Individual child that reveals itself with a slide-up fade.
 * Use inside AnimatedSection for staggered reveals.
 */
export function RevealItem({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0, y: 60 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.7, ease: [0.25, 1, 0.5, 1] },
        },
      }}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '0px 0px -60px 0px' }}
    >
      {children}
    </motion.div>
  );
}
