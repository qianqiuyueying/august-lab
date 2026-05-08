import { useEffect, useRef, useState, useCallback } from 'react';
import { MascotEngine, type AnimationName } from './mascotEngine';
import ChatBubble from './ChatBubble';
import { getMascotSettings } from '../../api/mascot';
import type { MascotSettings } from '../../types';

const CELL_W = 192;
const CELL_H = 208;
const MARGIN = 20;
const DRAG_THRESHOLD = 5;
const CLOSE_BUTTON_SIZE = 20;
const BASE_RANDOM_INTERVAL = 10000;
const RANDOM_JITTER = 8000;
const INTERACTION_COOLDOWN = 3000;

const INTERACT_ANIMS: AnimationName[] = ['waving', 'jumping'];
const RANDOM_ANIMS: { name: AnimationName; weight: number }[] = [
  { name: 'waving', weight: 40 },
  { name: 'jumping', weight: 25 },
  { name: 'idle', weight: 35 },
];

function pickWeighted(items: { name: AnimationName; weight: number }[]): AnimationName {
  const total = items.reduce((s, i) => s + i.weight, 0);
  let r = Math.random() * total;
  for (const item of items) {
    r -= item.weight;
    if (r <= 0) return item.name;
  }
  return items[items.length - 1].name;
}

