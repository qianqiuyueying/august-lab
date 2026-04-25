import type { ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

export interface AdminStat {
  label: string;
  value: number | string;
  tone?: 'blue' | 'green' | 'amber' | 'zinc';
}

interface AdminPageHeaderProps {
  title: string;
  description: string;
  actionLabel: string;
  secondaryActionLabel?: string;
  onAction: () => void;
  onSecondaryAction?: () => void;
}

interface AdminToolbarProps {
  search: string;
  searchPlaceholder: string;
  status: string;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  children?: ReactNode;
}

interface AdminDrawerProps {
  open: boolean;
  title: string;
  description?: string;
  children: ReactNode;
  onClose: () => void;
}

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  loading?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

const statToneClass: Record<NonNullable<AdminStat['tone']>, string> = {
  blue: 'bg-accent-subtle text-accent-hover dark:bg-accent-subtle-dark dark:text-blue-200',
  green: 'bg-success-subtle text-success dark:bg-success-subtle-dark dark:text-green-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  zinc: 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300',
};

export function AdminPageHeader({
  title,
  description,
  actionLabel,
  secondaryActionLabel,
  onAction,
  onSecondaryAction,
}: AdminPageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="section-label mb-2">Console</p>
        <h1 className="text-2xl font-bold leading-tight text-zinc-950 dark:text-white">{title}</h1>
        <p className="mt-1 text-sm text-text-muted dark:text-text-muted-dark">{description}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {secondaryActionLabel && onSecondaryAction && (
          <button type="button" onClick={onSecondaryAction} className="lab-button-secondary min-h-10 px-3 text-sm">
            {secondaryActionLabel}
          </button>
        )}
        <button type="button" onClick={onAction} className="lab-button min-h-10 px-3 text-sm">
          {actionLabel}
        </button>
      </div>
    </div>
  );
}

export function AdminStats({ stats }: { stats: AdminStat[] }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label} className="paper-panel p-4">
          <div className={`mb-3 inline-flex rounded-md px-2 py-1 text-xs font-bold ${statToneClass[stat.tone ?? 'zinc']}`}>
            {stat.label}
          </div>
          <div className="text-2xl font-bold leading-none text-zinc-950 dark:text-white">{stat.value}</div>
        </div>
      ))}
    </div>
  );
}

export function AdminToolbar({
  search,
  searchPlaceholder,
  status,
  onSearchChange,
  onStatusChange,
  children,
}: AdminToolbarProps) {
  return (
    <div className="paper-panel flex flex-col gap-3 p-3 md:flex-row">
      <label className="flex-1">
        <span className="sr-only">搜索</span>
        <input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={searchPlaceholder}
          className="focus-ring h-11 w-full rounded-lg border border-border bg-white px-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-accent dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
        />
      </label>
      <label className="md:w-44">
        <span className="sr-only">状态</span>
        <select
          value={status}
          onChange={(event) => onStatusChange(event.target.value)}
          className="focus-ring h-11 w-full rounded-lg border border-border bg-white px-3 text-sm text-zinc-900 outline-none transition-colors focus:border-accent dark:border-border-dark dark:bg-zinc-950 dark:text-zinc-100"
        >
          <option value="all">全部状态</option>
          <option value="published">已发布</option>
          <option value="draft">草稿</option>
        </select>
      </label>
      {children}
    </div>
  );
}

export function AdminStatusBadge({ status }: { status: string }) {
  const isPublished = status === 'published';
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${
        isPublished
          ? 'bg-success-subtle text-success dark:bg-success-subtle-dark dark:text-green-300'
          : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
      }`}
    >
      {isPublished ? '已发布' : '草稿'}
    </span>
  );
}

export function AdminPanel({ children }: { children: ReactNode }) {
  return <div className="paper-panel-strong overflow-hidden">{children}</div>;
}

export function AdminEmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center px-6 py-12 text-center">
      <h3 className="text-base font-bold text-zinc-900 dark:text-white">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-text-muted dark:text-text-muted-dark">{description}</p>
    </div>
  );
}

export function AdminErrorBanner({ message }: { message: string }) {
  if (!message) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg border border-danger/20 bg-danger-subtle px-4 py-3 text-sm font-medium text-danger dark:border-red-500/20 dark:bg-danger-subtle-dark dark:text-red-300"
    >
      {message}
    </motion.div>
  );
}

export function AdminDrawer({ open, title, description, children, onClose }: AdminDrawerProps) {
  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-zinc-950/30 backdrop-blur-[2px]"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 260 }}
            className="absolute right-0 top-0 flex h-full w-full max-w-3xl flex-col border-l border-border bg-background shadow-xl dark:border-border-dark dark:bg-background-dark"
          >
            <div className="flex items-start justify-between gap-4 border-b border-border bg-white px-5 py-4 dark:border-border-dark dark:bg-surface-dark">
              <div>
                <h2 className="text-lg font-bold text-zinc-950 dark:text-white">{title}</h2>
                {description && <p className="mt-1 text-sm text-text-muted dark:text-text-muted-dark">{description}</p>}
              </div>
              <button
                type="button"
                onClick={onClose}
                className="focus-ring rounded-lg px-2 py-1 text-sm font-bold text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-800 dark:hover:text-white"
                aria-label="关闭抽屉"
              >
                关闭
              </button>
            </div>
            <div className="flex-1 overflow-auto p-5">{children}</div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = '确认删除',
  loading = false,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-zinc-950/40"
            onClick={loading ? undefined : onCancel}
          />
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            className="relative w-full max-w-md rounded-lg border border-border bg-white p-5 shadow-xl dark:border-border-dark dark:bg-surface-dark"
          >
            <h2 className="text-lg font-bold text-zinc-950 dark:text-white">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-text-muted dark:text-text-muted-dark">{description}</p>
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" disabled={loading} onClick={onCancel} className="lab-button-secondary min-h-10 px-3 text-sm disabled:opacity-50">
                取消
              </button>
              <button
                type="button"
                disabled={loading}
                onClick={onConfirm}
                className="inline-flex min-h-10 items-center justify-center rounded-lg bg-danger px-3 text-sm font-bold text-white transition-colors hover:bg-red-700 disabled:opacity-50"
              >
                {loading ? '处理中...' : confirmLabel}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
