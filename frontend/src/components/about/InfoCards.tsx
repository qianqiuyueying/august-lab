interface InfoCardItem {
  label: string;
  value: string;
}

interface InfoCardsProps {
  items: InfoCardItem[];
}

export default function InfoCards({ items }: InfoCardsProps) {
  if (!items?.length) return null;

  return (
    <section className="grid gap-4 grid-cols-2 md:grid-cols-4">
      {items.map((item, index) => (
        <div
          key={index}
          className="glass-panel p-5 text-center"
        >
          <p className="text-xs uppercase tracking-wider text-text-muted mb-1">
            {item.label}
          </p>
          <p className="text-lg font-semibold text-paper">
            {item.value}
          </p>
        </div>
      ))}
    </section>
  );
}