export default function MascotPet() {
  const [dismissed, setDismissed] = useState(() => sessionStorage.getItem('mascot-dismissed') === 'true');
  const [position, setPosition] = useState(() => ({
    x: window.innerWidth - CELL_W * 1.2 - MARGIN,
    y: window.innerHeight - CELL_H * 1.2 - MARGIN,
  }));
  const [isMobile, setIsMobile] = useState(() => window.matchMedia('(max-width: 767px)').matches);
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [settings, setSettings] = useState<MascotSettings | null>(null);
  const [chatVisible, setChatVisible] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<MascotEngine | null>(null);
  const dragOriginRef = useRef({ x: 0, y: 0 });
  const dragElementOriginRef = useRef({ x: 0, y: 0 });
  const hasMovedRef = useRef(false);
  const randomTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastInteractionRef = useRef(0);
  const scheduleRandomRef = useRef<() => void>(() => {});

  // Load remote settings
  useEffect(() => {
    getMascotSettings()
      .then((s) => {
        setSettings(s);
        if (s.mascot_position_x != null && s.mascot_position_y != null) {
          setPosition({ x: s.mascot_position_x, y: s.mascot_position_y });
        }
      })
      .catch(() => {
        // Fallback: mascot works with defaults even without API
      });
  }, []);

  // Derived values from settings (with safe defaults)
  const scale = settings?.mascot_scale ?? 1.2;
  const mascotVisible = settings?.mascot_visible ?? true;
  const showOnMobile = settings?.show_on_mobile ?? false;
  const dragEnabled = settings?.drag_enabled ?? true;
  const greetingEnabled = settings?.greeting_enabled ?? true;
  const greetingDelay = settings?.greeting_delay_seconds ?? 8;

  useEffect(() => {
    scheduleRandomRef.current = () => {
      if (randomTimerRef.current) clearTimeout(randomTimerRef.current);
      const delay = BASE_RANDOM_INTERVAL + Math.random() * RANDOM_JITTER;
      randomTimerRef.current = setTimeout(() => {
        const now = performance.now();
        if (now - lastInteractionRef.current < INTERACTION_COOLDOWN) {
          scheduleRandomRef.current();
          return;
        }
        const anim = pickWeighted(RANDOM_ANIMS);
        engineRef.current?.playAnimation(anim);
        scheduleRandomRef.current();
      }, delay);
    };
  });

  // Init engine & sprite loading
  useEffect(() => {
    if (dismissed || (isMobile && !showOnMobile) || !mascotVisible) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    let engine: MascotEngine;
    try {
      engine = new MascotEngine(canvas);
    } catch {
      return; // Canvas 2D not available (e.g. jsdom test environment)
    }
    engineRef.current = engine;

    engine.loadSprite('/mascot/spritesheet.webp').then(() => {
      engine.start();
      scheduleRandomRef.current();
    }).catch(() => {
      // Sprite failed to load — mascot stays hidden
    });

    const mql = window.matchMedia('(max-width: 767px)');
    const onMediaChange = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mql.addEventListener('change', onMediaChange);

    const onResize = () => {
      setPosition((prev) => ({
        x: Math.max(0, Math.min(prev.x, window.innerWidth - CELL_W * scale)),
        y: Math.max(0, Math.min(prev.y, window.innerHeight - CELL_H * scale)),
      }));
    };
    window.addEventListener('resize', onResize);

    return () => {
      engine.destroy();
      if (randomTimerRef.current) clearTimeout(randomTimerRef.current);
      mql.removeEventListener('change', onMediaChange);
      window.removeEventListener('resize', onResize);
    };
  }, [dismissed, isMobile, mascotVisible, scale]);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    const el = containerRef.current;
    if (!el) return;

    el.setPointerCapture(e.pointerId);
    dragOriginRef.current = { x: e.clientX, y: e.clientY };
    dragElementOriginRef.current = { x: position.x, y: position.y };
    hasMovedRef.current = false;
    setIsDragging(true);

    const onMove = (ev: PointerEvent) => {
      const dx = ev.clientX - dragOriginRef.current.x;
      const dy = ev.clientY - dragOriginRef.current.y;
      if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
        hasMovedRef.current = true;
      }
      if (hasMovedRef.current) {
        setPosition({
          x: Math.max(0, Math.min(dragElementOriginRef.current.x + dx, window.innerWidth - CELL_W * scale)),
          y: Math.max(0, Math.min(dragElementOriginRef.current.y + dy, window.innerHeight - CELL_H * scale)),
        });
      }
    };

    const onUp = () => {
      el.releasePointerCapture(e.pointerId);
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
      setIsDragging(false);

      if (!hasMovedRef.current) {
        lastInteractionRef.current = performance.now();
        if (settings?.enabled) {
          setChatVisible((prev) => !prev);
        } else {
          const anim = INTERACT_ANIMS[Math.floor(Math.random() * INTERACT_ANIMS.length)];
          engineRef.current?.playAnimation(anim);
        }
      }
    };

    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp);
  }, [position, scale, settings?.enabled]);

  const handleDismiss = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setDismissed(true);
    sessionStorage.setItem('mascot-dismissed', 'true');
  }, []);

  if (dismissed || (isMobile && !showOnMobile) || !mascotVisible) return null;

  const cssW = CELL_W * scale;
  const cssH = CELL_H * scale;

  return (
    <div
      ref={containerRef}
      className="fixed z-50 select-none"
      style={{
        left: position.x,
        top: position.y,
        width: cssW,
        height: cssH,
        cursor: dragEnabled ? (isDragging ? 'grabbing' : 'grab') : 'pointer',
      }}
      onPointerDown={dragEnabled ? handlePointerDown : undefined}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={CELL_W}
          height={CELL_H}
          style={{ width: cssW, height: cssH }}
          className="pointer-events-none block"
        />
        <ChatBubble
          visible={chatVisible}
          greetingEnabled={greetingEnabled}
          greetingDelaySeconds={greetingDelay}
          onClose={() => setChatVisible(false)}
        />
      </div>
      <button
        className="absolute rounded-full bg-black/50 text-white text-xs leading-none
                   flex items-center justify-center hover:bg-black/70 transition-opacity"
        style={{
          top: -6,
          right: -6,
          width: CLOSE_BUTTON_SIZE,
          height: CLOSE_BUTTON_SIZE,
          opacity: isHovered ? 1 : 0,
        }}
        onClick={handleDismiss}
        aria-label="关闭看板娘"
      >
        &times;
      </button>
    </div>
  );
}
