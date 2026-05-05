# Fish Feast — Engineering Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `tmp-game/index.html` (single-file inline HTML/CSS/JS demo) into a modular TypeScript + Vite project under `fish-feast/`

**Architecture:** Pure TypeScript with Vite for dev/build. Game logic split into `game/` modules (no DOM access), UI into `ui/` modules (DOM + CSS, read-only state access). `main.ts` is the sole glue layer.

**Tech Stack:** Vite 6.x, TypeScript 5.x, Canvas API, native DOM, zero framework

---

### Task 1: Rename directory and set up project scaffolding

**Files:**
- Rename: `tmp-game/` → `fish-feast/`
- Create: `fish-feast/package.json`
- Create: `fish-feast/tsconfig.json`
- Create: `fish-feast/vite.config.ts`

- [ ] **Step 1: Rename tmp-game to fish-feast**

```bash
cd g:\vscode\projects\blog-site
git mv tmp-game fish-feast
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "fish-feast",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "isolatedModules": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
});
```

- [ ] **Step 5: Install dependencies**

```bash
cd fish-feast
npm install
```

- [ ] **Step 6: Commit**

```bash
git add fish-feast/
git commit -m "chore: set up fish-feast project with Vite + TypeScript"
```

---

### Task 2: Create shared types and constants

**Files:**
- Create: `fish-feast/src/types.ts`
- Create: `fish-feast/src/constants.ts`

- [ ] **Step 1: Write src/types.ts**

```typescript
export interface Fish {
  x: number;
  y: number;
  size: number;
  vx: number;
  vy: number;
  speed: number;
  dir: 1 | -1;
  color: string;
  tailPhase: number;
  tailSpeed: number;
  isPlayer: boolean;
  wobble: number;
  wobbleSpeed: number;
  alive: boolean;
  behavior: 'wander' | 'flee' | 'chase';
  behaviorTimer: number;
}

export interface Bubble {
  x: number;
  y: number;
  r: number;
  speed: number;
  alpha: number;
}

export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
  color: string;
  life: number;
  decay: number;
}

export interface GameState {
  player: Fish;
  fishes: Fish[];
  bubbles: Bubble[];
  particles: Particle[];
  score: number;
  level: number;
  gameTime: number;
  difficulty: number;
  spawnTimer: number;
  running: boolean;
  paused: boolean;
  highScore: number;
  levelUpTimer: number;
  lastTime: number;
}

export interface InputState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  pauseTriggered: boolean;
}
```

- [ ] **Step 2: Write src/constants.ts**

```typescript
export const FISH_COLORS = [
  '#ff6b6b', '#ffa726', '#ffee58', '#66bb6a', '#26c6da',
  '#42a5f5', '#ab47bc', '#ef5350', '#29b6f6', '#9ccc65',
  '#ff7043', '#ec407a', '#7e57c2', '#26a69a', '#ffca28',
] as const;

export const PLAYER_COLOR = '#4fc3f7';

export const INITIAL_PLAYER_SIZE = 20;
export const INITIAL_FISH_COUNT = 15;
export const INITIAL_BUBBLE_COUNT = 20;
export const MAX_FISH_BASE = 25;

export const PLAYER_ACCEL = 0.4;
export const PLAYER_FRICTION = 0.92;
export const PLAYER_MAX_SPEED = 6;

export const FLEE_SPEED = 2;
export const CHASE_SPEED = 0.8;

export const SIZE_EAT_THRESHOLD = 1.05; // player must be >= fish * this to eat
export const SIZE_FLEE_RATIO = 0.8; // fish flees if smaller than player * this
export const SIZE_CHASE_RATIO = 1.35; // fish chases if larger than player * this
export const GROWTH_RATIO = 0.18; // how much player grows per eat
export const DETECT_BASE_RANGE = 200;
export const DETECT_RANGE_PER_DIFF = 20;

export const PARTICLE_EAT_COUNT = 12;
export const PARTICLE_LEVELUP_COUNT = 20;
export const PARTICLE_DEATH_COUNT = 30;

export const LEVEL_UP_DISPLAY_TIME = 1.5;

export const LS_HIGH_SCORE_KEY = 'fishGameHighScore';
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd fish-feast
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add fish-feast/src/types.ts fish-feast/src/constants.ts
git commit -m "chore: add shared types and constants for fish-feast"
```

