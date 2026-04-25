import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/?search=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <motion.form onSubmit={handleSearch} className="flex gap-2">
      <div className="relative flex-1 sm:flex-none sm:w-72">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <circle cx="11" cy="11" r="8" />
          <path strokeLinecap="round" d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索文章..."
          className="w-full border border-zinc-200 dark:border-zinc-800 rounded-lg pl-9 pr-4 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-accent-start/30 focus:border-accent-start transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
        />
      </div>
      <motion.button
        type="submit"
        whileTap={{ scale: 0.96 }}
        className="px-5 py-2 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium hover:bg-zinc-800 dark:hover:bg-zinc-100 transition-colors"
      >
        搜索
      </motion.button>
    </motion.form>
  );
}
