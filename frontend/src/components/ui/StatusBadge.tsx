interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const published = status === 'published';

  return (
    <span className={`lab-chip ${published ? '' : 'border-border bg-paper-soft text-text-muted dark:border-border-dark dark:bg-surface-dark dark:text-text-muted-dark'}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${published ? 'bg-accent' : 'bg-text-muted'}`} />
      {published ? '已发布' : '进行中'}
    </span>
  );
}