---

### Task 3: Create game state module

**Files:**
- Create: `fish-feast/src/game/state.ts`

- [ ] **Step 1: Write src/game/state.ts**

```typescript
import type { GameState, Fish } from '../types';
import { INITIAL_PLAYER_SIZE, LS_HIGH_SCORE_KEY } from '../constants';
import { createFish, createBubble } from './spawner';

let state: GameState;

export function getState(): GameState {
  return state;
}

export function createState(canvasWidth: number, canvasHeight: number): GameState {
  const player = createFish(canvasWidth / 2, canvasHeight / 2, INITIAL_PLAYER_SIZE, true);
  player.dir = 1;
  player.vx = 0;
  player.vy = 0;

  const bubbles: ReturnType<typeof createBubble>[] = [];
  for (let i = 0; i < 20; i++) {
    bubbles.push(createBubble(canvasWidth, canvasHeight));
  }

  state = {
    player,
    fishes: spawnInitialFishes(canvasWidth, canvasHeight),
    bubbles,
    particles: [],
    score: 0,
    level: 1,
    gameTime: 0,
    difficulty: 1,
    spawnTimer: 0,
    running: false,
    paused: false,
    highScore: parseInt(localStorage.getItem(LS_HIGH_SCORE_KEY) || '0', 10),
    levelUpTimer: 0,
    lastTime: 0,
  };

  return state;
}

function spawnInitialFishes(W: number, H: number): Fish[] {
  const fishes: Fish[] = [];
  for (let i = 0; i < 15; i++) {
    const size = 5 + Math.random() * 25;
    const f = createFish(
      Math.random() * W,
      60 + Math.random() * (H - 120),
      size,
      false,
    );
    fishes.push(f);
  }
  return fishes;
}

export function resetState(canvasWidth: number, canvasHeight: number): GameState {
  return createState(canvasWidth, canvasHeight);
}

export function saveHighScore(score: number): void {
  if (score > state.highScore) {
    state.highScore = score;
    localStorage.setItem(LS_HIGH_SCORE_KEY, String(score));
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/state.ts
git commit -m "refactor: extract game state module"
```

---

### Task 4: Create spawner module

**Files:**
- Create: `fish-feast/src/game/spawner.ts`

- [ ] **Step 1: Write src/game/spawner.ts**

```typescript
import type { Fish, Bubble, Particle } from '../types';
import { FISH_COLORS, PLAYER_COLOR } from '../constants';

export function createFish(
  x: number | undefined,
  y: number | undefined,
  size: number | undefined,
  isPlayer: boolean,
  canvasWidth: number = window.innerWidth,
  canvasHeight: number = window.innerHeight,
  difficulty: number = 1,
): Fish {
  const actualSize = size ?? (8 + Math.random() * 30);
  const dir = isPlayer ? (1 as const) : (Math.random() < 0.5 ? 1 : -1) as 1 | -1;
  return {
    x: x ?? (dir > 0 ? -actualSize * 2 : canvasWidth + actualSize * 2),
    y: y ?? (50 + Math.random() * (canvasHeight - 100)),
    size: actualSize,
    vx: 0,
    vy: 0,
    speed: isPlayer ? 0 : (0.3 + Math.random() * 1.5) * (1 + difficulty * 0.1),
    dir,
    color: isPlayer ? PLAYER_COLOR : FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)],
    tailPhase: Math.random() * Math.PI * 2,
    tailSpeed: 3 + Math.random() * 2,
    isPlayer,
    wobble: 0,
    wobbleSpeed: 1 + Math.random() * 2,
    alive: true,
    behavior: 'wander' as const,
    behaviorTimer: Math.random() * 3,
  };
}

export function createBubble(canvasWidth: number, canvasHeight: number): Bubble {
  return {
    x: Math.random() * canvasWidth,
    y: canvasHeight + 10,
    r: 2 + Math.random() * 6,
    speed: 0.5 + Math.random() * 1.5,
    alpha: 0.1 + Math.random() * 0.3,
  };
}

export function createParticles(
  targetX: number,
  targetY: number,
  color: string,
  count: number,
  particles: Particle[],
): void {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 1 + Math.random() * 3;
    particles.push({
      x: targetX,
      y: targetY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      r: 1 + Math.random() * 3,
      color,
      life: 1,
      decay: 0.02 + Math.random() * 0.03,
    });
  }
}

export function spawnEnemyFish(playerSize: number, difficulty: number): Fish {
  const sizeRange = Math.max(5, playerSize * 0.3);
  const maxSize = playerSize * 1.5;
  const size = sizeRange + Math.random() * (maxSize - sizeRange);
  return createFish(undefined, undefined, size, false);
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/spawner.ts
git commit -m "refactor: extract spawner module with factory functions"
```

