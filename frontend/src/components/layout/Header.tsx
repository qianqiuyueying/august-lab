import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '../../hooks/useTheme';

const navLinks = [
  { to: '/', label: '首页' },
  { to: '/blog', label: '博客' },
  { to: '/products', label: '产品' },
  { to: '/about', label: '关于' },
];

function SunIcon() {
  return (
    <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <circle cx="12" cy="12" r="5" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

export default function Header() {
  const { theme, toggle } = useTheme();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <motion.header
        className="sticky top-0 z-50 backdrop-blur-xl bg-surface/80 dark:bg-surface-dark/80 border-b border-border/60 dark:border-border-dark/60"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2.5">
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                <rect x="2" y="2" width="20" height="20" rx="5" className="fill-zinc-900 dark:fill-white" />
                <path d="M7 17V7h2l3 8 3-8h2v10h-1.5V9l-2.5 8h-1L8.5 9v8H7z" className="fill-white dark:fill-zinc-900" />
              </svg>
              <motion.span
                className="text-[15px] font-bold tracking-tight text-zinc-900 dark:text-white"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                August&apos;s Lab
              </motion.span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-1">
              <div className="relative flex items-center">
                {navLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    className="relative px-3.5 py-1.5 text-[14px] font-medium text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
                  >
                    {link.label}
                    {isActive(link.to) && (
                      <motion.div
                        layoutId="nav-underline"
                        className="absolute bottom-0 left-1 right-1 h-0.5 bg-gradient-to-r from-accent-start via-accent-mid to-accent-end rounded-full"
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                  </Link>
                ))}
              </div>
            </nav>

            {/* Right side */}
            <div className="flex items-center gap-1">
              {/* Theme toggle */}
              <motion.button
                onClick={toggle}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-lg text-zinc-400 hover:text-zinc-900 dark:text-zinc-500 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                aria-label="切换亮暗模式"
              >
                {theme === 'light' ? <MoonIcon /> : <SunIcon />}
              </motion.button>

              {/* Mobile menu button */}
              <motion.button
                onClick={() => setMobileOpen(!mobileOpen)}
                whileTap={{ scale: 0.9 }}
                className="md:hidden p-2 rounded-lg text-zinc-400 hover:text-zinc-900 dark:text-zinc-500 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                aria-label="菜单"
              >
                {mobileOpen ? <CloseIcon /> : <MenuIcon />}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="md:hidden overflow-hidden border-t border-border/60 dark:border-border-dark/60"
            >
              <nav className="px-4 pb-4 pt-3 space-y-0.5">
                {navLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileOpen(false)}
                    className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive(link.to)
                        ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white'
                        : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-white'
                    }`}
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>
    </>
  );
}
