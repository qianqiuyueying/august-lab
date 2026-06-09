import { useRef } from 'react';
import { useScroll, useTransform, type MotionValue } from 'framer-motion';

/**
 * Replicates preview's section state machine (entering → entered → leaving).
 *
 * Returns [ref, opacity, y] — attach ref to a <motion.section>,
 * use opacity and y as motion style values.
 */
export function useSectionTransition(): [
  React.RefObject<HTMLElement | null>,
  MotionValue<number>,
  MotionValue<number>,
] {
  const ref = useRef<HTMLElement | null>(null);

  // scroll progress: 0 = section bottom enters viewport, 1 = section top exits viewport
  const { scrollYProgress } = useScroll({
    target: ref as React.RefObject<HTMLElement>,
    offset: ['start end', 'end start'],
  });

  // Key thresholds:
  // ~0.06 = section just appearing at bottom of screen → entering (hidden)
  // ~0.12 = section top at viewport 50% mark → entered (fully visible)
  // ~0.85 = section leaving top of screen → leaving (dimmed)
  //
  // Opacity: 0 at 0.06 → 1 at 0.12 → 0.3 at 0.85
  const opacity = useTransform(
    scrollYProgress,
    [0.00, 0.06, 0.13, 0.85, 1.00],
    [0.00, 0.00, 1.00, 1.00, 0.30],
  );

  // Y: 40 at 0.06 → 0 at 0.12 → -20 at 0.85
  const y = useTransform(
    scrollYProgress,
    [0.00, 0.06, 0.13, 0.85, 1.00],
    [40.0, 40.0, 0.00, 0.00, -20.0],
  );

  return [ref, opacity, y];
}
