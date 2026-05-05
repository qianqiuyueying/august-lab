function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

const overlayEl = () => el('overlay');
const deathInfoEl = () => el('deathInfo');
const restartBtn = () => el('restartBtn');
const instructionsEl = () => el('instructions');

export function setupOverlayCallbacks(onStart: () => void): void {
  el('startBtn').addEventListener('click', onStart);
  el('restartBtn').addEventListener('click', onStart);
}

export function showStartScreen(): void {
  overlayEl().classList.remove('hidden');
  overlayEl().querySelector('h1')!.textContent = '🐟 大鱼吃小鱼';
  overlayEl().querySelector('p')!.textContent = 'WASD / 方向键控制你的鱼，吃掉比你小的鱼，躲避比你大的鱼！';
  deathInfoEl().style.display = 'none';
}

export function showDeathScreen(score: number, level: number, highScore: number): void {
  overlayEl().classList.remove('hidden');
  overlayEl().querySelector('h1')!.textContent = '💀 被吃掉了！';
  overlayEl().querySelector('p')!.textContent = '你的鱼被更大的鱼吃掉了...';
  deathInfoEl().style.display = 'block';
  el('deathScore').textContent = `最终分数: ${score}`;
  el('deathLevel').textContent = `达到等级: ${level}`;
  el('highScore').textContent = `最高分: ${highScore}`;
}

export function hideOverlay(): void {
  overlayEl().classList.add('hidden');
  restartBtn().style.display = 'block';
  deathInfoEl().style.display = 'none';
  instructionsEl().style.opacity = '0.6';
  setTimeout(() => {
    instructionsEl().style.opacity = '0';
  }, 5000);
}

export function setPauseOverlay(visible: boolean): void {
  el('pauseOverlay').classList.toggle('active', visible);
}
