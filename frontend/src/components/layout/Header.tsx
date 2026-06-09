import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import BrandMark from '../ui/BrandMark';

const navLinks = [
  { to: '/', label: '首页', number: '01' },
  { to: '/blog', label: '笔记', number: '02' },
  { to: '/products', label: '作品', number: '03' },
  { to: '/about', label: '关于', number: '04' },
];

function Icon({ name }: { name: 'menu' | 'close' }) {
  const paths = {
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
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <motion.header
      className="sticky top-0 z-40 border-b border-border bg-background/94 backdrop-blur-xl"
      initial={{ y: -72 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between gap-4">
          <Link to="/" className="focus-ring rounded-lg">
            <BrandMark />
          </Link>

          <nav className="hidden items-center gap-1 md:flex" aria-label="主导航">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`relative rounded-lg px-3.5 py-2 text-sm font-bold transition-all ${
                  isActive(link.to)
                    ? 'text-amber bg-amber-subtle'
                    : 'text-text-muted hover:text-paper hover:bg-accent-subtle-dark'
                }`}
              >
                <span className="font-mono text-[10px] mr-1.5 opacity-70">
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
              onClick={() => setMobileOpen((open) => !open)}
              whileTap={{ scale: 0.94 }}
              className="focus-ring rounded-lg border border-border bg-paper-soft p-2 text-text-muted transition-colors hover:text-paper md:hidden"
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
            className="overflow-hidden border-t border-border md:hidden"
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
                      ? 'bg-amber-subtle text-amber'
                      : 'text-text-muted hover:bg-paper-soft hover:text-paper'
                  }`}
                >
                  <span className="font-mono text-[10px] mr-1.5 opacity-70">
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
