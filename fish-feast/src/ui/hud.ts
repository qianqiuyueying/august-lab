function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

export function updateHUD(score: number, level: number, playerSize: number): void {
  el('score').textContent = `分数: ${score}`;
  el('level').textContent = `等级: ${level}`;

  const currentThreshold = (level - 1) * 10;
  const nextThreshold = level * 10;
  const progress = Math.min((playerSize - currentThreshold) / (nextThreshold - currentThreshold), 1) * 100;
  el('xpBar').style.width = `${Math.max(0, progress)}%`;
}