---

### Task 5: Create input module

**Files:**
- Create: `fish-feast/src/game/input.ts`

- [ ] **Step 1: Write src/game/input.ts**

```typescript
import type { InputState } from '../types';

const state: InputState = {
  up: false,
  down: false,
  left: false,
  right: false,
  pauseTriggered: false,
};

export function getInput(): InputState {
  return state;
}

export function consumePause(): boolean {
  if (state.pauseTriggered) {
    state.pauseTriggered = false;
    return true;
  }
  return false;
}

export function initInput(): void {
  document.addEventListener('keydown', (e) => {
    state.up = state.up || e.code === 'KeyW' || e.code === 'ArrowUp';
    state.down = state.down || e.code === 'KeyS' || e.code === 'ArrowDown';
    state.left = state.left || e.code === 'KeyA' || e.code === 'ArrowLeft';
    state.right = state.right || e.code === 'KeyD' || e.code === 'ArrowRight';

    if (e.code === 'KeyP' || e.code === 'Escape') {
      e.preventDefault();
      state.pauseTriggered = true;
    }
  });

  document.addEventListener('keyup', (e) => {
    if (e.code === 'KeyW' || e.code === 'ArrowUp') state.up = false;
    if (e.code === 'KeyS' || e.code === 'ArrowDown') state.down = false;
    if (e.code === 'KeyA' || e.code === 'ArrowLeft') state.left = false;
    if (e.code === 'KeyD' || e.code === 'ArrowRight') state.right = false;
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/input.ts
git commit -m "refactor: extract input module with keyboard handling"
```

---

### Task 6: Create player module

**Files:**
- Create: `fish-feast/src/game/player.ts`

- [ ] **Step 1: Write src/game/player.ts**

```typescript
import type { Fish } from '../types';
import type { InputState } from '../types';
import { PLAYER_ACCEL, PLAYER_FRICTION, PLAYER_MAX_SPEED } from '../constants';

export function updatePlayer(
  player: Fish,
  input: InputState,
  dt: number,
  canvasWidth: number,
  canvasHeight: number,
): void {
  let ax = 0;
  let ay = 0;

  if (input.up) ay -= 1;
  if (input.down) ay += 1;
  if (input.left) ax -= 1;
  if (input.right) ax += 1;

  const kLen = Math.sqrt(ax * ax + ay * ay);
  if (kLen > 0) {
    ax = (ax / kLen) * PLAYER_ACCEL;
    ay = (ay / kLen) * PLAYER_ACCEL;
  }

  player.vx += ax;
  player.vy += ay;
  player.vx *= PLAYER_FRICTION;
  player.vy *= PLAYER_FRICTION;

  const spd = Math.sqrt(player.vx * player.vx + player.vy * player.vy);
  if (spd > PLAYER_MAX_SPEED) {
    player.vx = (player.vx / spd) * PLAYER_MAX_SPEED;
    player.vy = (player.vy / spd) * PLAYER_MAX_SPEED;
  }

  player.x += player.vx * 60 * dt;
  player.y += player.vy * 60 * dt;

  if (Math.abs(player.vx) > 0.5) {
    player.dir = player.vx > 0 ? 1 : -1;
  }

  player.tailPhase += player.tailSpeed * dt;
  player.wobble += player.wobbleSpeed * dt;

  player.x = Math.max(player.size, Math.min(canvasWidth - player.size, player.x));
  player.y = Math.max(player.size + 40, Math.min(canvasHeight - player.size, player.y));
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/player.ts
git commit -m "refactor: extract player movement module"
```

