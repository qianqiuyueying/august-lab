import '@testing-library/jest-dom';
import { beforeEach } from 'vitest';

// Mock window.matchMedia（Vitest/jsdom 环境不提供）
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// Disable framer-motion animations in tests
beforeEach(() => {
  const root = document.createElement('div');
  root.id = 'motion-config-root';
  document.body.appendChild(root);
});
