import { Outlet, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Header from './Header';
import ScrollProgress from './ScrollProgress';
import BrandMark from '../ui/BrandMark';

const footerLinks = [
  { to: '/', label: '首页' },
  { to: '/blog', label: '实验笔记' },
  { to: '/products', label: '作品记录' },
  { to: '/about', label: '关于 August' },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <div className="site-texture" />
      <ScrollProgress />
      <Header />

      <main className="relative z-10 w-full flex-1">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[34rem] hero-glow" />
        <AnimatePresence mode="popLayout">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-10 mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8"
            style={{ originX: 0.5, originY: 0 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      <footer className="relative z-10 border-t border-border bg-paper/72 backdrop-blur-xl dark:border-border-dark dark:bg-surface-dark/72">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.5fr_1fr_1fr] lg:px-8">
          <div>
            <BrandMark />
            <p className="mt-5 max-w-md text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
              这里记录技术探索、产品实验和长期思考。页面尽量安静，把注意力留给文章本身，也留给那些正在打磨的小作品。
            </p>
          </div>

          <div>
            <h2 className="section-label mb-4">Navigation</h2>
            <div className="grid gap-2">
              {footerLinks.map((link) => (
                <Link key={link.to} to={link.to} className="text-sm font-semibold text-text-secondary transition-colors hover:text-accent dark:text-text-secondary-dark dark:hover:text-text-primary-dark">
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          <div>
            <h2 className="section-label mb-4">Stack</h2>
            <div className="flex flex-wrap gap-2">
              {['FastAPI', 'React', 'TypeScript', 'Tailwind', 'SQLite'].map((item) => (
                <span key={item} className="lab-chip">{item}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-border/70 dark:border-border-dark/70">
          <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-5 text-sm text-text-muted dark:text-text-muted-dark sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
            <p>&copy; {new Date().getFullYear()} August&apos;s Lab. Built as a living notebook.</p>
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
      </footer>
    </div>
  );
}
