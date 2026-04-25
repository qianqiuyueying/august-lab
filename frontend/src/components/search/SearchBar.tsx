import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/blog?search=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <motion.form onSubmit={handleSearch} className="flex gap-2">
      <div className="relative flex-1 sm:flex-none sm:w-72">
        <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
          <circle cx="11" cy="11" r="8" />
          <path strokeLinecap="round" d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索文章..."
          className="focus-ring w-full rounded-lg border border-border bg-paper/90 py-2.5 pl-9 pr-4 text-sm text-text-primary transition-all placeholder:text-text-muted focus:border-accent dark:border-border-dark dark:bg-surface-dark/90 dark:text-text-primary-dark"
        />
      </div>
      <motion.button
        type="submit"
        whileTap={{ scale: 0.96 }}
        className="lab-button min-h-0 px-5 py-2.5"
      >
        搜索
      </motion.button>
    </motion.form>
  );
}
