import { useState, useEffect, type FormEvent } from 'react';
import { motion } from 'framer-motion';
import { getAbout, updateAbout } from '../../api/about';
import ArticleContent from '../../components/articles/ArticleContent';
import TagInput from '../../components/admin/TagInput';

const CONTACT_PLATFORMS = [
  { value: 'github', label: 'GitHub' },
  { value: 'twitter', label: 'Twitter / X' },
  { value: 'email', label: 'Email' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'custom', label: '自定义' },
] as const;

interface InfoCard {
  label: string;
  value: string;
}

interface Contact {
  platform: string;
  url: string;
  name?: string;
}

export default function AdminPages() {
  // Hero fields
  const [eyebrow, setEyebrow] = useState('About');
  const [title, setTitle] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [heroSubtitle, setHeroSubtitle] = useState('');
  const [coverImage, setCoverImage] = useState('');

  // Content fields
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('markdown');
  const [preview, setPreview] = useState(false);

  // Tech stack
  const [techStack, setTechStack] = useState<string[]>([]);

  // Info cards
  const [infoCards, setInfoCards] = useState<InfoCard[]>([]);

  // Contacts
  const [contacts, setContacts] = useState<Contact[]>([]);

  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadAbout();
  }, []);

  const loadAbout = async () => {
    try {
      const data = await getAbout();
      setEyebrow(data.eyebrow || 'About');
      setTitle(data.title);
      setAvatarUrl(data.avatar_url || '');
      setHeroSubtitle(data.hero_subtitle || '');
      setCoverImage(data.cover_image);
      setContent(data.content);
      setContentType(data.content_type || 'markdown');
      try {
        setTechStack(JSON.parse(data.tech_stack) as string[]);
      } catch {
        setTechStack([]);
      }
      setInfoCards(Array.isArray(data.info_cards) ? data.info_cards : []);
      setContacts(Array.isArray(data.contacts) ? data.contacts : []);
    } catch {
      // About page doesn't exist yet — show empty form
    } finally {
      setLoading(false);
    }
  };

  const addInfoCard = () => {
    setInfoCards([...infoCards, { label: '', value: '' }]);
  };

  const removeInfoCard = (index: number) => {
    setInfoCards(infoCards.filter((_, i) => i !== index));
  };

  const updateInfoCard = (index: number, field: keyof InfoCard, val: string) => {
    setInfoCards(infoCards.map((card, i) => (i === index ? { ...card, [field]: val } : card)));
  };

  const addContact = () => {
    setContacts([...contacts, { platform: 'github', url: '' }]);
  };

  const removeContact = (index: number) => {
    setContacts(contacts.filter((_, i) => i !== index));
  };

  const updateContact = (index: number, field: keyof Contact, val: string) => {
    setContacts(contacts.map((c, i) => (i === index ? { ...c, [field]: val } : c)));
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
        avatar_url: avatarUrl,
        hero_subtitle: heroSubtitle,
        cover_image: coverImage,
        content,
        content_type: contentType,
        tech_stack: JSON.stringify(techStack),
        info_cards: infoCards.filter((c) => c.label && c.value),
        contacts: contacts.filter((c) => c.url),
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

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* ===== Hero 区 ===== */}
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">Hero 头部</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Eyebrow 标签</label>
                  <input type="text" value={eyebrow} onChange={(e) => setEyebrow(e.target.value)} className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">主标题</label>
                  <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="August's Lab" className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all" />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">头像 URL</label>
                  <input type="text" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} placeholder="/images/avatar.jpg" className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">一句话简介</label>
                  <input type="text" value={heroSubtitle} onChange={(e) => setHeroSubtitle(e.target.value)} placeholder="全栈开发者 / 独立开发者" className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">封面图 URL</label>
                <input type="text" value={coverImage} onChange={(e) => setCoverImage(e.target.value)} placeholder="/images/brand/about-workbench.webp" className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all" />
              </div>
              {/* 实时预览 */}
              <div className="flex items-center gap-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg p-3 text-sm">
                {avatarUrl && <img src={avatarUrl} alt="" className="w-10 h-10 rounded-full object-cover" />}
                <div>
                  <span className="text-zinc-500 dark:text-zinc-400">{eyebrow}</span>
                  {title && <span className="ml-2 font-semibold text-zinc-900 dark:text-white">{title}</span>}
                  {heroSubtitle && <span className="ml-2 text-zinc-500 dark:text-zinc-400">— {heroSubtitle}</span>}
                </div>
              </div>
            </div>
          </div>

          {/* ===== 信息卡片 ===== */}
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">信息卡片</h2>
            <div className="space-y-3">
              {infoCards.map((card, index) => (
                <div key={index} className="flex items-center gap-3">
                  <input type="text" value={card.label} onChange={(e) => updateInfoCard(index, 'label', e.target.value)} placeholder="标签（如：职位）" className="flex-1 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm" />
                  <input type="text" value={card.value} onChange={(e) => updateInfoCard(index, 'value', e.target.value)} placeholder="值（如：全栈开发者）" className="flex-1 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm" />
                  <button type="button" onClick={() => removeInfoCard(index)} className="text-red-500 hover:text-red-700 text-lg leading-none" title="删除">✕</button>
                </div>
              ))}
              <button type="button" onClick={addInfoCard} className="text-sm text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors">
                + 添加卡片
              </button>
            </div>
          </div>

          {/* ===== 技术栈 ===== */}
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">技术栈标签</h2>
            <TagInput tags={techStack} onChange={setTechStack} />
          </div>

          {/* ===== 联系方式 ===== */}
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">联系方式</h2>
            <div className="space-y-3">
              {contacts.map((contact, index) => (
                <div key={index} className="flex items-center gap-3">
                  <select value={contact.platform} onChange={(e) => updateContact(index, 'platform', e.target.value)} className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm">
                    {CONTACT_PLATFORMS.map((p) => (
                      <option key={p.value} value={p.value}>{p.label}</option>
                    ))}
                  </select>
                  {contact.platform === 'custom' && (
                    <input type="text" value={contact.name || ''} onChange={(e) => updateContact(index, 'name', e.target.value)} placeholder="自定义名称" className="w-28 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm" />
                  )}
                  <input type="text" value={contact.url} onChange={(e) => updateContact(index, 'url', e.target.value)} placeholder={contact.platform === 'email' ? '邮箱地址' : 'URL'} className="flex-1 border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all text-sm" />
                  <button type="button" onClick={() => removeContact(index)} className="text-red-500 hover:text-red-700 text-lg leading-none" title="删除">✕</button>
                </div>
              ))}
              <button type="button" onClick={addContact} className="text-sm text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors">
                + 添加联系方式
              </button>
            </div>
          </div>

          {/* ===== 旧 Markdown 正文 ===== */}
          <div className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">正文内容（可选）</h2>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">格式</label>
              <select value={contentType} onChange={(e) => setContentType(e.target.value)} className="border border-zinc-300 dark:border-zinc-700 rounded-lg px-2 py-1 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-xs focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all">
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
            </div>
            {contentType === 'markdown' && (
              <div className="mb-2 flex gap-2">
                <button type="button" onClick={() => setPreview(false)} className={`px-3 py-1 text-xs rounded-md transition-colors ${!preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}>编辑</button>
                <button type="button" onClick={() => setPreview(true)} className={`px-3 py-1 text-xs rounded-md transition-colors ${preview ? 'bg-accent text-white' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}>预览</button>
              </div>
            )}
            {contentType === 'markdown' && preview ? (
              <div className="border border-zinc-300 dark:border-zinc-700 rounded-lg p-4 bg-white dark:bg-zinc-900 min-h-[160px] prose dark:prose-invert max-w-none">
                <ArticleContent content={content} />
              </div>
            ) : (
              <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={6} className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all font-mono text-sm" placeholder="输入 Markdown 内容..." />
            )}
          </div>

          {/* ===== 保存 ===== */}
          <div className="flex items-center gap-3">
            <motion.button type="submit" disabled={saving} whileTap={{ scale: saving ? 1 : 0.98 }} className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm">
              {saving ? '保存中...' : '保存'}
            </motion.button>
            <a href="/about" target="_blank" rel="noopener noreferrer" className="text-sm text-zinc-500 dark:text-zinc-400 hover:text-accent dark:hover:text-accent-dark transition-colors">
              前台预览 →
            </a>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
