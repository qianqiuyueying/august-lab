"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { MascotEngine } from "./mascot-engine";
import type { AnimationName } from "./mascot-engine";

const SCALE = 1.0;
const MARGIN = 20;
const DRAG_THRESHOLD = 5;
const CLOSE_BTN = 20;
const CELL_W = 192;
const CELL_H = 208;
const RANDOM_INTERVAL = 12000;

const INTERACT_ANIMS: AnimationName[] = ["waving", "jumping"];
const RANDOM_ANIMS: { name: AnimationName; weight: number }[] = [
  { name: "waving", weight: 40 },
  { name: "jumping", weight: 25 },
  { name: "idle", weight: 35 },
];

function pickWeighted(items: typeof RANDOM_ANIMS): AnimationName {
  const total = items.reduce((s, i) => s + i.weight, 0);
  let r = Math.random() * total;
  for (const item of items) {
    r -= item.weight;
    if (r <= 0) return item.name;
  }
  return items[items.length - 1].name;
}

export default function MascotPet() {
  const [visible, setVisible] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<MascotEngine | null>(null);
  const dragOrigin = useRef({ x: 0, y: 0 });
  const dragElOrigin = useRef({ x: 0, y: 0 });
  const hasMoved = useRef(false);
  const randomTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mounted = useRef(false);

  const cssW = CELL_W * SCALE;
  const cssH = CELL_H * SCALE;

  useEffect(() => {
    if (mounted.current) return;
    mounted.current = true;

    // Check dismissed
    if (typeof sessionStorage !== "undefined" && sessionStorage.getItem("mascot-dismissed") === "true") {
      return;
    }

    // Check mobile - hide on screens < 768px
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      return;
    }

    // Set position
    setPos({
      x: window.innerWidth - cssW - MARGIN,
      y: window.innerHeight - cssH - MARGIN,
    });

    // Delay canvas init slightly to ensure DOM is ready
    const timer = setTimeout(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      try {
        const engine = new MascotEngine(canvas, SCALE);
        engineRef.current = engine;

        engine.loadSprite("/mascot/spritesheet.webp").then(() => {
          engine.start();
          setVisible(true);
          startRandomTimer(engine);
        }).catch((err) => {
          console.error("Mascot sprite load failed:", err);
        });
      } catch (err) {
        console.error("Mascot engine init failed:", err);
      }
    }, 100);

    // Resize handler
    const onResize = () => {
      if (window.innerWidth < 768) {
        setVisible(false);
      } else {
        setPos((prev) => ({
          x: Math.max(0, Math.min(prev.x, window.innerWidth - cssW)),
          y: Math.max(0, Math.min(prev.y, window.innerHeight - cssH)),
        }));
      }
    };
    window.addEventListener("resize", onResize);

    return () => {
      clearTimeout(timer);
      if (randomTimer.current) clearTimeout(randomTimer.current);
      engineRef.current?.destroy();
      window.removeEventListener("resize", onResize);
    };
  }, []);

  const startRandomTimer = (engine: MascotEngine) => {
    const schedule = () => {
      if (randomTimer.current) clearTimeout(randomTimer.current);
      randomTimer.current = setTimeout(() => {
        engine.playAnimation(pickWeighted(RANDOM_ANIMS));
        schedule();
      }, RANDOM_INTERVAL + Math.random() * 6000);
    };
    schedule();
  };

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    const el = containerRef.current;
    if (!el) return;
    el.setPointerCapture(e.pointerId);
    dragOrigin.current = { x: e.clientX, y: e.clientY };
    dragElOrigin.current = { x: pos.x, y: pos.y };
    hasMoved.current = false;
    setIsDragging(true);

    const onMove = (ev: PointerEvent) => {
      const dx = ev.clientX - dragOrigin.current.x;
      const dy = ev.clientY - dragOrigin.current.y;
      if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
        hasMoved.current = true;
      }
      if (hasMoved.current) {
        setPos({
          x: Math.max(0, Math.min(dragElOrigin.current.x + dx, window.innerWidth - cssW)),
          y: Math.max(0, Math.min(dragElOrigin.current.y + dy, window.innerHeight - cssH)),
        });
      }
    };

    const onUp = () => {
      el.releasePointerCapture(e.pointerId);
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      setIsDragging(false);
      if (!hasMoved.current) {
        const anim = INTERACT_ANIMS[Math.floor(Math.random() * INTERACT_ANIMS.length)];
        engineRef.current?.playAnimation(anim);
      }
    };

    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp);
  }, [pos, cssW, cssH]);

  const handleDismiss = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setVisible(false);
    sessionStorage.setItem("mascot-dismissed", "true");
    engineRef.current?.destroy();
  }, []);

  if (!visible) return null;

  return (
    <div
      ref={containerRef}
      style={{
        position: "fixed",
        left: pos.x,
        top: pos.y,
        width: cssW,
        height: cssH,
        zIndex: 9999,
        cursor: isDragging ? "grabbing" : "grab",
        userSelect: "none",
      }}
      onPointerDown={handlePointerDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <canvas
        ref={canvasRef}
        width={cssW}
        height={cssH}
        style={{ width: cssW, height: cssH, pointerEvents: "none", display: "block" }}
      />
      <button
        style={{
          position: "absolute",
          top: -6,
          right: -6,
          width: CLOSE_BTN,
          height: CLOSE_BTN,
          borderRadius: "50%",
          background: "rgba(0,0,0,0.5)",
          color: "#fff",
          fontSize: 12,
          lineHeight: 1,
          border: "none",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: isHovered ? 1 : 0,
          transition: "opacity 0.2s",
        }}
        onClick={handleDismiss}
        aria-label="关闭看板娘"
      >
        ×
      </button>
    </div>
  );
}
