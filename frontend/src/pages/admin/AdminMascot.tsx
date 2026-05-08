import { useState, useEffect, type FormEvent } from 'react';
import { motion } from 'framer-motion';
import { getAdminMascotSettings, updateAdminMascotSettings } from '../../api/mascot';
import { AdminErrorBanner } from '../../components/admin/AdminPrimitives';
import type { MascotSettingsAdmin } from '../../types';

const EMPTY_FORM: MascotSettingsAdmin = {
  id: 0,
  persona: '',
  api_key: '',
  api_base_url: '',
  model: '',
  temperature: 0.7,
  max_tokens: 256,
  enabled: true,
  mascot_visible: true,
  mascot_scale: 1.0,
  mascot_position_x: null,
  mascot_position_y: null,
  show_on_mobile: false,
  greeting_enabled: true,
  greeting_delay_seconds: 3,
  random_action_interval: 60,
  context_aware: true,
  drag_enabled: true,
};

export default function AdminMascot() {
  const [form, setForm] = useState<MascotSettingsAdmin>(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await getAdminMascotSettings();
      setForm(data);
    } catch {
      setError('加载设置失败');
    } finally {
      setLoading(false);
    }
  };

  const updateField = <K extends keyof MascotSettingsAdmin>(
    key: K,
    value: MascotSettingsAdmin[K],
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSaved('');
    try {
      const updated = await updateAdminMascotSettings(form);
      setForm(updated);
      setSaved('设置已保存');
      setTimeout(() => setSaved(''), 2000);
    } catch (err) {
      setError(
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || '保存失败',
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 w-48 rounded bg-zinc-200 dark:bg-zinc-800" />
        <div className="h-64 rounded-xl bg-zinc-200 dark:bg-zinc-800" />
      </div>
    );
  }

  const sectionClass =
    'bg-white dark:bg-zinc-900/50 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 p-6 shadow-sm';
  const sectionTitleClass =
    'text-lg font-semibold text-zinc-900 dark:text-white mb-4';
  const labelClass =
    'block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1';
  const inputClass =
    'w-full border border-zinc-300 dark:border-zinc-700 rounded-lg px-3 py-2.5 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
        看板娘设置
      </h1>

      <AdminErrorBanner message={error} />

      {saved && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-green-600 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg text-sm"
        >
          {saved}
        </motion.div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* ===== 左栏：主体设置 ===== */}
          <div className="lg:col-span-2 space-y-6">
            {/* Persona */}
            <div className={sectionClass}>
              <h2 className={sectionTitleClass}>人设（System Prompt）</h2>
              <div>
                <label className={labelClass}>角色提示词</label>
                <textarea
                  value={form.persona}
                  onChange={(e) => updateField('persona', e.target.value)}
                  rows={6}
                  className={inputClass}
                  placeholder="你是一只可爱的看板娘..."
                />
              </div>
            </div>

            {/* API 配置 */}
            <div className={sectionClass}>
              <h2 className={sectionTitleClass}>API 配置</h2>
              <div className="space-y-4">
                <div>
                  <label className={labelClass}>API Key</label>
                  <input
                    type="password"
                    value={form.api_key}
                    onChange={(e) => updateField('api_key', e.target.value)}
                    className={inputClass}
                    placeholder="sk-..."
                  />
                </div>
                <div>
                  <label className={labelClass}>Base URL</label>
                  <input
                    type="text"
                    value={form.api_base_url}
                    onChange={(e) =>
                      updateField('api_base_url', e.target.value)
                    }
                    className={inputClass}
                    placeholder="https://api.openai.com/v1"
                  />
                </div>
                <div>
                  <label className={labelClass}>Model</label>
                  <input
                    type="text"
                    value={form.model}
                    onChange={(e) => updateField('model', e.target.value)}
                    className={inputClass}
                    placeholder="gpt-4o-mini"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>
                      Temperature ({form.temperature})
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={form.temperature}
                      onChange={(e) =>
                        updateField('temperature', parseFloat(e.target.value))
                      }
                      className="w-full accent-accent"
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Max Tokens</label>
                    <input
                      type="number"
                      value={form.max_tokens}
                      onChange={(e) =>
                        updateField('max_tokens', parseInt(e.target.value) || 0)
                      }
                      className={inputClass}
                      min={1}
                      max={4096}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* 行为设置 */}
            <div className={sectionClass}>
              <h2 className={sectionTitleClass}>行为设置</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.greeting_enabled}
                      onChange={(e) =>
                        updateField('greeting_enabled', e.target.checked)
                      }
                      className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                    />
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      启用问候语
                    </span>
                  </label>
                  <div>
                    <label className={labelClass}>
                      问候延迟（秒）
                    </label>
                    <input
                      type="number"
                      value={form.greeting_delay_seconds}
                      onChange={(e) =>
                        updateField(
                          'greeting_delay_seconds',
                          parseInt(e.target.value) || 0,
                        )
                      }
                      className={inputClass}
                      min={0}
                      max={120}
                    />
                  </div>
                </div>
                <div>
                  <label className={labelClass}>
                    随机动作间隔（秒）
                  </label>
                  <input
                    type="number"
                    value={form.random_action_interval}
                    onChange={(e) =>
                      updateField(
                        'random_action_interval',
                        parseInt(e.target.value) || 0,
                      )
                    }
                    className={inputClass}
                    min={10}
                    max={3600}
                  />
                </div>
                <div className="flex flex-wrap gap-6">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.context_aware}
                      onChange={(e) =>
                        updateField('context_aware', e.target.checked)
                      }
                      className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                    />
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      上下文感知
                    </span>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.drag_enabled}
                      onChange={(e) =>
                        updateField('drag_enabled', e.target.checked)
                      }
                      className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                    />
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      允许拖拽
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* ===== 右栏：开关 & 外观 ===== */}
          <div className="space-y-6">
            {/* 开关 */}
            <div className={sectionClass}>
              <h2 className={sectionTitleClass}>开关</h2>
              <div className="space-y-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    启用看板娘
                  </span>
                  <input
                    type="checkbox"
                    checked={form.enabled}
                    onChange={(e) =>
                      updateField('enabled', e.target.checked)
                    }
                    className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                  />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    显示形象
                  </span>
                  <input
                    type="checkbox"
                    checked={form.mascot_visible}
                    onChange={(e) =>
                      updateField('mascot_visible', e.target.checked)
                    }
                    className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                  />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    移动端显示
                  </span>
                  <input
                    type="checkbox"
                    checked={form.show_on_mobile}
                    onChange={(e) =>
                      updateField('show_on_mobile', e.target.checked)
                    }
                    className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-accent focus:ring-accent/30"
                  />
                </label>
              </div>
            </div>

            {/* 外观 */}
            <div className={sectionClass}>
              <h2 className={sectionTitleClass}>外观</h2>
              <div className="space-y-4">
                <div>
                  <label className={labelClass}>
                    缩放比例 ({form.mascot_scale})
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="3"
                    step="0.1"
                    value={form.mascot_scale}
                    onChange={(e) =>
                      updateField('mascot_scale', parseFloat(e.target.value))
                    }
                    className="w-full accent-accent"
                  />
                </div>
              </div>
            </div>

            {/* 保存按钮 */}
            <motion.button
              type="submit"
              disabled={saving}
              whileTap={{ scale: saving ? 1 : 0.98 }}
              className="w-full bg-accent text-white px-4 py-2.5 rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors text-sm"
            >
              {saving ? '保存中...' : '保存设置'}
            </motion.button>
          </div>
        </div>
      </form>
    </motion.div>
  );
}
