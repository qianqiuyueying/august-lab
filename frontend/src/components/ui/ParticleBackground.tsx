import { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  size: number;
  speed: number;
  opacity: number;
  warm: boolean; // true = amber, false = cyan
  wobble: number;
}

const MAX = 60;

export function PreviewParticles() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animFrameRef = useRef<number>(0);
  const lastScrollRef = useRef(0);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Init particles
    particlesRef.current = Array.from({ length: MAX }, () => {
      const p = newParticle(canvas);
      p.y = Math.random() * canvas.height; // spread across screen initially
      return p;
    });

    function newParticle(c: HTMLCanvasElement): Particle {
      return {
        x: Math.random() * c.width,
        y: c.height + 10,
        size: Math.random() * 2 + 0.5,
        speed: 0.2 + Math.random() * 0.6,
        opacity: Math.random() * 0.4 + 0.1,
        warm: Math.random() > 0.6, // 40% warm amber, 60% cool cyan
        wobble: Math.random() * 2,
      };
    }

    const draw = () => {
      const c = canvas;
      const scrollSpeed = Math.abs(window.scrollY - lastScrollRef.current) * 0.02;
      lastScrollRef.current = window.scrollY;

      ctx.clearRect(0, 0, c.width, c.height);

      for (const p of particlesRef.current) {
        p.y -= p.speed + scrollSpeed * 0.3;
        p.x += Math.sin(p.y * 0.01 + p.wobble) * 0.3;

        if (p.y < -10) {
          Object.assign(p, newParticle(c));
          p.y = c.height + 10;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        const color = p.warm
          ? `rgba(200,132,60,${p.opacity})`
          : `rgba(59,165,196,${p.opacity})`;
        ctx.fillStyle = color;
        ctx.fill();
      }

      animFrameRef.current = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-0"
      aria-hidden="true"
    />
  );
}
