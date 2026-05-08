interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  accentLine?: boolean;
}

export default function GlassPanel({ children, className = '', accentLine = false }: GlassPanelProps) {
  return (
    <div className={`glass-panel ${className}`}>
      {accentLine && (
        <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-accent-start to-accent-mid" />
      )}
      {children}
    </div>
  );
}
