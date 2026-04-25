interface BrandMarkProps {
  className?: string;
  compact?: boolean;
}

export default function BrandMark({ className = 'h-9 w-9', compact = false }: BrandMarkProps) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${compact ? '' : 'min-w-0'}`}>
      <svg className={className} viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <rect x="4" y="4" width="40" height="40" rx="8" className="fill-ink dark:fill-text-primary-dark" />
        <path
          d="M19.5 12.5h9l-2.7 11.3c-.2.9-.1 1.8.4 2.6l5.5 9.4H16.3l5.5-9.4c.5-.8.6-1.7.4-2.6L19.5 12.5Z"
          className="fill-paper dark:fill-background-dark"
        />
        <path d="M19 29.5h10" className="stroke-accent dark:stroke-accent-mid" strokeWidth="2" strokeLinecap="round" />
        <circle cx="18" cy="18" r="1.7" className="fill-clay" />
        <circle cx="30" cy="15" r="1.4" className="fill-accent" />
        <circle cx="32" cy="22" r="1.1" className="fill-blueprint" />
      </svg>
      {!compact && (
        <span className="min-w-0">
          <span className="block text-[15px] font-extrabold leading-none text-text-primary dark:text-text-primary-dark">
            August&apos;s Lab
          </span>
          <span className="mt-1 block text-[11px] font-semibold leading-none text-text-muted dark:text-text-muted-dark">
            Notes and small experiments
          </span>
        </span>
      )}
    </span>
  );
}
