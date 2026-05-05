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
