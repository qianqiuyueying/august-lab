import type { Fish, Bubble, Particle } from '../types';

let ctx: CanvasRenderingContext2D;
let W: number;
let H: number;

export function initRenderer(canvas: HTMLCanvasElement): void {
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Failed to get 2d context');
  ctx = context;
  resize(canvas);
  window.addEventListener('resize', () => resize(canvas));
}

function resize(canvas: HTMLCanvasElement): void {
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

export function getCanvasSize(): { width: number; height: number } {
  return { width: W, height: H };
}

export function draw(
  fishes: Fish[],
  player: Fish | null,
  particles: Particle[],
  bubbles: Bubble[],
  gameTime: number,
  gameRunning: boolean,
): void {
  drawBackground(gameTime, bubbles);
  drawFishLayer(fishes, player, gameRunning);
  drawParticlesLayer(particles);
}

function drawBackground(gameTime: number, bubbles: Bubble[]): void {
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, '#0a1628');
  grad.addColorStop(0.3, '#0d2137');
  grad.addColorStop(0.7, '#0a2a4a');
  grad.addColorStop(1, '#061224');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  ctx.save();
  ctx.globalAlpha = 0.03;
  for (let i = 0; i < 5; i++) {
    const x = W * 0.15 + i * W * 0.18;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x - 40 + Math.sin(gameTime * 0.3 + i) * 20, H);
    ctx.lineTo(x + 60 + Math.sin(gameTime * 0.3 + i) * 20, H);
    ctx.closePath();
    ctx.fillStyle = '#4fc3f7';
    ctx.fill();
  }
  ctx.restore();

  for (const b of bubbles) {
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(150,220,255,${b.alpha})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}

function drawFishLayer(fishes: Fish[], player: Fish | null, gameRunning: boolean): void {
  const sorted = [...fishes].filter(f => f.alive);
  sorted.sort((a, b) => a.size - b.size);
  for (const f of sorted) {
    drawFish(f);
  }

  if (gameRunning && player && player.alive) {
    drawFish(player);
  }
}

function drawFish(fish: Fish): void {
  ctx.save();
  ctx.translate(fish.x, fish.y);
  ctx.scale(fish.dir, 1);

  const s = fish.size;
  const tailWag = Math.sin(fish.tailPhase) * 0.4;
  const bodyWobble = Math.sin(fish.wobble) * 2;

  if (fish.isPlayer) {
    ctx.shadowColor = '#4fc3f7';
    ctx.shadowBlur = 15;
  }

  drawTail(s, tailWag, fish.color);
  drawBody(s, bodyWobble, fish.color);
  drawEye(s, bodyWobble);
  if (fish.isPlayer) drawMouth(s, bodyWobble);
  drawDorsalFin(s, bodyWobble, fish.color);

  ctx.shadowBlur = 0;
  ctx.restore();
}

function drawTail(s: number, tailWag: number, color: string): void {
  ctx.beginPath();
  ctx.moveTo(-s * 0.6, 0);
  ctx.lineTo(-s * 1.2, -s * 0.5 + Math.sin(tailWag) * s * 0.2);
  ctx.lineTo(-s * 1.2, s * 0.5 + Math.sin(tailWag) * s * 0.2);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.8;
  ctx.fill();
  ctx.globalAlpha = 1;
}

function drawBody(s: number, bodyWobble: number, color: string): void {
  ctx.beginPath();
  ctx.ellipse(0, bodyWobble, s * 0.7, s * 0.4, 0, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();

  ctx.beginPath();
  ctx.ellipse(s * 0.1, bodyWobble - s * 0.1, s * 0.4, s * 0.15, -0.2, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255,255,255,0.2)';
  ctx.fill();
}

function drawEye(s: number, bodyWobble: number): void {
  ctx.beginPath();
  ctx.arc(s * 0.3, bodyWobble - s * 0.08, s * 0.12, 0, Math.PI * 2);
  ctx.fillStyle = '#fff';
  ctx.fill();
  ctx.beginPath();
  ctx.arc(s * 0.33, bodyWobble - s * 0.08, s * 0.06, 0, Math.PI * 2);
  ctx.fillStyle = '#222';
  ctx.fill();
}

function drawMouth(s: number, bodyWobble: number): void {
  ctx.beginPath();
  ctx.arc(s * 0.6, bodyWobble + s * 0.05, s * 0.08, 0, Math.PI);
  ctx.strokeStyle = 'rgba(0,0,0,0.5)';
  ctx.lineWidth = 1;
  ctx.stroke();
}

function drawDorsalFin(s: number, bodyWobble: number, color: string): void {
  ctx.beginPath();
  ctx.moveTo(-s * 0.1, bodyWobble - s * 0.35);
  ctx.quadraticCurveTo(s * 0.1, bodyWobble - s * 0.6, s * 0.3, bodyWobble - s * 0.35);
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.6;
  ctx.fill();
  ctx.globalAlpha = 1;
}

function drawParticlesLayer(particles: Particle[]): void {
  for (const p of particles) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r * p.life, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.globalAlpha = p.life;
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}
