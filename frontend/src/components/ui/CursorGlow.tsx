import { useEffect, useRef } from 'react';

/**
 * Replicates the preview's cursor-glow: a radial gradient that follows the mouse
 * with lerp smoothing (factor 0.08), appearing on hover and hiding on mouse leave.
 */
export default function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null);
  const targetRef = useRef({ x: 0, y: 0 });
  const currentRef = useRef({ x: 0, y: 0 });
  const visibleRef = useRef(false);
  const rafRef = useRef(0);

  useEffect(() => {
    const glow = glowRef.current;
    if (!glow) return;

    const onMove = (e: MouseEvent) => {
      targetRef.current = { x: e.clientX, y: e.clientY };
      if (!visibleRef.current) {
        visibleRef.current = true;
        glow.classList.remove('hidden');
      }
    };

    const onLeave = () => {
      visibleRef.current = false;
      glow.classList.add('hidden');
    };

    const tick = () => {
      const cx = currentRef.current.x;
      const cy = currentRef.current.y;
      const tx = targetRef.current.x;
      const ty = targetRef.current.y;

      currentRef.current = {
        x: cx + (tx - cx) * 0.08,
        y: cy + (ty - cy) * 0.08,
      };

      if (visibleRef.current) {
        glow.style.transform = `translate(${currentRef.current.x - 150}px, ${currentRef.current.y - 150}px)`;
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    document.addEventListener('mousemove', onMove, { passive: true });
    document.addEventListener('mouseleave', onLeave);
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseleave', onLeave);
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <div
      ref={glowRef}
      className="hidden"
      style={{
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: 9999,
        width: 300,
        height: 300,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(200,132,60,.08), transparent 70%)',
        transform: 'translate(-150px, -150px)',
        transition: 'opacity .3s',
      }}
      aria-hidden="true"
    />
  );
}
