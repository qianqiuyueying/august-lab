interface CoverImageFieldProps {
  value: string;
  onSelect: () => void;
  onClear: () => void;
}

export default function CoverImageField({ value, onSelect, onClear }: CoverImageFieldProps) {
  const preview = value || '/images/brand/fallback-article.webp';

  return (
    <div className="rounded-lg border border-border bg-white p-3 dark:border-border-dark dark:bg-zinc-950">
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="text-sm font-bold text-zinc-700 dark:text-zinc-300">封面图片</span>
        <div className="flex gap-2">
          {value && (
            <button type="button" onClick={onClear} className="text-xs font-bold text-danger hover:text-red-700">
              清空
            </button>
          )}
          <button type="button" onClick={onSelect} className="text-xs font-bold text-accent hover:text-accent-hover">
            选择图片
          </button>
        </div>
      </div>
      <div className="overflow-hidden rounded-lg border border-border bg-paper-soft dark:border-border-dark dark:bg-surface-dark">
        <img src={preview} alt={value ? '文章封面预览' : ''} aria-hidden={!value} className="aspect-[16/7] w-full object-cover" />
      </div>
      <p className="mt-2 truncate text-xs text-text-muted dark:text-text-muted-dark">
        {value || '未选择封面，将使用默认占位图片。'}
      </p>
    </div>
  );
}
