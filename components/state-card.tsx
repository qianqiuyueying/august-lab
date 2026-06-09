import Link from "next/link";

interface StateCardProps {
  type: "loading" | "error" | "empty";
  title?: string;
  desc?: string;
  retryHref?: string;
  retryLabel?: string;
  minHeight?: string;
}

export function StateCard({ type, title, desc, retryHref, retryLabel, minHeight = "100vh" }: StateCardProps) {
  const defaults = {
    loading: { icon: "⟳", title: "加载中", desc: "正在获取内容…" },
    error:   { icon: "!", title: "加载失败", desc: "无法连接到服务器，请稍后重试。" },
    empty:   { icon: "—", title: "暂无内容", desc: "还没有发布任何内容，敬请期待。" },
  } as const;

  const d = defaults[type];

  return (
    <div className="state-card" style={{ minHeight }}>
      <div className="state-card__icon" style={type === "loading" ? { animation: "pulse 1.5s ease-in-out infinite" } : undefined}>
        {d.icon}
      </div>
      <div className="state-card__title">{title ?? d.title}</div>
      <p className="state-card__desc">{desc ?? d.desc}</p>
      {retryHref && (
        <Link href={retryHref} className="btn" style={{ marginTop: "var(--sp-lg)" }}>
          {retryLabel ?? "重试"}
        </Link>
      )}
    </div>
  );
}
