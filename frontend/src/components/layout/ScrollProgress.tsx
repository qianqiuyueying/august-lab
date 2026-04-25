import { motion, useScroll, useTransform } from 'framer-motion';

export default function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-accent-start via-accent-mid to-accent-end origin-left z-50"
      style={{ scaleX }}
    />
  );
}
