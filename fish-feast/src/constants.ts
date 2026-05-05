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

export const SIZE_EAT_THRESHOLD = 1.05;
export const SIZE_FLEE_RATIO = 0.8;
export const SIZE_CHASE_RATIO = 1.35;
export const GROWTH_RATIO = 0.18;
export const DETECT_BASE_RANGE = 200;
export const DETECT_RANGE_PER_DIFF = 20;

export const PARTICLE_EAT_COUNT = 12;
export const PARTICLE_LEVELUP_COUNT = 20;
export const PARTICLE_DEATH_COUNT = 30;

export const LEVEL_UP_DISPLAY_TIME = 1.5;

export const LS_HIGH_SCORE_KEY = 'fishGameHighScore';