---

### Task 7: Create enemy module

**Files:**
- Create: `fish-feast/src/game/enemy.ts`

- [ ] **Step 1: Write src/game/enemy.ts**

```typescript
import type { Fish } from '../types';
import { FLEE_SPEED, CHASE_SPEED, DETECT_BASE_RANGE, DETECT_RANGE_PER_DIFF, SIZE_FLEE_RATIO, SIZE_CHASE_RATIO } from '../constants';

export function updateEnemyBehavior(
  fishes: Fish[],
  player: Fish,
  dt: number,
  difficulty: number,
): void {
  if (!player.alive) return;

  const detectRange = DETECT_BASE_RANGE + difficulty * DETECT_RANGE_PER_DIFF;

  for (const f of fishes) {
    if (!f.alive || f.isPlayer) continue;

    f.behaviorTimer -= dt;
    if (f.behaviorTimer <= 0) {
      f.behaviorTimer = 1 + Math.random() * 2;

      const dx = f.x - player.x;
      const dy = f.y - player.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < detectRange) {
        if (f.size < player.size * SIZE_FLEE_RATIO) {
          f.behavior = 'flee';
        } else if (f.size > player.size * SIZE_CHASE_RATIO) {
          f.behavior = 'chase';
        } else {
          f.behavior = 'wander';
        }
      } else {
        f.behavior = 'wander';
      }
    }

    applyBehavior(f, player, dt);
  }
}

function applyBehavior(f: Fish, player: Fish, dt: number): void {
  if (f.behavior === 'flee') {
    const dx = f.x - player.x;
    const dy = f.y - player.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > 0) {
      f.x += (dx / dist) * FLEE_SPEED * 60 * dt;
      f.y += (dy / dist) * FLEE_SPEED * 60 * dt;
    }
    f.dir = dx > 0 ? 1 : -1;
  } else if (f.behavior === 'chase') {
    const dx = player.x - f.x;
    const dy = player.y - f.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > 0) {
      f.x += (dx / dist) * CHASE_SPEED * 60 * dt;
      f.y += (dy / dist) * CHASE_SPEED * 60 * dt;
    }
    f.dir = dx > 0 ? 1 : -1;
  }
}

export function updateFishMovement(
  fishes: Fish[],
  dt: number,
  canvasWidth: number,
): Fish[] {
  for (const f of fishes) {
    if (f.behavior === 'wander') {
      f.x += f.speed * f.dir * 60 * dt;
    }
    f.tailPhase += f.tailSpeed * dt;
    f.wobble += f.wobbleSpeed * dt;
  }
  return fishes.filter(f => {
    if (!f.alive) return false;
    if ((f.dir > 0 && f.x > canvasWidth + f.size * 3) || (f.dir < 0 && f.x < -f.size * 3)) {
      return false;
    }
    return true;
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/enemy.ts
git commit -m "refactor: extract enemy AI and movement module"
```

---

### Task 8: Create collision module

**Files:**
- Create: `fish-feast/src/game/collision.ts`

- [ ] **Step 1: Write src/game/collision.ts**

