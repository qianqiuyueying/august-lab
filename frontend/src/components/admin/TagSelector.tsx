import { useMemo, useState } from 'react';
import type { Tag } from '../../types';
import { createTag } from '../../api/tags';

interface TagSelectorProps {
  tags: Tag[];
  selected: string[];
  disabled?: boolean;
  onCreated: (tag: Tag) => void;
  onChange: (tags: string[]) => void;
}

export default function TagSelector({ tags, selected, disabled = false, onCreated, onChange }: TagSelectorProps) {
  const [newTag, setNewTag] = useState('');
  const [creating, setCreating] = useState(false);
  const normalizedSelected = useMemo(() => new Set(selected), [selected]);

  const toggleTag = (name: string) => {
    if (normalizedSelected.has(name)) {
      onChange(selected.filter((item) => item !== name));
    } else {
      onChange([...selected, name]);
    }
  };

  const handleCreate = async () => {
    const name = newTag.trim();
    if (!name || normalizedSelected.has(name)) return;
    const existing = tags.find((tag) => tag.name.toLowerCase() === name.toLowerCase());
    if (existing) {
      onChange([...selected, existing.name]);
      setNewTag('');
      return;
    }

    setCreating(true);
    try {
      const created = await createTag(name);
      onCreated(created);
      onChange([...selected, created.name]);
      setNewTag('');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-white p-3 dark:border-border-dark dark:bg-zinc-950">
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="text-sm font-bold text-zinc-700 dark:text-zinc-300">标签</span>
        <span className="text-xs text-text-muted dark:text-text-muted-dark">{selected.length} 个已选</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const active = normalizedSelected.has(tag.name);
          return (
            <button
              key={tag.id}
              type="button"
              disabled={disabled}
              onClick={() => toggleTag(tag.name)}
              className={`focus-ring rounded-full border px-3 py-1.5 text-xs font-bold transition-colors disabled:opacity-50 ${
                active
                  ? 'border-accent bg-accent-subtle text-accent-hover dark:border-blue-400 dark:bg-accent-subtle-dark dark:text-blue-100'
                  : 'border-border bg-paper-soft text-text-muted hover:border-accent hover:text-accent dark:border-border-dark dark:bg-surface-dark dark:text-text-muted-dark'
              }`}
            >
              {tag.name}
            </button>
          );
        })}
      </div>

      {tags.length === 0 && (
        <p className="rounded-md bg-zinc-50 px-3 py-2 text-xs text-text-muted dark:bg-zinc-900 dark:text-text-muted-dark">
          还没有标签，输入名称即可创建。
        </p>
      )}

      <div className="mt-3 flex gap-2">
        <input
          value={newTag}
          disabled={disabled || creating}
          onChange={(event) => setNewTag(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              void handleCreate();
            }
          }}
          placeholder="创建新标签"
          className="focus-ring h-10 min-w-0 flex-1 rounded-lg border border-border bg-white px-3 text-sm text-zinc-900 dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
        />
        <button
          type="button"
          disabled={disabled || creating || !newTag.trim()}
          onClick={() => void handleCreate()}
          className="lab-button-secondary h-10 px-3 text-sm disabled:opacity-50"
        >
          {creating ? '创建中...' : '创建'}
        </button>
      </div>
    </div>
  );
}
