import { initRenderer, getCanvasSize } from './game/renderer';
import { initInput } from './game/input';
import { createState, getState, saveHighScore, resetState } from './game/state';
import { startGameLoop, startGame } from './game/engine';
import { updateHUD } from './ui/hud';
import { setupOverlayCallbacks, showStartScreen, showDeathScreen, hideOverlay, setPauseOverlay } from './ui/overlay';
import { showLevelUpEffect, hideLevelUpEffect } from './ui/effects';

const canvas = document.getElementById('game') as HTMLCanvasElement;
initRenderer(canvas);

initInput();

const { width, height } = getCanvasSize();
createState(width, height);

setupOverlayCallbacks(onStart);

showStartScreen();

let prevLevelUpTimer = 0;

startGameLoop(onFrame);

function onStart(): void {
  const { width, height } = getCanvasSize();
  resetState(width, height);
  hideOverlay();
  startGame();
}

function onFrame(): void {
  const state = getState();

  updateHUD(state.score, state.level, state.player.size);

  if (state.levelUpTimer > 0 && prevLevelUpTimer <= 0) {
    showLevelUpEffect(state.level);
  } else if (state.levelUpTimer <= 0 && prevLevelUpTimer > 0) {
    hideLevelUpEffect();
  }
  prevLevelUpTimer = state.levelUpTimer;

  setPauseOverlay(state.paused);

  if (!state.running && !state.player.alive) {
    saveHighScore(state.score);
    showDeathScreen(state.score, state.level, state.highScore);
  }
}
