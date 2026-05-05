function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

export function showLevelUpEffect(level: number): void {
  const levelUpEl = el('levelUpText');
  levelUpEl.textContent = `🎉 等级 ${level}!`;
  levelUpEl.classList.add('visible');
  el('flashOverlay').classList.add('active');
}

export function hideLevelUpEffect(): void {
  el('levelUpText').classList.remove('visible');
  el('flashOverlay').classList.remove('active');
}
