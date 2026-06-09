interface StatusDotProps {
  status: string;
  showLabel?: boolean;
}

const statusMap: Record<string, { className: string; label: string }> = {
  published: { className: 'status-dot--active', label: '已发布' },
  active: { className: 'status-dot--active', label: '运行中' },
  testing: { className: 'status-dot--testing', label: '测试中' },
  beta: { className: 'status-dot--testing', label: 'Beta' },
  draft: { className: 'status-dot--archived', label: '草稿' },
  archived: { className: 'status-dot--archived', label: '归档' },
};

export default function StatusDot({ status, showLabel = true }: StatusDotProps) {
  const config = statusMap[status] ?? statusMap.archived;
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`status-dot ${config.className}`} />
      {showLabel && (
        <span className="text-xs font-bold text-text-muted">
          {config.label}
        </span>
      )}
    </span>
  );
}
