import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface ArticleEditorProps {
  initialContent?: string;
  onChange: (content: string) => void;
  onRequestImage?: () => void;
}

export default function ArticleEditor({ initialContent = '', onChange, onRequestImage }: ArticleEditorProps) {
  const [preview, setPreview] = useState(false);

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <label className="block text-sm font-bold text-zinc-700 dark:text-zinc-300">
          内容 (Markdown)
        </label>
        <div className="flex gap-2">
          {onRequestImage && (
            <button
              type="button"
              onClick={onRequestImage}
              className="text-sm font-bold text-accent transition-colors hover:text-accent-hover"
            >
              插入图片
            </button>
          )}
          <button
            type="button"
            onClick={() => setPreview(!preview)}
            className="text-sm font-bold text-accent transition-colors hover:text-accent-hover"
          >
            {preview ? '编辑' : '预览'}
          </button>
        </div>
      </div>
      {preview ? (
        <div className="markdown-body min-h-[300px] rounded-lg border border-border bg-paper p-4 dark:border-border-dark dark:bg-surface-dark">
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
            {initialContent}
          </ReactMarkdown>
        </div>
      ) : (
        <textarea
          value={initialContent}
          onChange={(event) => onChange(event.target.value)}
          rows={16}
          className="w-full rounded-lg border border-zinc-300 bg-white p-3 font-mono text-sm text-zinc-900 transition-all focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 dark:border-zinc-700 dark:bg-surface-dark dark:text-zinc-100"
          placeholder="在此输入 Markdown 内容，图片可使用标准语法：![说明](/uploads/images/example.webp)"
        />
      )}
    </div>
  );
}
