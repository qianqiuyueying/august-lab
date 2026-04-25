import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { createProduct, deleteProduct, getAdminProducts, updateProduct, uploadProductZip } from '../../api/products';
import {
  AdminDrawer,
  AdminEmptyState,
  AdminErrorBanner,
  AdminPageHeader,
  AdminPanel,
  AdminStats,
  AdminStatusBadge,
  AdminToolbar,
  ConfirmDialog,
  type AdminStat,
} from '../../components/admin/AdminPrimitives';
import { formatDate } from '../../utils/formatDate';
import type { Product } from '../../types';

type ProductDrawerMode = 'create' | 'edit';

interface ProductFormState {
  title: string;
  slug: string;
  description: string;
  status: string;
}

const emptyProductForm: ProductFormState = {
  title: '',
  slug: '',
  description: '',
  status: 'draft',
};

function getErrorMessage(error: unknown, fallback: string) {
  return (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || fallback;
}

export default function AdminProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [statsSource, setStatsSource] = useState<Product[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [uploadingId, setUploadingId] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<ProductDrawerMode>('create');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<ProductFormState>(emptyProductForm);
  const [deleteTarget, setDeleteTarget] = useState<Product | null>(null);
  const uploadInputs = useRef<Record<number, HTMLInputElement | null>>({});

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [filteredData, allData] = await Promise.all([
        getAdminProducts(1, 50, statusFilter, search || undefined),
        statusFilter === 'all'
          ? Promise.resolve(null)
          : getAdminProducts(1, 50, 'all', search || undefined),
      ]);
      setProducts(filteredData.items);
      setStatsSource((allData ?? filteredData).items);
    } catch (loadError) {
      setError(getErrorMessage(loadError, '产品列表加载失败'));
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    void loadProducts();
  }, [loadProducts]);

  const stats = useMemo<AdminStat[]>(() => {
    const published = statsSource.filter((product) => product.status === 'published').length;
    const draft = statsSource.filter((product) => product.status === 'draft').length;
    const runnable = statsSource.filter((product) => product.runtime_url).length;
    return [
      { label: '全部产品', value: statsSource.length, tone: 'blue' },
      { label: '已发布', value: published, tone: 'green' },
      { label: '草稿', value: draft, tone: 'amber' },
      { label: '可运行', value: runnable, tone: 'zinc' },
    ];
  }, [statsSource]);

  const openCreateDrawer = () => {
    setDrawerMode('create');
    setEditingId(null);
    setForm(emptyProductForm);
    setError('');
    setDrawerOpen(true);
  };

  const openEditDrawer = (product: Product) => {
    setDrawerMode('edit');
    setEditingId(product.id);
    setForm({
      title: product.title,
      slug: product.slug,
      description: product.description || '',
      status: product.status,
    });
    setError('');
    setDrawerOpen(true);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.title.trim() || !form.slug.trim()) return;
    setSaving(true);
    setError('');
    try {
      if (drawerMode === 'edit' && editingId) {
        await updateProduct(editingId, {
          title: form.title.trim(),
          description: form.description.trim(),
          status: form.status,
        });
      } else {
        await createProduct({
          title: form.title.trim(),
          slug: form.slug.trim(),
          description: form.description.trim(),
          status: form.status,
        });
      }
      setDrawerOpen(false);
      setForm(emptyProductForm);
      setEditingId(null);
      await loadProducts();
    } catch (saveError) {
      setError(getErrorMessage(saveError, '产品保存失败'));
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (productId: number, event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadingId(productId);
    setError('');
    try {
      await uploadProductZip(productId, file);
      await loadProducts();
    } catch (uploadError) {
      setError(getErrorMessage(uploadError, 'ZIP 上传失败'));
    } finally {
      setUploadingId(null);
      const input = uploadInputs.current[productId];
      if (input) input.value = '';
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError('');
    try {
      await deleteProduct(deleteTarget.id);
      setDeleteTarget(null);
      await loadProducts();
    } catch (deleteError) {
      setError(getErrorMessage(deleteError, '产品删除失败'));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-5">
      <AdminPageHeader
        title="产品管理"
        description="维护产品页面、草稿、发布状态和 ZIP 静态包。上传成功后，产品前台页会直接运行静态作品。"
        actionLabel="创建产品"
        onAction={openCreateDrawer}
      />

      <AdminErrorBanner message={error} />
      <AdminStats stats={stats} />
      <AdminToolbar
        search={search}
        status={statusFilter}
        searchPlaceholder="搜索标题、slug 或描述"
        onSearchChange={setSearch}
        onStatusChange={setStatusFilter}
      />

      <AdminPanel>
        <div className="hidden grid-cols-[minmax(0,1.25fr)_120px_120px_140px_240px] gap-4 border-b border-border bg-zinc-50 px-5 py-3 text-xs font-bold text-text-muted dark:border-border-dark dark:bg-zinc-900/70 lg:grid">
          <span>产品</span>
          <span>状态</span>
          <span>运行文件</span>
          <span>更新时间</span>
          <span className="text-right">操作</span>
        </div>

        {loading ? (
          <AdminEmptyState title="正在加载产品" description="正在读取后台产品列表和发布状态。" />
        ) : products.length === 0 ? (
          <AdminEmptyState title="没有找到产品" description="调整搜索或状态筛选，或者创建一个新产品。" />
        ) : (
          <div className="divide-y divide-border dark:divide-border-dark">
            {products.map((product) => (
              <div
                key={product.id}
                className="grid gap-4 px-5 py-4 transition-colors hover:bg-zinc-50/80 dark:hover:bg-zinc-900/40 lg:grid-cols-[minmax(0,1.25fr)_120px_120px_140px_240px] lg:items-center"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-bold text-zinc-950 dark:text-white">{product.title}</div>
                  <div className="mt-1 text-xs font-medium text-accent">/{product.slug}</div>
                  <p className="mt-1 line-clamp-2 text-xs leading-5 text-text-muted dark:text-text-muted-dark">
                    {product.description || '暂无描述'}
                  </p>
                </div>
                <div>
                  <AdminStatusBadge status={product.status} />
                </div>
                <div>
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${
                      product.runtime_url
                        ? 'bg-success-subtle text-success dark:bg-success-subtle-dark dark:text-green-300'
                        : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300'
                    }`}
                  >
                    {product.runtime_url ? '已上传' : '未上传'}
                  </span>
                </div>
                <div className="text-xs text-text-muted dark:text-text-muted-dark">{formatDate(product.updated_at || product.created_at) || '无记录'}</div>
                <div className="flex flex-wrap justify-start gap-2 lg:justify-end">
                  {product.status === 'published' && (
                    <Link to={`/products/${product.slug}`} className="text-sm font-bold text-accent hover:text-accent-hover">
                      预览
                    </Link>
                  )}
                  {product.runtime_url && (
                    <a href={product.runtime_url} target="_blank" rel="noreferrer" className="text-sm font-bold text-accent hover:text-accent-hover">
                      运行页
                    </a>
                  )}
                  <button
                    type="button"
                    disabled={uploadingId === product.id}
                    onClick={() => uploadInputs.current[product.id]?.click()}
                    className="text-sm font-bold text-accent hover:text-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {uploadingId === product.id ? '上传中...' : '上传 ZIP'}
                  </button>
                  <input
                    ref={(node) => {
                      uploadInputs.current[product.id] = node;
                    }}
                    type="file"
                    accept=".zip"
                    onChange={(event) => void handleUpload(product.id, event)}
                    className="hidden"
                  />
                  <button type="button" onClick={() => openEditDrawer(product)} className="text-sm font-bold text-accent hover:text-accent-hover">
                    编辑
                  </button>
                  <button type="button" onClick={() => setDeleteTarget(product)} className="text-sm font-bold text-danger hover:text-red-700">
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </AdminPanel>

      <AdminDrawer
        open={drawerOpen}
        title={drawerMode === 'edit' ? '编辑产品' : '创建产品'}
        description={drawerMode === 'edit' ? '修改产品标题、描述和发布状态。slug 创建后保持不变。' : '创建产品记录后，可以在列表中上传 ZIP 静态包。'}
        onClose={() => {
          if (!saving) setDrawerOpen(false);
        }}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-bold text-zinc-700 dark:text-zinc-300">标题</span>
              <input
                value={form.title}
                onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
                required
                className="focus-ring w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-bold text-zinc-700 dark:text-zinc-300">状态</span>
              <select
                value={form.status}
                onChange={(event) => setForm((current) => ({ ...current, status: event.target.value }))}
                className="focus-ring w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
              >
                <option value="draft">草稿</option>
                <option value="published">发布</option>
              </select>
            </label>
          </div>
          <label className="block">
            <span className="mb-1 block text-sm font-bold text-zinc-700 dark:text-zinc-300">Slug</span>
            <input
              value={form.slug}
              onChange={(event) => setForm((current) => ({ ...current, slug: event.target.value }))}
              required
              disabled={drawerMode === 'edit'}
              placeholder="my-product"
              className="focus-ring w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-zinc-900 disabled:bg-zinc-100 disabled:text-zinc-500 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100 dark:disabled:bg-zinc-900"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-bold text-zinc-700 dark:text-zinc-300">描述</span>
            <textarea
              value={form.description}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
              rows={5}
              className="focus-ring w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
              placeholder="产品简短描述"
            />
          </label>
          <div className="sticky bottom-0 -mx-5 -mb-5 flex justify-end gap-2 border-t border-border bg-background px-5 py-4 dark:border-border-dark dark:bg-background-dark">
            <button type="button" disabled={saving} onClick={() => setDrawerOpen(false)} className="lab-button-secondary min-h-10 px-3 text-sm disabled:opacity-50">
              取消
            </button>
            <button type="submit" disabled={saving || !form.title.trim() || !form.slug.trim()} className="lab-button min-h-10 px-3 text-sm disabled:opacity-50">
              {saving ? '保存中...' : drawerMode === 'edit' ? '保存修改' : '创建产品'}
            </button>
          </div>
        </form>
      </AdminDrawer>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="删除产品"
        description={deleteTarget ? `确定要删除产品「${deleteTarget.title}」吗？对应的产品静态目录也会被删除。` : ''}
        loading={deleting}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </div>
  );
}
