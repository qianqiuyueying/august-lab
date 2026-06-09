"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const ADMIN_NAV = [
  { href: "/admin", label: "仪表盘" },
  { href: "/admin/articles", label: "文章管理" },
  { href: "/admin/products", label: "产品管理" },
  { href: "/admin/about", label: "关于页" },
  { href: "/admin/mascot", label: "看板娘" },
];

export function AdminSidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  };

  return (
    <aside className="admin-sidebar" id="adminSidebar">
      <div className="admin-sidebar__header">
        <span className="admin-sidebar__brand">管理后台</span>
      </div>

      <nav className="admin-nav">
        {ADMIN_NAV.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`admin-nav__item${isActive(href) ? " admin-nav__item--active" : ""}`}
          >
            <span className="admin-nav__label">{label}</span>
          </Link>
        ))}
      </nav>

      <div className="admin-sidebar__footer">
        <Link href="/" className="admin-nav__item">
          <span className="admin-nav__label">← 返回首页</span>
        </Link>
      </div>
    </aside>
  );
}