```typescript
import type { GameState } from '../types';
import { SIZE_EAT_THRESHOLD, GROWTH_RATIO, PARTICLE_EAT_COUNT, PARTICLE_LEVELUP_COUNT, PARTICLE_DEATH_COUNT, LEVEL_UP_DISPLAY_TIME } from '../constants';
import { createParticles } from './spawner';

export function processCollisions(state: GameState): boolean {
  let playerAlive = true;

  for (const f of state.fishes) {
    if (!f.alive) continue;

    const dx = f.x - state.player.x;
    const dy = f.y - state.player.y;
    const d = Math.sqrt(dx * dx + dy * dy);
    const threshold = state.player.size * 0.5 + f.size * 0.5;

    if (d < threshold) {
      if (state.player.size >= f.size * SIZE_EAT_THRESHOLD) {
        const growth = f.size * GROWTH_RATIO;
        state.player.size += growth;
        state.score += Math.floor(f.size * 10);
        createParticles(f.x, f.y, f.color, PARTICLE_EAT_COUNT, state.particles);
        f.alive = false;

        const newLevel = Math.floor(state.player.size / 10) + 1;
        if (newLevel > state.level) {
          state.level = newLevel;
          createParticles(state.player.x, state.player.y, '#4fc3f7', PARTICLE_LEVELUP_COUNT, state.particles);
          state.levelUpTimer = LEVEL_UP_DISPLAY_TIME;
        }
      } else if (f.size > state.player.size * SIZE_EAT_THRESHOLD) {
        createParticles(state.player.x, state.player.y, '#4fc3f7', PARTICLE_DEATH_COUNT, state.particles);
        state.player.alive = false;
        state.running = false;
        playerAlive = false;
      }
    }
  }

  return playerAlive;
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/collision.ts
git commit -m "refactor: extract collision detection and eating logic"
```

---

### Task 9: Create renderer module

**Files:**
- Create: `fish-feast/src/game/renderer.ts`

- [ ] **Step 1: Write src/game/renderer.ts**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/renderer.ts
git commit -m "refactor: extract canvas renderer module"
```

---

### Task 10: Create game engine module

**Files:**
- Create: `fish-feast/src/game/engine.ts`

- [ ] **Step 1: Write src/game/engine.ts**

```typescript
import type { GameState } from '../types';
import { getInput, consumePause } from './input';
import { getState } from './state';
import { updatePlayer } from './player';
import { updateEnemyBehavior, updateFishMovement } from './enemy';
import { processCollisions } from './collision';
import { spawnEnemyFish } from './spawner';
import { draw, getCanvasSize } from './renderer';
import { MAX_FISH_BASE } from '../constants';

let animFrameId = 0;

export function startGameLoop(onUpdate: () => void): void {
  const state = getState();

  function loop(timestamp: number): void {
    const dt = Math.min((timestamp - state.lastTime) / 1000, 0.05);
    state.lastTime = timestamp;

    update(dt);
    render();
    onUpdate();

    animFrameId = requestAnimationFrame(loop);
  }

  state.lastTime = performance.now();
  animFrameId = requestAnimationFrame(loop);
}

export function stopGameLoop(): void {
  cancelAnimationFrame(animFrameId);
}

function update(dt: number): void {
  const state = getState();

  // Handle pause toggle
  const pausePressed = consumePause();
  if (pausePressed) {
    togglePause();
  }

  if (!state.running || state.paused) return;

  state.gameTime += dt;
  state.difficulty = 1 + state.gameTime / 30;

  // Level-up display timer
  if (state.levelUpTimer > 0) {
    state.levelUpTimer -= dt;
  }

  const input = getInput();
  const { width, height } = getCanvasSize();

  updatePlayer(state.player, input, dt, width, height);
  updateEnemyBehavior(state.fishes, state.player, dt, state.difficulty);

  // Spawn enemies
  state.spawnTimer += dt;
  const spawnInterval = Math.max(0.5, 2 - state.difficulty * 0.15);
  if (state.spawnTimer > spawnInterval) {
    state.spawnTimer = 0;
    const maxFish = MAX_FISH_BASE + state.difficulty * 2;
    if (state.fishes.length < maxFish) {
      state.fishes.push(spawnEnemyFish(state.player.size, state.difficulty));
    }
  }

  // Update fish positions and remove off-screen
  state.fishes = updateFishMovement(state.fishes, dt, width);

  // Collisions
  processCollisions(state);

  // Update bubbles
  updateBubbles(dt, width, height);

  // Update particles
  updateParticles(dt);
}

