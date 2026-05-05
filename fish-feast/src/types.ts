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
