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
          className="paper-panel-strong p-5 rounded-xl border border-border bg-paper shadow-sm dark:border-border-dark dark:bg-surface-dark text-center"
        >
          <p className="text-xs uppercase tracking-wider text-text-muted dark:text-text-muted-dark mb-1">
            {item.label}
          </p>
          <p className="text-lg font-semibold text-text-primary dark:text-text-primary-dark">
            {item.value}
          </p>
        </div>
      ))}
    </section>
  );
}
