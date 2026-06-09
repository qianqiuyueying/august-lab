import { useEffect } from 'react';

/**
 * Always dark mode — matching the "AugLab 2.0" preview design.
 * Keeps the API shape for backward compatibility.
 */
export function useTheme() {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.add('dark');
  }, []);

  const toggle = () => {
    // No-op: theme is always dark per the preview design
  };

  return { theme: 'dark' as const, toggle };
}
