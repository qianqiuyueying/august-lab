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

  const pausePressed = consumePause();
  if (pausePressed) {
    togglePause();
  }

  if (!state.running || state.paused) return;

  state.gameTime += dt;
  state.difficulty = 1 + state.gameTime / 30;

  if (state.levelUpTimer > 0) {
    state.levelUpTimer -= dt;
  }

  const input = getInput();
  const { width, height } = getCanvasSize();

  updatePlayer(state.player, input, dt, width, height);
  updateEnemyBehavior(state.fishes, state.player, dt, state.difficulty);

  state.spawnTimer += dt;
  const spawnInterval = Math.max(0.5, 2 - state.difficulty * 0.15);
  if (state.spawnTimer > spawnInterval) {
    state.spawnTimer = 0;
    const maxFish = MAX_FISH_BASE + state.difficulty * 2;
    if (state.fishes.length < maxFish) {
      state.fishes.push(spawnEnemyFish(state.player.size, state.difficulty));
    }
  }

  state.fishes = updateFishMovement(state.fishes, dt, width);

  processCollisions(state);

  updateBubbles(dt, width, height);
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
