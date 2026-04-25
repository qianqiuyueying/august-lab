import { useCallback, useEffect, useRef, useState, type ChangeEvent } from 'react';
import { deleteAsset, getAssets, uploadAsset } from '../../api/assets';
import type { Asset } from '../../types';
import { AdminEmptyState, AdminErrorBanner } from './AdminPrimitives';

interface MediaPickerProps {
  open: boolean;
  title?: string;
  onClose: () => void;
  onSelect: (asset: Asset) => void;
}

function getErrorMessage(error: unknown, fallback: string) {
  return (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || fallback;
}

export default function MediaPicker({ open, title = '选择图片', onClose, onSelect }: MediaPickerProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAssets(1, 48, search || undefined);
      setAssets(data.items);
    } catch (loadError) {
      setError(getErrorMessage(loadError, '图片资源加载失败'));
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    if (open) void loadAssets();
  }, [open, loadAssets]);

  if (!open) return null;

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const asset = await uploadAsset(file);
      setAssets((current) => [asset, ...current]);
      onSelect(asset);
    } catch (uploadError) {
      setError(getErrorMessage(uploadError, '图片上传失败'));
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const handleDelete = async (asset: Asset) => {
    setError('');
    try {
      await deleteAsset(asset.id);
      setAssets((current) => current.filter((item) => item.id !== asset.id));
    } catch (deleteError) {
      setError(getErrorMessage(deleteError, '图片删除失败'));
    }
  };

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-zinc-950/40 p-4">
      <div className="flex max-h-[86vh] w-full max-w-5xl flex-col overflow-hidden rounded-lg border border-border bg-white shadow-xl dark:border-border-dark dark:bg-surface-dark">
        <div className="flex flex-col gap-3 border-b border-border p-4 dark:border-border-dark md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-bold text-zinc-950 dark:text-white">{title}</h2>
            <p className="mt-1 text-sm text-text-muted dark:text-text-muted-dark">上传图片后可作为封面，或插入到 Markdown 正文中。</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <input ref={fileRef} type="file" accept="image/*" onChange={handleUpload} className="hidden" />
            <button type="button" disabled={uploading} onClick={() => fileRef.current?.click()} className="lab-button min-h-10 px-3 text-sm disabled:opacity-50">
              {uploading ? '上传中...' : '上传图片'}
            </button>
            <button type="button" onClick={onClose} className="lab-button-secondary min-h-10 px-3 text-sm">
              关闭
            </button>
          </div>
        </div>

        <div className="border-b border-border p-3 dark:border-border-dark">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="搜索图片文件名"
            className="focus-ring h-11 w-full rounded-lg border border-border bg-white px-3 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
          />
        </div>

        <div className="flex-1 overflow-auto p-4">
          <AdminErrorBanner message={error} />
          {loading ? (
            <AdminEmptyState title="正在加载图片" description="正在读取媒体库中的图片资源。" />
          ) : assets.length === 0 ? (
            <AdminEmptyState title="还没有图片" description="上传一张图片后即可用于文章封面或正文插图。" />
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {assets.map((asset) => (
                <div key={asset.id} className="overflow-hidden rounded-lg border border-border bg-paper-soft dark:border-border-dark dark:bg-zinc-950">
                  <button type="button" onClick={() => onSelect(asset)} className="focus-ring block w-full text-left">
                    <img src={asset.url} alt={asset.original_name} className="aspect-[4/3] w-full object-cover" />
                    <div className="p-3">
                      <div className="truncate text-xs font-bold text-zinc-900 dark:text-white">{asset.original_name}</div>
                      <div className="mt-1 text-[11px] text-text-muted dark:text-text-muted-dark">{Math.ceil(asset.size / 1024)} KB</div>
                    </div>
                  </button>
                  <div className="flex border-t border-border dark:border-border-dark">
                    <button type="button" onClick={() => void navigator.clipboard?.writeText(asset.url)} className="flex-1 px-3 py-2 text-xs font-bold text-accent hover:bg-accent-subtle dark:hover:bg-accent-subtle-dark">
                      复制 URL
                    </button>
                    <button type="button" onClick={() => void handleDelete(asset)} className="flex-1 px-3 py-2 text-xs font-bold text-danger hover:bg-danger-subtle dark:hover:bg-danger-subtle-dark">
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
