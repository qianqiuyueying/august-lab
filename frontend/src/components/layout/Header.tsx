import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { useTheme } from '../../hooks/useTheme';
import BrandMark from '../ui/BrandMark';

const navLinks = [
  { to: '/', label: '首页', number: '01' },
  { to: '/blog', label: '笔记', number: '02' },
  { to: '/products', label: '作品', number: '03' },
  { to: '/about', label: '关于', number: '04' },
];

function Icon({ name }: { name: 'sun' | 'moon' | 'menu' | 'close' }) {
  const paths = {
    sun: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
      </>
    ),
    moon: <path d="M20 14.4A7.5 7.5 0 019.6 4a8.5 8.5 0 1010.4 10.4Z" />,
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    close: <path d="M6 6l12 12M18 6L6 18" />,
  };

  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  );
}

export default function Header() {
  const { theme, toggle } = useTheme();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <motion.header
      className="sticky top-0 z-40 border-b border-border/80 bg-background/86 backdrop-blur-xl dark:border-border-dark/80 dark:bg-background-dark/86"
      initial={{ y: -72 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          <Link to="/" className="focus-ring rounded-lg">
            <BrandMark />
          </Link>

          <nav className="hidden items-center gap-1 md:flex" aria-label="主导航">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`relative rounded-lg px-3.5 py-2 text-sm font-bold transition-colors ${
                  isActive(link.to)
                    ? 'text-text-primary dark:text-text-primary-dark'
                    : 'text-text-muted hover:text-text-primary dark:text-text-muted-dark dark:hover:text-text-primary-dark'
                }`}
              >
                <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
                  {link.number}
                </span>
                {link.label}
                {isActive(link.to) && (
                  <motion.span
                    layoutId="nav-marker"
                    className="absolute inset-x-3 bottom-1 h-0.5 rounded-full bg-accent"
                    transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                  />
                )}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <motion.button
              type="button"
              onClick={toggle}
              whileTap={{ scale: 0.94 }}
              className="focus-ring rounded-lg border border-border bg-paper/72 p-2 text-text-muted transition-colors hover:text-text-primary dark:border-border-dark dark:bg-surface-dark/72 dark:text-text-muted-dark dark:hover:text-text-primary-dark"
              aria-label="切换明暗模式"
            >
              {theme === 'light' ? <Icon name="moon" /> : <Icon name="sun" />}
            </motion.button>
            <motion.button
              type="button"
              onClick={() => setMobileOpen((open) => !open)}
              whileTap={{ scale: 0.94 }}
              className="focus-ring rounded-lg border border-border bg-paper/72 p-2 text-text-muted transition-colors hover:text-text-primary dark:border-border-dark dark:bg-surface-dark/72 dark:text-text-muted-dark dark:hover:text-text-primary-dark md:hidden"
              aria-label="打开菜单"
            >
              {mobileOpen ? <Icon name="close" /> : <Icon name="menu" />}
            </motion.button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.nav
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden border-t border-border/80 dark:border-border-dark/80 md:hidden"
            aria-label="移动端导航"
          >
            <div className="mx-auto max-w-7xl space-y-1 px-4 py-4">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileOpen(false)}
                  className={`block rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
                    isActive(link.to)
                      ? 'bg-accent-subtle text-accent-hover dark:bg-accent-subtle-dark dark:text-text-primary-dark'
                      : 'text-text-muted hover:bg-paper dark:text-text-muted-dark dark:hover:bg-surface-dark'
                  }`}
                >
                  <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
                    {link.number}
                  </span>
                  {link.label}
                </Link>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
