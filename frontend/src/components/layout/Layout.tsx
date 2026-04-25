import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Header from './Header';
import ScrollProgress from './ScrollProgress';
import { Link } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col relative">
      {/* Subtle noise texture overlay */}
      <div className="bg-noise" />

      <ScrollProgress />
      <Header />
      <main className="flex-1 w-full relative">
        {/* Hero glow gradient behind content area */}
        <div className="absolute inset-x-0 top-0 h-[600px] hero-glow pointer-events-none" />

        <AnimatePresence mode="popLayout">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 relative z-10"
            style={{ originX: 0.5, originY: 0 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-border dark:border-border-dark bg-surface/60 dark:bg-surface-dark/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            {/* Brand */}
            <div className="md:col-span-2">
              <p className="text-lg font-bold text-gradient mb-2">August's Lab</p>
              <p className="text-sm text-text-secondary dark:text-text-secondary-dark max-w-sm">
                技术探索与创造的交汇点。分享技术思考，记录产品旅程。
              </p>
            </div>

            {/* Navigation */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted dark:text-text-muted-dark mb-3">导航</h3>
              <div className="space-y-2">
                {[
                  { to: '/', label: '首页' },
                  { to: '/blog', label: '博客' },
                  { to: '/products', label: '产品' },
                  { to: '/about', label: '关于' },
                ].map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    className="block text-sm text-text-secondary dark:text-text-secondary-dark hover:text-text-primary dark:hover:text-text-primary-dark transition-colors"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>

            {/* Tech */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted dark:text-text-muted-dark mb-3">技术栈</h3>
              <div className="space-y-2 text-sm text-text-secondary dark:text-text-secondary-dark">
                <p>FastAPI + React</p>
                <p>TypeScript + Tailwind</p>
                <p>SQLite + Docker</p>
              </div>
            </div>
          </div>

          <div className="border-t border-border/50 dark:border-border-dark/50 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-text-muted dark:text-text-muted-dark">
              &copy; {new Date().getFullYear()} August's Lab. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-muted dark:text-text-muted-dark hover:text-text-primary dark:hover:text-text-primary-dark transition-colors"
                aria-label="GitHub"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 1.746.566C10.16 9.21 11.135 9 12 9c.865 0 1.84.21 2.264.651.906-.836 1.746-.566 1.746-.566.544 1.378.202 2.396.1 2.65.64.7 1.03 1.595 1.03 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
              </a>
              <a
                href="mailto:hello@example.com"
                className="text-text-muted dark:text-text-muted-dark hover:text-text-primary dark:hover:text-text-primary-dark transition-colors"
                aria-label="Email"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
