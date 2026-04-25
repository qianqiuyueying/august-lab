import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getSetting, updateSetting } from '../../api/settings';

export default function AdminSettings() {
  const [aboutBio, setAboutBio] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    getSetting('about_bio')
      .then((d) => setAboutBio(d.value))
      .catch(() => setAboutBio(''))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateSetting('about_bio', aboutBio);
      setSuccess('已保存');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">站点设置</h1>

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

      {loading ? (
        <div className="animate-pulse h-64 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">关于我简介</h2>
          <textarea
            value={aboutBio}
            onChange={(e) => setAboutBio(e.target.value)}
            rows={12}
            className="w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all font-mono text-sm"
            placeholder="输入简介内容..."
          />
          <div className="mt-4 flex items-center gap-3">
            <motion.button
              onClick={handleSave}
              disabled={saving}
              whileTap={{ scale: saving ? 1 : 0.98 }}
              className="bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
            >
              {saving ? '保存中...' : '保存'}
            </motion.button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
