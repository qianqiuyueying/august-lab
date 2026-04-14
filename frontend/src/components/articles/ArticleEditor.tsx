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
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          内容 (Markdown)
        </label>
        <button
          type="button"
          onClick={() => setPreview(!preview)}
          className="text-sm text-indigo-600 hover:text-indigo-500"
        >
          {preview ? '编辑' : '预览'}
        </button>
      </div>
      {preview ? (
        <div className="prose prose-lg dark:prose-invert max-w-none border border-gray-300 dark:border-gray-600 rounded p-4 min-h-[300px] bg-gray-50 dark:bg-gray-900">
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
            {content}
          </ReactMarkdown>
        </div>
      ) : (
        <textarea
          value={content}
          onChange={handleChange}
          rows={16}
          className="w-full border border-gray-300 dark:border-gray-600 rounded-md p-3 font-mono text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          placeholder="在此输入 Markdown 内容..."
        />
      )}
    </div>
  );
}
