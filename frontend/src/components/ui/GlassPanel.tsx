interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  accentLine?: boolean; // when true, add gradient top accent line
}

export default function GlassPanel({ children, className = '', accentLine = false }: GlassPanelProps) {
  return (
    <div
      className={`relative rounded-xl border border-white/20 bg-white/60 shadow-[0_8px_32px_rgba(37,99,235,0.08)] backdrop-blur-xl overflow-hidden ${className}`}
    >
      {accentLine && (
        <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-accent-start to-accent-mid" />
      )}
      {children}
    </div>
  );
}
