import { useRef } from 'react';
import { useScroll, useTransform, type MotionValue } from 'framer-motion';

/**
 * Returns a MotionValue<number> for parallax translateY based on scroll position
 * relative to the section.
 *
 * @param speed — parallax speed factor (preview: 0.015–0.07)
 * @returns [ref, y] — attach ref to the section, use y for translateY
 */
export function useParallax(speed: number): [React.RefObject<HTMLElement | null>, MotionValue<number>] {
  const ref = useRef<HTMLElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref as React.RefObject<HTMLElement>,
    offset: ['start end', 'end start'],
  });
  const y = useTransform(scrollYProgress, [0, 1], [speed * 100, -speed * 100]);
  return [ref, y];
}

/**
 * Simplified parallax — returns a y value for use with motion.div style={{ y }}.
 * The stronger the speed, the more the element moves relative to scroll.
 */
export function useParallaxY(speed: number): MotionValue<number> {
  const { scrollY } = useScroll();
  return useTransform(scrollY, [0, 3000], [0, -speed * 200]);
}
