interface TagsProps {
  tags: string[];
  active?: string;
  size?: "sm" | "md";
}

export function Tags({ tags, active, size = "sm" }: TagsProps) {
  if (!tags || tags.length === 0) return null;

  return (
    <div style={{ display: "flex", gap: "var(--sp-xs)", flexWrap: "wrap" }}>
      {tags.map((tag) => (
        <span
          key={tag}
          className={`tag${active === tag ? " tag--active" : ""}`}
          style={size === "sm" ? { fontSize: "var(--fs-meta)" } : { fontSize: "var(--fs-small)" }}
        >
          {tag}
        </span>
      ))}
    </div>
  );
}
