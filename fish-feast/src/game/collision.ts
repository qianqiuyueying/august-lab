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
