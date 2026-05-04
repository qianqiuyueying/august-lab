import '@testing-library/jest-dom';
import { beforeEach } from 'vitest';

// Mock localStorage（jsdom v29 不默认提供）
const localStorageMock = {
  getItem: (_key: string) => null,
  setItem: (_key: string, _value: string) => {},
  removeItem: (_key: string) => {},
  clear: () => {},
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

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
