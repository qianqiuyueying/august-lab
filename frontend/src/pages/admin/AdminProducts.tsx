import { useState, useEffect, type FormEvent, useRef } from 'react';
import { motion } from 'framer-motion';
import { getProducts, createProduct, deleteProduct, uploadProductZip } from '../../api/products';
import type { Product } from '../../types';
import { useAuth } from '../../contexts/useAuth';

export default function AdminProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('draft');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadingId, setUploadingId] = useState<number | null>(null);
  const { isAuthenticated } = useAuth();

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadProducts();
  }, [isAuthenticated]);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !slug) return;
    setLoading(true);
    setError('');
    try {
      await createProduct({ slug, title, description, status });
      setTitle('');
      setSlug('');
      setDescription('');
      setStatus('draft');
      await loadProducts();
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此产品吗？')) return;
    try {
      await deleteProduct(id);
      await loadProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const handleUpload = async (productId: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingId(productId);
    setError('');
    try {
      await uploadProductZip(productId, file);
      await loadProducts();
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '上传失败');
    } finally {
      setUploadingId(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">产品管理</h1>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-sm">
          {error}
        </motion.div>
      )}

      {/* Create product */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">创建新产品</h2>
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
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Slug</label>
              <input
                type="text"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                required
                placeholder="my-project"
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">描述</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="产品简短描述"
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
          <motion.button
            type="submit"
            disabled={loading}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
          >
            {loading ? '创建中...' : '创建产品'}
          </motion.button>
        </form>
      </motion.div>

      {/* Product list */}
      <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">已有产品</h2>
        {products.length === 0 ? (
          <div className="text-zinc-500">暂无产品</div>
        ) : (
          <div className="space-y-3">
            {products.map((p) => (
              <div key={p.id} className="flex justify-between items-center border-b border-zinc-200 dark:border-zinc-800 pb-3 last:border-b-0">
                <div className="flex-1">
                  <span className="font-medium text-zinc-900 dark:text-white">{p.title}</span>
                  <span className="ml-2 text-sm text-zinc-500">/{p.slug}</span>
                  <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${p.status === 'published' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'}`}>
                    {p.status === 'published' ? '已发布' : '草稿'}
                  </span>
                  {p.description && (
                    <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">{p.description}</div>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <label className="text-sm text-accent hover:text-accent-hover cursor-pointer font-medium" title="上传 ZIP">
                    {uploadingId === p.id ? '上传中...' : '上传 ZIP'}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".zip"
                      disabled={uploadingId === p.id}
                      onChange={(e) => handleUpload(p.id, e)}
                      className="hidden"
                    />
                  </label>
                  <motion.button
                    onClick={() => handleDelete(p.id)}
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
