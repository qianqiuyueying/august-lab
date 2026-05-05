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
