interface TickDividerProps {
  className?: string;
}

export default function TickDivider({ className = '' }: TickDividerProps) {
  return (
    <hr className={`tick-divider ${className}`} />
  );
}
