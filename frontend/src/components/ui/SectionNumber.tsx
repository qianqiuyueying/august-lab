interface SectionNumberProps {
  number: string;
  label: string;
}

export default function SectionNumber({ number, label }: SectionNumberProps) {
  return (
    <div className="flex items-center gap-2.5 mb-3">
      <span className="font-mono text-xs font-extrabold text-accent tracking-wider">{number}</span>
      <span className="text-xs font-bold text-accent/60">{label}</span>
    </div>
  );
}
