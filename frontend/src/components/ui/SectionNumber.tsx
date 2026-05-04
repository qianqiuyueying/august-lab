interface SectionNumberProps {
  number: string; // e.g., "001"
  label: string;  // e.g., "首页"
}

export default function SectionNumber({ number, label }: SectionNumberProps) {
  return (
    <div className="flex items-baseline gap-3">
      <span className="lab-number" aria-hidden="true">
        {number}
      </span>
      <span className="text-lg font-semibold text-text-muted dark:text-text-muted-dark">
        {label}
      </span>
    </div>
  );
}
