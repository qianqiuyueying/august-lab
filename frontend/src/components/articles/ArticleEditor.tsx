import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface ArticleEditorProps {
  initialContent?: string;
  onChange: (content: string) => void;
}

export default function ArticleEditor({ initialContent = '', onChange }: ArticleEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [preview, setPreview] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    onChange(e.target.value);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
          内容 (Markdown)
        </label>
        <button
          type="button"
          onClick={() => setPreview(!preview)}
          className="text-sm text-accent hover:text-accent-hover transition-colors"
        >
          {preview ? '编辑' : '预览'}
        </button>
      </div>
      {preview ? (
        <div className="prose prose-zinc dark:prose-invert max-w-none border border-zinc-300 dark:border-zinc-700 rounded-lg p-4 min-h-[300px] bg-zinc-50 dark:bg-zinc-900">
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
            {content}
          </ReactMarkdown>
        </div>
      ) : (
        <textarea
          value={content}
          onChange={handleChange}
          rows={16}
          className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg p-3 font-mono text-sm bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
          placeholder="在此输入 Markdown 内容..."
        />
      )}
    </div>
  );
}
