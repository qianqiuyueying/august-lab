import type { Fish, InputState } from '../types';
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
