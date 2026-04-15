import { useState, useEffect, type FormEvent, useRef } from 'react';
import { motion } from 'framer-motion';
import { getArticles, getArticle, uploadMd, createArticle, updateArticle, deleteArticle } from '../../api/articles';
import type { ArticleListItem } from '../../types';
import ArticleEditor from '../../components/articles/ArticleEditor';

export default function AdminArticles() {
  const [articles, setArticles] = useState<ArticleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [summary, setSummary] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [status, setStatus] = useState('draft');

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      const data = await getArticles(1, 50);
      setArticles(data.items);
    } catch {
      setError('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setContent('');
    setSummary('');
    setTagsInput('');
    setStatus('draft');
    setEditingId(null);
    setShowForm(false);
  };

  const startEdit = async (article: ArticleListItem) => {
    const full = await getArticle(article.slug);
    setTitle(full.title);
    setContent(full.content);
    setSummary(full.summary);
    setTagsInput(full.tags.map((t) => t.name).join(', '));
    setStatus(full.status);
    setEditingId(full.id);
    setShowForm(true);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const parsed = await uploadMd(file);
      setTitle(parsed.title);
      setContent(parsed.content);
      setShowForm(true);
    } catch {
      setError('解析 Markdown 文件失败');
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !content) return;
    setLoading(true);
    setError('');
    try {
      const tags = tagsInput.split(',').map((t) => t.trim()).filter(Boolean);
      if (editingId) {
        await updateArticle(editingId, { title, content, summary, status, tags });
      } else {
        await createArticle({ title, content, summary, status, tags });
      }
      resetForm();
      await loadArticles();
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此文章吗？')) return;
    try {
      await deleteArticle(id);
      await loadArticles();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">文章管理</h1>
      </div>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-sm">
          {error}
        </motion.div>
      )}

      {/* Upload area */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">上传 Markdown 文件</h2>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => { resetForm(); setShowForm(true); }}
            className="text-sm text-accent hover:text-accent-hover transition-colors"
          >
            手动创建
          </motion.button>
        </div>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1 mb-4">
          上传 .md 文件后自动解析标题和内容，可在编辑器中微调后发布
        </p>
        <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-lg cursor-pointer hover:border-accent hover:bg-accent/5 transition-colors">
          <span className="text-sm text-zinc-500 dark:text-zinc-400">
            点击选择或拖拽 .md 文件
          </span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".md"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </motion.div>

      {/* Editor form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">
            {editingId ? '编辑文章' : '创建文章'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                <input
                  type="text"
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">标签 (逗号分隔)</label>
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                  placeholder="React, FastAPI"
                  className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">状态</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
                >
                  <option value="draft">草稿</option>
                  <option value="published">发布</option>
                </select>
              </div>
            </div>
            <ArticleEditor initialContent={content} onChange={setContent} />
            <div className="flex gap-2">
              <motion.button
                type="submit"
                disabled={loading}
                whileTap={{ scale: loading ? 1 : 0.98 }}
                className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
              >
                {loading ? '保存中...' : editingId ? '保存修改' : '发布'}
              </motion.button>
              <button
                type="button"
                onClick={resetForm}
                className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors text-sm"
              >
                取消
              </button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Article list */}
      <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">已有文章</h2>
        {loading ? (
          <div className="text-zinc-500">加载中...</div>
        ) : articles.length === 0 ? (
          <div className="text-zinc-500">暂无文章</div>
        ) : (
          <div className="space-y-3">
            {articles.map((a) => (
              <div key={a.id} className="flex justify-between items-center border-b border-zinc-200 dark:border-zinc-800 pb-3 last:border-b-0">
                <div className="flex-1">
                  <span className="font-medium text-zinc-900 dark:text-white">{a.title}</span>
                  <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${a.status === 'published' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'}`}>
                    {a.status === 'published' ? '已发布' : '草稿'}
                  </span>
                  {a.tags.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {a.tags.map((t) => (
                        <span key={t.id} className="text-xs px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">{t.name}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => startEdit(a)}
                    className="text-accent hover:text-accent-hover text-sm font-medium"
                  >
                    编辑
                  </button>
                  <motion.button
                    onClick={() => handleDelete(a.id)}
                    whileTap={{ scale: 0.95 }}
                    className="text-red-600 hover:text-red-500 text-sm font-medium"
                  >
                    删除
                  </motion.button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
