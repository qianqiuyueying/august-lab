const CELL_W = 192;
const CELL_H = 208;

export type AnimationName =
  | "idle"
  | "running-right"
  | "running-left"
  | "waving"
  | "jumping"
  | "failed"
  | "waiting"
  | "running"
  | "review";

interface AnimDef {
  row: number;
  frames: number;
  dur: number[];
  loop: boolean;
}

const ANIMS: Record<AnimationName, AnimDef> = {
  idle:          { row: 0, frames: 6, dur: [280, 110, 110, 140, 140, 320], loop: true },
  "running-right": { row: 1, frames: 8, dur: [120, 120, 120, 120, 120, 120, 120, 220], loop: false },
  "running-left":  { row: 2, frames: 8, dur: [120, 120, 120, 120, 120, 120, 120, 220], loop: false },
  waving:        { row: 3, frames: 4, dur: [140, 140, 140, 280], loop: false },
  jumping:       { row: 4, frames: 5, dur: [140, 140, 140, 140, 280], loop: false },
  failed:        { row: 5, frames: 8, dur: [140, 140, 140, 140, 140, 140, 140, 240], loop: false },
  waiting:       { row: 6, frames: 6, dur: [150, 150, 150, 150, 150, 260], loop: true },
  running:       { row: 7, frames: 6, dur: [120, 120, 120, 120, 120, 220], loop: true },
  review:        { row: 8, frames: 6, dur: [150, 150, 150, 150, 150, 280], loop: true },
};

export class MascotEngine {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private sprite: HTMLImageElement | null = null;
  private currentAnim: AnimationName = "idle";
  private frame = 0;
  private elapsed = 0;
  private lastTime = 0;
  private rafId: number | null = null;
  private running = false;
  private queuedAnim: AnimationName | null = null;
  private scale = 1;

  constructor(canvas: HTMLCanvasElement, scale = 1) {
    this.canvas = canvas;
    this.scale = scale;
    const w = Math.floor(CELL_W * scale);
    const h = Math.floor(CELL_H * scale);
    this.canvas.width = w;
    this.canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas 2D context not available");
    this.ctx = ctx;
    this.ctx.imageSmoothingEnabled = false;
  }

  async loadSprite(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { this.sprite = img; resolve(); };
      img.onerror = () => reject(new Error(`Failed to load sprite: ${url}`));
      img.src = url;
    });
  }

  playAnimation(name: AnimationName): void {
    const anim = ANIMS[name];
    if (this.currentAnim === name && anim.loop) return;
    const currentDef = ANIMS[this.currentAnim];
    if (!currentDef.loop && this.running) {
      this.queuedAnim = name;
      return;
    }
    this.currentAnim = name;
    this.frame = 0;
    this.elapsed = 0;
    this.queuedAnim = null;
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    this.frame = 0;
    this.elapsed = 0;
    this.lastTime = performance.now();
    this.drawCurrentFrame();
    this.rafId = requestAnimationFrame(this.tick);
  }

  stop(): void {
    this.running = false;
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  destroy(): void {
    this.stop();
    this.sprite = null;
  }

  private tick = (now: number): void => {
    if (!this.running) return;
    const dt = Math.min(now - this.lastTime, 1000);
    this.lastTime = now;
    this.elapsed += dt;
    const anim = ANIMS[this.currentAnim];
    let safety = 60;
    while (safety-- > 0) {
      const currentDur = anim.dur[this.frame];
      if (this.elapsed < currentDur) break;
      this.elapsed -= currentDur;
      if (this.frame + 1 >= anim.frames) {
        if (anim.loop) {
          this.frame = 0;
        } else {
          this.frame = 0;
          this.elapsed = 0;
          if (this.queuedAnim) {
            this.currentAnim = this.queuedAnim;
            this.queuedAnim = null;
          } else {
            this.currentAnim = "idle";
          }
          break;
        }
      } else {
        this.frame++;
      }
    }
    this.drawCurrentFrame();
    this.rafId = requestAnimationFrame(this.tick);
  };

  private drawCurrentFrame(): void {
    if (!this.sprite) return;
    const anim = ANIMS[this.currentAnim];
    const sW = Math.floor(CELL_W * this.scale);
    const sH = Math.floor(CELL_H * this.scale);
    this.ctx.clearRect(0, 0, sW, sH);
    this.ctx.drawImage(
      this.sprite,
      this.frame * CELL_W,
      anim.row * CELL_H,
      CELL_W,
      CELL_H,
      0, 0, sW, sH
    );
  }
}
