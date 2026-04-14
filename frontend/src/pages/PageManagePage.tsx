import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getPages, createPage, deletePage } from '../api/pages';
import type { Page } from '../types';
import ArticleEditor from '../components/articles/ArticleEditor';
import { useAuth } from '../contexts/AuthContext';

export default function PageManagePage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadPages();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const loadPages = async () => {
    try {
      const data = await getPages();
      setPages(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !slug || !content) return;
    setLoading(true);
    setError('');
    try {
      await createPage({ slug, title, content, status });
      setTitle('');
      setSlug('');
      setContent('');
      setStatus('draft');
      await loadPages();
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此页面吗？')) return;
    try {
      await deletePage(id);
      await loadPages();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <h1 className="text-2xl font-bold mb-6 text-zinc-900 dark:text-white">静态页面管理</h1>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg mb-4"
        >
          {error}
        </motion.div>
      )}

      <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 mb-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">创建新页面</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">标题</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Slug</label>
              <input
                type="text"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                required
                placeholder="about"
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">状态</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
            >
              <option value="draft">草稿</option>
              <option value="published">发布</option>
            </select>
          </div>
          <ArticleEditor initialContent={content} onChange={setContent} />
          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors"
          >
            {loading ? '创建中...' : '创建页面'}
          </motion.button>
        </form>
      </div>

      <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">已有页面</h2>
        {pages.length === 0 ? (
          <div className="text-zinc-500">暂无页面</div>
        ) : (
          <div className="space-y-3">
            {pages.map((p) => (
              <div key={p.id} className="flex justify-between items-center border-b border-zinc-200 dark:border-zinc-800 pb-3">
                <div>
                  <span className="font-medium text-zinc-900 dark:text-white">{p.title}</span>
                  <span className="ml-2 text-sm text-zinc-500">/{p.slug}</span>
                  <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${p.status === 'published' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'}`}>
                    {p.status === 'published' ? '已发布' : '草稿'}
                  </span>
                </div>
                <motion.button
                  onClick={() => handleDelete(p.id)}
                  whileTap={{ scale: 0.95 }}
                  className="text-red-600 hover:text-red-500 text-sm font-medium"
                >
                  删除
                </motion.button>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
