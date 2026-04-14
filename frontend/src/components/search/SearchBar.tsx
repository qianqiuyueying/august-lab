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
      <motion.input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索文章..."
        whileFocus={{ scale: 1.01 }}
        className="flex-1 sm:flex-none sm:w-64 border border-zinc-300 dark:border-zinc-700 rounded-lg px-4 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
      />
      <motion.button
        type="submit"
        whileTap={{ scale: 0.96 }}
        className="px-4 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-hover transition-colors"
      >
        搜索
      </motion.button>
    </motion.form>
  );
}
