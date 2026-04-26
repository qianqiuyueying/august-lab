import { useState, useEffect, type FormEvent } from 'react';
import { motion } from 'framer-motion';
import { getAbout, updateAbout } from '../../api/about';
import ArticleContent from '../../components/articles/ArticleContent';
import TagInput from '../../components/admin/TagInput';

export default function AdminPages() {
  const [eyebrow, setEyebrow] = useState('About');
  const [title, setTitle] = useState('');
  const [coverImage, setCoverImage] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('markdown');
  const [techStack, setTechStack] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [preview, setPreview] = useState(false);

  useEffect(() => {
    loadAbout();
  }, []);

  const loadAbout = async () => {
    try {
      const data = await getAbout();
      setEyebrow(data.eyebrow || 'About');
      setTitle(data.title);
      setCoverImage(data.cover_image);
      setContent(data.content);
      setContentType(data.content_type || 'markdown');
      try {
        setTechStack(JSON.parse(data.tech_stack) as string[]);
      } catch {
        setTechStack([]);
      }
    } catch {
      // About page doesn't exist yet — show empty form
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateAbout({
        eyebrow,
        title,
        cover_image: coverImage,
        content,
        content_type: contentType,
        tech_stack: JSON.stringify(techStack),
      });
      setSuccess('已保存');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse h-64 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">关于页</h1>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-sm">
          {error}
        </motion.div>
      )}
      {success && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-green-600 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg text-sm">
          {success}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Eyebrow + Title */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Eyebrow 标签</label>
              <input
                type="text"
                value={eyebrow}
                onChange={(e) => setEyebrow(e.target.value)}
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">主标题</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                placeholder="关于 August's Lab"
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              />
            </div>
          </div>

          {/* Cover Image */}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">封面图片路径</label>
            <input
              type="text"
              value={coverImage}
              onChange={(e) => setCoverImage(e.target.value)}
              placeholder="/images/brand/about-workbench.webp"
              className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
            />
          </div>

          {/* Content type selector + editor */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">正文内容</label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
                className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-2 py-1 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-xs focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all"
              >
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
            </div>

            {/* Toggle */}
            {contentType === 'markdown' && (
              <div className="mb-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => setPreview(false)}
                  className={`px-3 py-1 text-xs rounded-md transition-colors ${!preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}
                >
                  编辑
                </button>
                <button
                  type="button"
                  onClick={() => setPreview(true)}
                  className={`px-3 py-1 text-xs rounded-md transition-colors ${preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}
                >
                  预览
                </button>
              </div>
            )}

            {contentType === 'markdown' && preview ? (
              <div className="border border-zinc-300 dark:border-zinc-700 rounded-lg p-4 bg-white dark:bg-zinc-900 min-h-[160px] prose dark:prose-invert max-w-none">
                <ArticleContent content={content} />
              </div>
            ) : (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={10}
                className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all font-mono text-sm"
                placeholder="输入 Markdown 内容..."
              />
            )}
          </div>

          {/* Tech Stack */}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">技术栈标签</label>
            <TagInput tags={techStack} onChange={setTechStack} />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <motion.button
              type="submit"
              disabled={saving}
              whileTap={{ scale: saving ? 1 : 0.98 }}
              className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
            >
              {saving ? '保存中...' : '保存'}
            </motion.button>
            <a
              href="/about"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-500 dark:text-zinc-400 hover:text-accent dark:hover:text-accent-dark transition-colors"
            >
              前台预览 →
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
