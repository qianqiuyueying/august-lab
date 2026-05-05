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
