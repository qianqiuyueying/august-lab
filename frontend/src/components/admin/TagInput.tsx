import { useState } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
}

export default function TagInput({ tags, onChange }: TagInputProps) {
  const [input, setInput] = useState('');

  const add = () => {
    const trimmed = input.trim();
    if (!trimmed || tags.includes(trimmed)) return;
    onChange([...tags, trimmed]);
    setInput('');
  };

  const remove = (index: number) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-2">
        {tags.map((tag, i) => (
          <span key={i} className="inline-flex items-center gap-1 bg-accent-subtle dark:bg-accent-subtle-dark text-accent dark:text-accent px-3 py-1 rounded-full text-sm">
            {tag}
            <button
              type="button"
              onClick={() => remove(i)}
              className="ml-0.5 text-accent/60 hover:text-accent dark:text-accent-dark/60 dark:hover:text-accent-dark"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add(); } }}
          placeholder="输入标签后按回车"
          className="flex-1 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm"
        />
        <button type="button" onClick={add} className="px-4 py-2 bg-accent text-white rounded-lg text-sm hover:bg-accent-hover transition-colors">
          添加
        </button>
      </div>
    </div>
  );
}
