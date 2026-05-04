import { Outlet, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Header from './Header';
import ScrollProgress from './ScrollProgress';
import BrandMark from '../ui/BrandMark';
import ParticleBackground from '../ui/ParticleBackground';

const footerLinks = [
  { to: '/', label: '首页', number: '01' },
  { to: '/blog', label: '笔记', number: '02' },
  { to: '/products', label: '作品', number: '03' },
  { to: '/about', label: '关于', number: '04' },
];

export default function Layout() {
  const location = useLocation();
  const isProductRuntimePage = /^\/products\/[^/]+$/.test(location.pathname);

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <ParticleBackground />
      <div className="site-texture" />
      <ScrollProgress />
      <Header />

      <main className="relative z-10 w-full flex-1">
        {!isProductRuntimePage && <div className="pointer-events-none absolute inset-x-0 top-0 h-[34rem] hero-glow" />}
        <AnimatePresence mode="popLayout">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
            className={
              isProductRuntimePage
                ? 'relative z-10'
                : 'relative z-10 px-4 py-10 sm:px-6 sm:py-14 lg:px-8'
            }
            style={{ originX: 0.5, originY: 0 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      {!isProductRuntimePage && <footer className="relative z-10 border-t border-border bg-paper/72 backdrop-blur-xl dark:border-border-dark dark:bg-surface-dark/72">
        <div className="mx-auto max-w-7xl grid gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_1fr] lg:px-8">
          <div>
            <BrandMark />
            <p className="mt-4 text-sm text-text-muted dark:text-text-muted-dark max-w-sm">
              写下实验、系统和那些慢慢成形的想法。
            </p>
          </div>

          <div>
            <h2 className="section-label mb-4">Navigation</h2>
            <div className="grid gap-2">
              {footerLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-sm font-semibold text-text-secondary transition-colors hover:text-accent dark:text-text-secondary-dark dark:hover:text-text-primary-dark"
                >
                  <span className="font-mono text-[10px] mr-1.5 text-text-muted dark:text-text-muted-dark">
                    {link.number}
                  </span>
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-border/70 dark:border-border-dark/70">
          <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-5 text-sm text-text-muted dark:text-text-muted-dark sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
            <p>&copy; {new Date().getFullYear()} August&apos;s Lab. Built with curiosity and caffeine.</p>
            <div className="flex gap-4">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="font-semibold hover:text-accent">
                GitHub
              </a>
              <a href="mailto:hello@example.com" className="font-semibold hover:text-accent">
                Email
              </a>
            </div>
          </div>
        </div>
      </footer>}
    </div>
  );
}
