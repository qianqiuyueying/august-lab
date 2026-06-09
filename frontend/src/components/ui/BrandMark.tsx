interface BrandMarkProps {
  className?: string;
  compact?: boolean;
}

export default function BrandMark({ compact = false }: BrandMarkProps) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${compact ? '' : 'min-w-0'}`}>
      <div
        className="flex h-9 w-9 items-center justify-center rounded-lg text-lg font-black text-background shrink-0"
        style={{ background: 'linear-gradient(135deg, #c8843c, #3ba5c4)' }}
      >
        A
      </div>
      {!compact && (
        <span className="min-w-0">
          <span className="block text-[15px] font-extrabold leading-none text-text-primary">
            August&apos;s Lab
          </span>
          <span className="mt-1 block text-[11px] font-semibold leading-none text-text-muted">
            Notes and small experiments
          </span>
        </span>
      )}
    </span>
  );
}
