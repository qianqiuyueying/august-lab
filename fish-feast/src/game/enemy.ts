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
