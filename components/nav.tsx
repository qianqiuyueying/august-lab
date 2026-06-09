"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { href: "/", label: "首页" },
  { href: "/blog", label: "笔记" },
  { href: "/products", label: "作品" },
  { href: "/about", label: "关于" },
];

export function Nav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <nav className="nav-v2 nav-v2--solid">
      <Link href="/" className="nav-v2__brand">Atelier</Link>
      <div className="nav-v2__links">
        {NAV_LINKS.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`nav-v2__link${isActive(href) ? " active" : ""}`}
          >
            {label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
