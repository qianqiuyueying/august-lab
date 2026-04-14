import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Header from './Header';
import ScrollProgress from './ScrollProgress';

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col bg-background dark:bg-background-dark">
      <ScrollProgress />
      <Header />
      <main className="flex-1 w-full relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35, ease: [0.25, 0.1, 0.25, 1] }}
            className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
      <footer className="border-t border-zinc-200/60 dark:border-zinc-800/60 bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-zinc-400 dark:text-zinc-500 text-sm">
            &copy; {new Date().getFullYear()} August's Lab. Built with FastAPI & React.
          </p>
        </div>
      </footer>
    </div>
  );
}