function updateBubbles(dt: number, W: number, H: number): void {
  const state = getState();
  for (const b of state.bubbles) {
    b.y -= b.speed * 60 * dt;
    b.x += Math.sin(state.gameTime + b.y * 0.01) * 0.3;
    if (b.y < -10) {
      b.y = H + 10;
      b.x = Math.random() * W;
    }
  }
}

function updateParticles(dt: number): void {
  const state = getState();
  for (const p of state.particles) {
    p.x += p.vx * 60 * dt;
    p.y += p.vy * 60 * dt;
    p.life -= p.decay;
  }
  state.particles = state.particles.filter(p => p.life > 0);
}

function togglePause(): void {
  const state = getState();
  if (!state.running) return;
  state.paused = !state.paused;
}

function render(): void {
  const state = getState();
  draw(
    state.fishes,
    state.player,
    state.particles,
    state.bubbles,
    state.gameTime,
    state.running,
  );
}

export function startGame(): void {
  const state = getState();
  state.running = true;
  state.paused = false;
}

export function stopGame(): void {
  const state = getState();
  state.running = false;
  state.paused = false;
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/game/engine.ts
git commit -m "refactor: extract game engine main loop"
```

---

### Task 11: Create UI modules

**Files:**
- Create: `fish-feast/src/ui/hud.ts`
- Create: `fish-feast/src/ui/overlay.ts`
- Create: `fish-feast/src/ui/effects.ts`

- [ ] **Step 1: Write src/ui/hud.ts**

```typescript
function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

export function updateHUD(score: number, level: number, playerSize: number): void {
  el('score').textContent = `分数: ${score}`;
  el('level').textContent = `等级: ${level}`;

  const currentThreshold = (level - 1) * 10;
  const nextThreshold = level * 10;
  const progress = Math.min((playerSize - currentThreshold) / (nextThreshold - currentThreshold), 1) * 100;
  el('xpBar').style.width = `${Math.max(0, progress)}%`;
}
```

- [ ] **Step 2: Write src/ui/overlay.ts**

```typescript
function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

const overlayEl = () => el('overlay');
const deathInfoEl = () => el('deathInfo');
const restartBtn = () => el('restartBtn');
const instructionsEl = () => el('instructions');

export function setupOverlayCallbacks(onStart: () => void): void {
  el('startBtn').addEventListener('click', onStart);
  el('restartBtn').addEventListener('click', onStart);
}

export function showStartScreen(): void {
  overlayEl().classList.remove('hidden');
  overlayEl().querySelector('h1')!.textContent = '🐟 大鱼吃小鱼';
  overlayEl().querySelector('p')!.textContent = 'WASD / 方向键控制你的鱼，吃掉比你小的鱼，躲避比你大的鱼！';
  deathInfoEl().style.display = 'none';
}

export function showDeathScreen(score: number, level: number, highScore: number): void {
  overlayEl().classList.remove('hidden');
  overlayEl().querySelector('h1')!.textContent = '💀 被吃掉了！';
  overlayEl().querySelector('p')!.textContent = '你的鱼被更大的鱼吃掉了...';
  deathInfoEl().style.display = 'block';
  el('deathScore').textContent = `最终分数: ${score}`;
  el('deathLevel').textContent = `达到等级: ${level}`;
  el('highScore').textContent = `最高分: ${highScore}`;
}

export function hideOverlay(): void {
  overlayEl().classList.add('hidden');
  restartBtn().style.display = 'block';
  deathInfoEl().style.display = 'none';
  instructionsEl().style.opacity = '0.6';
  setTimeout(() => {
    instructionsEl().style.opacity = '0';
  }, 5000);
}

export function setPauseOverlay(visible: boolean): void {
  el('pauseOverlay').classList.toggle('active', visible);
}
```

- [ ] **Step 3: Write src/ui/effects.ts**

```typescript
function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

export function showLevelUpEffect(level: number): void {
  const levelUpEl = el('levelUpText');
  levelUpEl.textContent = `🎉 等级 ${level}!`;
  levelUpEl.classList.add('visible');
  el('flashOverlay').classList.add('active');
}

export function hideLevelUpEffect(): void {
  el('levelUpText').classList.remove('visible');
  el('flashOverlay').classList.remove('active');
}
```

- [ ] **Step 4: Commit**

```bash
git add fish-feast/src/ui/
git commit -m "refactor: extract UI modules (HUD, overlay, effects)"
```

---

### Task 12: Extract CSS to separate file

**Files:**
- Create: `fish-feast/src/styles/main.css`
- Modify: `fish-feast/index.html` (remove inline `<style>` block, add `<link>`)

- [ ] **Step 1: Write src/styles/main.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #0a1628; }
canvas { display: block; }
#ui {
  position: fixed; top: 0; left: 0; right: 0;
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px;
  background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 100%);
  pointer-events: none; z-index: 10;
  font-family: 'Segoe UI', sans-serif; color: #fff;
}
#ui > div { pointer-events: auto; }
#score { font-size: 20px; font-weight: bold; text-shadow: 0 0 10px rgba(0,200,255,0.5); }
#level { font-size: 14px; color: #88ccff; }
#xpBarContainer {
  width: 160px; height: 6px; background: rgba(255,255,255,0.1);
  border-radius: 3px; margin-top: 4px; overflow: hidden;
}
#xpBar {
  height: 100%; width: 0%; border-radius: 3px;
  background: linear-gradient(90deg, #4fc3f7, #ab47bc);
  transition: width 0.2s;
}
#restartBtn {
  padding: 8px 20px; border: 2px solid #4fc3f7; border-radius: 20px;
  background: rgba(79,195,247,0.15); color: #4fc3f7; font-size: 14px;
  cursor: pointer; transition: all 0.3s;
}
#restartBtn:hover { background: rgba(79,195,247,0.3); }
#overlay {
  position: fixed; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(10,22,40,0.9); z-index: 20;
  font-family: 'Segoe UI', sans-serif; color: #fff;
  transition: opacity 0.5s;
}
#overlay.hidden { opacity: 0; pointer-events: none; }
#overlay h1 { font-size: 48px; margin-bottom: 10px;
  background: linear-gradient(135deg, #4fc3f7, #ab47bc);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
#overlay p { font-size: 16px; color: #88ccff; margin-bottom: 30px; }
#startBtn {
  padding: 14px 48px; border: none; border-radius: 30px;
  background: linear-gradient(135deg, #4fc3f7, #29b6f6);
  color: #fff; font-size: 18px; font-weight: bold;
  cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 20px rgba(79,195,247,0.4);
}
#startBtn:hover { transform: scale(1.05); box-shadow: 0 6px 30px rgba(79,195,247,0.6); }
#deathScore { font-size: 28px; color: #ff7043; margin: 10px 0; }
#deathLevel { font-size: 16px; color: #88ccff; margin-bottom: 10px; }
#highScore { font-size: 14px; color: #66bb6a; margin-bottom: 20px; }
#instructions {
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  font-family: 'Segoe UI', sans-serif; color: rgba(255,255,255,0.4);
  font-size: 13px; z-index: 10; pointer-events: none;
  transition: opacity 2s;
}
#pauseOverlay {
  position: fixed; inset: 0; display: none; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(10,22,40,0.7); z-index: 15;
  font-family: 'Segoe UI', sans-serif; color: #fff;
}
#pauseOverlay.active { display: flex; }
#pauseOverlay h2 { font-size: 36px; margin-bottom: 10px; }
#pauseOverlay p { font-size: 16px; color: #88ccff; }
#levelUpText {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-family: 'Segoe UI', sans-serif; font-size: 48px; font-weight: bold;
  color: #4fc3f7; z-index: 12; pointer-events: none;
  text-shadow: 0 0 20px #4fc3f7, 0 0 40px #4fc3f7;
  opacity: 0; transition: opacity 0.3s, transform 0.3s;
}
#levelUpText.visible {
  opacity: 1; transform: translate(-50%, -50%) scale(1.1);
}
#flashOverlay {
  position: fixed; inset: 0; pointer-events: none; z-index: 11;
  background: radial-gradient(circle, rgba(79,195,247,0.3), transparent 70%);
  opacity: 0; transition: opacity 0.15s;
}
#flashOverlay.active { opacity: 1; }
```

- [ ] **Step 2: Strip inline `<style>` from index.html and replace with `<link>`**

Replace the entire `<style>...</style>` block in `<head>` with:

```html
<link rel="stylesheet" href="/src/styles/main.css">
```

- [ ] **Step 3: Remove the original `<script>` block from index.html**

Replace the `<script>...</script>` block with:

```html
<script type="module" src="/src/main.ts"></script>
```

- [ ] **Step 4: Commit**

```bash
git add fish-feast/
git commit -m "refactor: extract CSS and link module entry in index.html"
```

---

### Task 13: Create main entry point

**Files:**
- Create: `fish-feast/src/main.ts`

- [ ] **Step 1: Write src/main.ts**

```typescript
import { initRenderer, getCanvasSize } from './game/renderer';
import { initInput } from './game/input';
import { createState, getState, saveHighScore, resetState } from './game/state';
import { startGameLoop, startGame } from './game/engine';
import { updateHUD } from './ui/hud';
import { setupOverlayCallbacks, showStartScreen, showDeathScreen, hideOverlay, setPauseOverlay } from './ui/overlay';
import { showLevelUpEffect, hideLevelUpEffect } from './ui/effects';

// Initialize renderer
const canvas = document.getElementById('game') as HTMLCanvasElement;
initRenderer(canvas);

// Initialize input
initInput();

// Create initial state
const { width, height } = getCanvasSize();
createState(width, height);

// Setup UI callbacks
setupOverlayCallbacks(onStart);

// Show start screen
showStartScreen();

// Start game loop (renders without game running)
startGameLoop(onFrame);

function onStart(): void {
  const { width, height } = getCanvasSize();
  resetState(width, height);
  hideOverlay();
  startGame();
}

let prevLevelUpTimer = 0;

function onFrame(): void {
  const state = getState();

  // Update HUD
  updateHUD(state.score, state.level, state.player.size);

  // Handle level-up display
  if (state.levelUpTimer > 0 && prevLevelUpTimer <= 0) {
    showLevelUpEffect(state.level);
  } else if (state.levelUpTimer <= 0 && prevLevelUpTimer > 0) {
    hideLevelUpEffect();
  }
  prevLevelUpTimer = state.levelUpTimer;

  // Handle pause UI
  setPauseOverlay(state.paused);

  // Handle death
  if (!state.running && !state.player.alive) {
    saveHighScore(state.score);
    showDeathScreen(state.score, state.level, state.highScore);
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add fish-feast/src/main.ts
git commit -m "refactor: add main entry point wiring game + UI"
```

---

### Task 14: Build verification

- [ ] **Step 1: Install dependencies**

```bash
cd fish-feast
npm install
```

- [ ] **Step 2: Run TypeScript type check**

```bash
npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Run production build**

```bash
npx vite build
```

Expected: `dist/` directory produced with `index.html` and `assets/`.

- [ ] **Step 4: Verify build output is functional**

Check that `fish-feast/dist/index.html` exists and references `./assets/` with relative paths.

- [ ] **Step 5: Commit**

```bash
cd g:\vscode\projects\blog-site
git add fish-feast/
git commit -m "refactor: verify fish-feast TypeScript compilation and Vite build"
```

---

### Task 15: Final cleanup — remove old files

- [ ] **Step 1: Verify nothing references tmp-game anymore**

Run and confirm no results:
```bash
git grep "tmp-game" -- ":(exclude).git"
```

- [ ] **Step 2: Final commit if needed**

If any cleanup was needed:
```bash
git add -A
git commit -m "chore: cleanup tmp-game references"
```
