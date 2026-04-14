import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
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
  }, [isAuthenticated]);

  const loadPages = async () => {
    try {
      const data = await getPages();
      setPages(data);
    } catch (err: any) {
      setError(err.message);
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
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此页面吗？')) return;
    try {
      await deletePage(id);
      await loadPages();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">静态页面管理</h1>

      {error && <div className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded mb-4">{error}</div>}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">创建新页面</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">标题</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Slug</label>
              <input
                type="text"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                required
                placeholder="about"
                className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">状态</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="draft">草稿</option>
              <option value="published">发布</option>
            </select>
          </div>
          <ArticleEditor initialContent={content} onChange={setContent} />
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading ? '创建中...' : '创建页面'}
          </button>
        </form>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">已有页面</h2>
        {pages.length === 0 ? (
          <div className="text-gray-500">暂无页面</div>
        ) : (
          <div className="space-y-2">
            {pages.map((p) => (
              <div key={p.id} className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-2">
                <div>
                  <span className="font-medium text-gray-900 dark:text-white">{p.title}</span>
                  <span className="ml-2 text-sm text-gray-500">/{p.slug}</span>
                  <span className={`ml-2 text-xs px-2 py-0.5 rounded ${p.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {p.status === 'published' ? '已发布' : '草稿'}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="text-red-600 hover:text-red-500 text-sm"
                >
                  删除
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
