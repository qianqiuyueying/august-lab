import { useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  maxRotation?: number;
  stiffness?: number;
  damping?: number;
}

/**
 * 3D tilt wrapper — tracks mouse position and applies perspective-based rotation.
 */
export default function TiltCard({
  children,
  className = '',
  maxRotation = 18,
  stiffness = 350,
  damping = 30,
}: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseX = useSpring(x, { stiffness, damping, mass: 0.5 });
  const mouseY = useSpring(y, { stiffness, damping, mass: 0.5 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const xNorm = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
    const yNorm = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
    x.set(xNorm * maxRotation);
    y.set(-yNorm * maxRotation);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      style={{ rotateX: mouseY, rotateY: mouseX, transformStyle: 'preserve-3d' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
    >
      {children}
    </motion.div>
  );
}
