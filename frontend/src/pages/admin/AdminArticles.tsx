import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { createArticle, deleteArticle, getAdminArticles, getArticle, updateArticle, uploadMd } from '../../api/articles';
import { getTags } from '../../api/tags';
import ArticleEditor from '../../components/articles/ArticleEditor';
import CoverImageField from '../../components/admin/CoverImageField';
import MediaPicker from '../../components/admin/MediaPicker';
import TagSelector from '../../components/admin/TagSelector';
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
import type { ArticleListItem, Asset, Tag } from '../../types';

type ArticleDrawerMode = 'create' | 'edit';
type MediaTarget = 'cover' | 'content';

interface ArticleFormState {
  title: string;
  summary: string;
  coverImage: string;
  selectedTags: string[];
  status: string;
  content: string;
}

const emptyArticleForm: ArticleFormState = {
  title: '',
  summary: '',
  coverImage: '',
  selectedTags: [],
  status: 'draft',
  content: '',
};

function getErrorMessage(error: unknown, fallback: string) {
  return (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || fallback;
}

export default function AdminArticles() {
  const [articles, setArticles] = useState<ArticleListItem[]>([]);
  const [statsSource, setStatsSource] = useState<ArticleListItem[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [tagFilter, setTagFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<ArticleDrawerMode>('create');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<ArticleFormState>(emptyArticleForm);
  const [deleteTarget, setDeleteTarget] = useState<ArticleListItem | null>(null);
  const [mediaOpen, setMediaOpen] = useState(false);
  const [mediaTarget, setMediaTarget] = useState<MediaTarget>('cover');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadTags = useCallback(async () => {
    try {
      const data = await getTags();
      setTags(data);
    } catch (tagError) {
      setError(getErrorMessage(tagError, '标签加载失败'));
    }
  }, []);

  const loadArticles = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [filteredData, allData] = await Promise.all([
        getAdminArticles(1, 50, statusFilter, search || undefined, tagFilter || undefined),
        statusFilter === 'all'
          ? Promise.resolve(null)
          : getAdminArticles(1, 50, 'all', search || undefined, tagFilter || undefined),
      ]);
      setArticles(filteredData.items);
      setStatsSource((allData ?? filteredData).items);
    } catch (loadError) {
      setError(getErrorMessage(loadError, '文章列表加载失败'));
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, tagFilter]);

  useEffect(() => {
    void loadTags();
  }, [loadTags]);

  useEffect(() => {
    void loadArticles();
  }, [loadArticles]);

  const stats = useMemo<AdminStat[]>(() => {
    const published = statsSource.filter((article) => article.status === 'published').length;
    const draft = statsSource.filter((article) => article.status === 'draft').length;
    return [
      { label: '全部文章', value: statsSource.length, tone: 'blue' },
      { label: '已发布', value: published, tone: 'green' },
      { label: '草稿', value: draft, tone: 'amber' },
    ];
  }, [statsSource]);

  const openCreateDrawer = () => {
    setDrawerMode('create');
    setEditingId(null);
    setForm(emptyArticleForm);
    setError('');
    setDrawerOpen(true);
  };

  const openEditDrawer = async (article: ArticleListItem) => {
    setDrawerMode('edit');
    setError('');
    setDrawerOpen(true);
    try {
      const fullArticle = await getArticle(article.slug);
      setEditingId(fullArticle.id);
      setForm({
        title: fullArticle.title,
        summary: fullArticle.summary || '',
        coverImage: fullArticle.cover_image || '',
        selectedTags: fullArticle.tags.map((tag) => tag.name),
        status: fullArticle.status,
        content: fullArticle.content,
      });
    } catch (editError) {
      setDrawerOpen(false);
      setError(getErrorMessage(editError, '文章详情加载失败'));
    }
  };

  const handleMarkdownUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError('');
    try {
      const parsed = await uploadMd(file);
      setDrawerMode('create');
      setEditingId(null);
      setForm({
        ...emptyArticleForm,
        title: parsed.title,
        content: parsed.content,
        coverImage: parsed.cover_image || '',
      });
      setDrawerOpen(true);
    } catch (uploadError) {
      setError(getErrorMessage(uploadError, 'Markdown 文件解析失败'));
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.title.trim() || !form.content.trim()) return;
    setSaving(true);
    setError('');
    try {
      const payload = {
        title: form.title.trim(),
        content: form.content,
        summary: form.summary.trim(),
        cover_image: form.coverImage || null,
        status: form.status,
        tags: form.selectedTags,
      };
      if (drawerMode === 'edit' && editingId) {
        await updateArticle(editingId, payload);
      } else {
        await createArticle(payload);
      }
      setDrawerOpen(false);
      setForm(emptyArticleForm);
      setEditingId(null);
      await Promise.all([loadArticles(), loadTags()]);
    } catch (saveError) {
      setError(getErrorMessage(saveError, '文章保存失败'));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError('');
    try {
      await deleteArticle(deleteTarget.id);
      setDeleteTarget(null);
      await loadArticles();
    } catch (deleteError) {
      setError(getErrorMessage(deleteError, '文章删除失败'));
    } finally {
      setDeleting(false);
    }
  };

  const openMedia = (target: MediaTarget) => {
    setMediaTarget(target);
    setMediaOpen(true);
  };

  const handleMediaSelect = (asset: Asset) => {
    if (mediaTarget === 'cover') {
      setForm((current) => ({ ...current, coverImage: asset.url }));
    } else {
      setForm((current) => ({
        ...current,
        content: `${current.content}${current.content.endsWith('\n') || !current.content ? '' : '\n\n'}![${asset.original_name}](${asset.url})`,
      }));
    }
    setMediaOpen(false);
  };

  return (
    <div className="space-y-5">
      <AdminPageHeader
        title="文章管理"
        description="维护文章、草稿、标签、封面和发布状态。默认从列表进入编辑，标签和图片资源可以复用。"
        actionLabel="新建文章"
        secondaryActionLabel="上传 Markdown"
        onAction={openCreateDrawer}
        onSecondaryAction={() => fileInputRef.current?.click()}
      />

      <input ref={fileInputRef} type="file" accept=".md" onChange={handleMarkdownUpload} className="hidden" />

      <AdminErrorBanner message={error} />
      <AdminStats stats={stats} />
      <AdminToolbar
        search={search}
        status={statusFilter}
        searchPlaceholder="搜索标题、摘要或正文"
        onSearchChange={setSearch}
        onStatusChange={setStatusFilter}
      >
        <label className="md:w-48">
          <span className="sr-only">标签</span>
          <select
            value={tagFilter}
            onChange={(event) => setTagFilter(event.target.value)}
            className="focus-ring h-11 w-full rounded-lg border border-border bg-white px-3 text-sm text-zinc-900 outline-none transition-colors focus:border-accent dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
          >
            <option value="">全部标签</option>
            {tags.map((tag) => (
              <option key={tag.id} value={tag.name}>
                {tag.name}
              </option>
            ))}
          </select>
        </label>
      </AdminToolbar>

      <AdminPanel>
        <div className="hidden grid-cols-[minmax(0,1.2fr)_220px_110px_130px_150px] gap-4 border-b border-border bg-zinc-50 px-5 py-3 text-xs font-bold text-text-muted dark:border-border-dark dark:bg-zinc-900/70 lg:grid">
          <span>文章</span>
          <span>标签</span>
          <span>状态</span>
          <span>更新时间</span>
          <span className="text-right">操作</span>
        </div>

        {loading ? (
          <AdminEmptyState title="正在加载文章" description="正在读取后台文章列表和状态统计。" />
        ) : articles.length === 0 ? (
          <AdminEmptyState title="没有找到文章" description="调整搜索、状态或标签筛选，或者新建一篇文章。" />
        ) : (
          <div className="divide-y divide-border dark:divide-border-dark">
            {articles.map((article) => (
              <div
                key={article.id}
                className="grid gap-4 px-5 py-4 transition-colors hover:bg-zinc-50/80 dark:hover:bg-zinc-900/40 lg:grid-cols-[minmax(0,1.2fr)_220px_110px_130px_150px] lg:items-center"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-bold text-zinc-950 dark:text-white">{article.title}</div>
                  <p className="mt-1 line-clamp-2 text-xs leading-5 text-text-muted dark:text-text-muted-dark">
                    {article.summary || '暂无摘要'}
                  </p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {article.tags.length > 0 ? (
                    article.tags.map((tag) => (
                      <span key={tag.id} className="lab-chip px-2 py-0.5 text-[11px]">
                        {tag.name}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-text-muted dark:text-text-muted-dark">无标签</span>
                  )}
                </div>
                <div>
                  <AdminStatusBadge status={article.status} />
                </div>
                <div className="text-xs text-text-muted dark:text-text-muted-dark">{formatDate(article.created_at) || '无记录'}</div>
                <div className="flex flex-wrap justify-start gap-2 lg:justify-end">
                  {article.status === 'published' && (
                    <Link to={`/articles/${article.slug}`} className="text-sm font-bold text-accent hover:text-accent-hover">
                      预览
                    </Link>
                  )}
                  <button type="button" onClick={() => void openEditDrawer(article)} className="text-sm font-bold text-accent hover:text-accent-hover">
                    编辑
                  </button>
                  <button type="button" onClick={() => setDeleteTarget(article)} className="text-sm font-bold text-danger hover:text-red-700">
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
        title={drawerMode === 'edit' ? '编辑文章' : '新建文章'}
        description="填写标题、摘要、封面、标签和发布状态，正文支持 Markdown 与图片链接。"
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
            <span className="mb-1 block text-sm font-bold text-zinc-700 dark:text-zinc-300">摘要</span>
            <input
              value={form.summary}
              onChange={(event) => setForm((current) => ({ ...current, summary: event.target.value }))}
              className="focus-ring w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
              placeholder="用于列表和文章页的简短说明"
            />
          </label>

          <CoverImageField
            value={form.coverImage}
            onSelect={() => openMedia('cover')}
            onClear={() => setForm((current) => ({ ...current, coverImage: '' }))}
          />

          <TagSelector
            tags={tags}
            selected={form.selectedTags}
            disabled={saving}
            onCreated={(tag) => setTags((current) => [...current, tag].sort((a, b) => a.name.localeCompare(b.name)))}
            onChange={(selectedTags) => setForm((current) => ({ ...current, selectedTags }))}
          />

          <ArticleEditor
            initialContent={form.content}
            onChange={(content) => setForm((current) => ({ ...current, content }))}
            onRequestImage={() => openMedia('content')}
          />

          <div className="sticky bottom-0 -mx-5 -mb-5 flex justify-end gap-2 border-t border-border bg-background px-5 py-4 dark:border-border-dark dark:bg-background-dark">
            <button type="button" disabled={saving} onClick={() => setDrawerOpen(false)} className="lab-button-secondary min-h-10 px-3 text-sm disabled:opacity-50">
              取消
            </button>
            <button type="submit" disabled={saving || !form.title.trim() || !form.content.trim()} className="lab-button min-h-10 px-3 text-sm disabled:opacity-50">
              {saving ? '保存中...' : drawerMode === 'edit' ? '保存修改' : '创建文章'}
            </button>
          </div>
        </form>
      </AdminDrawer>

      <MediaPicker open={mediaOpen} title={mediaTarget === 'cover' ? '选择封面图片' : '插入正文图片'} onClose={() => setMediaOpen(false)} onSelect={handleMediaSelect} />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="删除文章"
        description={deleteTarget ? `确定要删除文章「${deleteTarget.title}」吗？这个操作不能撤销。` : ''}
        loading={deleting}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </div>
  );
}
