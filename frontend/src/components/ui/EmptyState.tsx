interface EmptyStateProps {
  title: string;
  description?: string;
}

export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="paper-panel mx-auto max-w-xl px-6 py-12 text-center">
      <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-lg border border-border bg-paper-soft text-accent dark:border-border-dark dark:bg-surface-dark">
        <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
          <path d="M5 4h14v16H5z" />
          <path d="M8 8h8M8 12h8M8 16h5" />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">{title}</h2>
      {description && <p className="mt-2 text-sm text-text-secondary dark:text-text-secondary-dark">{description}</p>}
    </div>
  );
}
