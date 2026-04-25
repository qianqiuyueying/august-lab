import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { getDashboardStats } from '../../api/dashboard';
import type { DashboardStats } from '../../api/dashboard';

const BAR_COLORS = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#0ea5e9', '#6366f1', '#8b5cf6', '#a78bfa', '#14b8a6', '#f59e0b'];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats().then(setStats).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-2xl font-bold text-zinc-900 dark:text-white">仪表盘</div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse h-28 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    { label: '文章', value: stats.article_count, sub: `${stats.published_count} 已发布 · ${stats.draft_count} 草稿`, to: '/admin/articles', color: 'from-indigo-500 to-blue-600' },
    { label: '产品', value: stats.product_count, sub: '主题 & 模板', to: '/admin/products', color: 'from-purple-500 to-pink-600' },
    { label: '页面', value: stats.page_count, sub: '静态页面', to: '/admin/pages', color: 'from-emerald-500 to-teal-600' },
    { label: '标签', value: stats.tag_count, sub: '分类标签', to: '/admin/articles', color: 'from-amber-500 to-orange-600' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">仪表盘</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">站点概览与快捷操作</p>
      </div>

      {/* 统计卡片 */}
      <motion.div
        className="grid grid-cols-2 sm:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {statCards.map((stat) => (
          <Link key={stat.label} to={stat.to}>
            <motion.div
              whileHover={{ y: -4, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`bg-gradient-to-br ${stat.color} rounded-xl p-5 text-white shadow-lg cursor-pointer`}
            >
              <div className="text-3xl font-bold">{stat.value}</div>
              <div className="text-sm font-medium mt-1 opacity-90">{stat.label}</div>
              <div className="text-xs mt-0.5 opacity-60">{stat.sub}</div>
            </motion.div>
          </Link>
        ))}
      </motion.div>

      {/* 两列：标签分布 + 近期文章 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 标签分布 */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">标签分布</h2>
          {stats.tag_distribution.length === 0 ? (
            <p className="text-zinc-400 text-sm py-8 text-center">暂无标签数据</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={stats.tag_distribution}>
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: 'currentColor' }} stroke="transparent" />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid rgba(0,0,0,0.08)',
                    fontSize: '13px',
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {stats.tag_distribution.map((_, i) => (
                    <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </motion.div>

        {/* 近期文章 */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">近期文章</h2>
            <Link to="/admin/articles" className="text-xs text-accent hover:text-accent-hover font-medium">查看全部</Link>
          </div>
          {stats.recent_articles.length === 0 ? (
            <p className="text-zinc-400 text-sm py-8 text-center">暂无文章</p>
          ) : (
            <div className="space-y-3">
              {stats.recent_articles.map((a) => (
                <div key={a.id} className="flex items-start justify-between border-b border-zinc-100 dark:border-zinc-800 pb-3 last:border-b-0 last:pb-0">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-zinc-900 dark:text-white truncate">{a.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${a.status === 'published' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'}`}>
                        {a.status === 'published' ? '已发布' : '草稿'}
                      </span>
                      <span className="text-xs text-zinc-400">{formatDate(a.created_at)}</span>
                    </div>
                    {a.tags.length > 0 && (
                      <div className="flex gap-1 mt-1.5 flex-wrap">
                        {a.tags.map((t) => (
                          <span key={t.id} className="text-xs px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">{t.name}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* 系统状态 */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">系统状态</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex items-center gap-3 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800/50">
            <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-900 dark:text-white">数据库</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">{stats.database_size != null ? formatBytes(stats.database_size) : '—'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800/50">
            <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-900 dark:text-white">用户数</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">{stats.user_count}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800/50">
            <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-900 dark:text-white">API 状态</p>
              <p className="text-xs text-green-600 dark:text-green-400">运行中</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 快捷操作 */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
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
          <Link to="/admin/products">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 px-4 py-2 rounded-lg font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              创建产品
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
      </motion.div>
    </div>
  );
}
