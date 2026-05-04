interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Frosted glass panel — semi-transparent background with blur and subtle border.
 */
export default function GlassPanel({ children, className = '' }: GlassPanelProps) {
  return (
    <div
      className={`rounded-2xl border border-white/20 bg-white/60 shadow-[0_8px_32px_rgba(37,99,235,0.08)] backdrop-blur-xl ${className}`}
    >
      {children}
    </div>
  );
}
