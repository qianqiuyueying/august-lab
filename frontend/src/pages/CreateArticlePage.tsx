import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticleMutations } from '../hooks/useArticles';
import ArticleEditor from '../components/articles/ArticleEditor';

export default function CreateArticlePage() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [summary, setSummary] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { createArticle } = useArticleMutations();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !content) return;
    setLoading(true);
    setError('');
    try {
      const tags = tagsInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
      const article = await createArticle({ title, content, summary, status, tags });
      navigate(`/articles/${article.slug}`);
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <h1 className="text-2xl font-bold mb-6 text-zinc-900 dark:text-white">创建文章</h1>

      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg mb-4"
        >
          {error}
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
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
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">摘要</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows={2}
            className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">标签 (逗号分隔)</label>
          <input
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="React, FastAPI, TypeScript"
            className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
          />
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
        <div className="flex gap-2">
          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors"
          >
            {loading ? '创建中...' : '创建'}
          </motion.button>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
          >
            取消
          </button>
        </div>
      </form>
    </motion.div>
  );
}
