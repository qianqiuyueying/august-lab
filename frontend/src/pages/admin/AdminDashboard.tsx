import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getArticles } from '../../api/articles';
import { getPages } from '../../api/pages';

export default function AdminDashboard() {
  const [articleCount, setArticleCount] = useState(0);
  const [pageCount, setPageCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getArticles(1, 1).then((d: { total: number }) => { setArticleCount(d.total); }).catch(() => {}),
      getPages().then((d: { length: number }) => { setPageCount(d.length); }).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const stats = [
    { label: '文章', value: articleCount, to: '/admin/articles', color: 'from-indigo-500 to-blue-600' },
    { label: '页面', value: pageCount, to: '/admin/pages', color: 'from-emerald-500 to-teal-600' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">仪表盘</h1>
        <p className="text-zinc-500 dark:text-zinc-400 mt-1">欢迎回来，admin</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse h-32 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
          ))}
        </div>
      ) : (
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {stats.map((stat) => (
            <Link key={stat.label} to={stat.to}>
              <motion.div
                whileHover={{ y: -4, scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className={`bg-gradient-to-br ${stat.color} rounded-xl p-6 text-white shadow-lg cursor-pointer`}
              >
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm font-medium mt-1 opacity-80">{stat.label}</div>
              </motion.div>
            </Link>
          ))}
        </motion.div>
      )}

      {/* Quick actions */}
      <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">快捷操作</h2>
        <div className="flex flex-wrap gap-3">
          <Link to="/admin/articles">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-accent text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-accent-hover transition-colors"
            >
              上传文章
            </motion.button>
          </Link>
          <Link to="/admin/pages">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 px-4 py-2 rounded-lg font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              上传页面
            </motion.button>
          </Link>
          <Link to="/admin/settings">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 px-4 py-2 rounded-lg font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              编辑简介
            </motion.button>
          </Link>
        </div>
      </div>
    </div>
  );
}
