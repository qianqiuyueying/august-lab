"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const IconDashboard = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>;
const IconArticle = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5A2.5 2.5 0 0 1 4 19.5z"/><line x1="8" y1="9" x2="16" y2="9"/><line x1="8" y1="13" x2="14" y2="13"/><line x1="8" y1="17" x2="12" y2="17"/></svg>;
const IconProduct = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" y1="22" x2="12" y2="12"/></svg>;
const IconAbout = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>;
const IconMascot = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="14" r="3"/><path d="M12 2a4 4 0 0 1 4 4c0 1.1-.7 2.6-1.5 3.5M9 10c-2 0-4 1-4 3s1 3 2 3.5M15 10c2 0 4 1 4 3s-1 3-2 3.5"/></svg>;
const IconHome = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
const IconLogout = <svg className="admin-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>;

const navItems = [
  { href: "/admin", label: "仪表盘", icon: IconDashboard },
  { href: "/admin/articles", label: "文章管理", icon: IconArticle },
  { href: "/admin/products", label: "产品管理", icon: IconProduct },
  { href: "/admin/about", label: "关于页", icon: IconAbout },
  { href: "/admin/mascot", label: "看板娘", icon: IconMascot },
];

export function AdminSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [showLogout, setShowLogout] = useState(false);

  useEffect(() => {
    const s = localStorage.getItem("atelier-admin-sidebar");
    if (s === "collapsed") setCollapsed(true);
  }, []);

  const toggle = useCallback(() => {
    setCollapsed((p) => {
      const n = !p;
      localStorage.setItem("atelier-admin-sidebar", n ? "collapsed" : "open");
      return n;
    });
  }, []);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  const isActive = (href: string) =>
    href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);

  return (
    <>
      <aside className={`admin-sidebar ${collapsed ? "admin-sidebar--closed" : "admin-sidebar--open"}`}>
        <div className="admin-sidebar__header">
          <span className={`admin-sidebar__brand${collapsed ? " admin-sidebar__brand--hidden" : ""}`}>管理后台</span>
          <button className="admin-sidebar__toggle" title={collapsed ? "展开侧边栏" : "收起侧边栏"} onClick={toggle}>
            {collapsed
              ? <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              : <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            }
          </button>
        </div>
        <nav className="admin-nav">
          {navItems.map(({ href, label, icon }) => (
            <Link key={href} href={href} className={`admin-nav__item${isActive(href) ? " admin-nav__item--active" : ""}`}>
              {icon}
              <span className={`admin-nav__label${collapsed ? " admin-nav__label--hidden" : ""}`}>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="admin-sidebar__footer">
          <Link href="/" className="admin-nav__item">
            {IconHome}
            <span className={`admin-nav__label${collapsed ? " admin-nav__label--hidden" : ""}`}>返回首页</span>
          </Link>
          <button className="admin-nav__item" onClick={() => setShowLogout(true)}>
            {IconLogout}
            <span className={`admin-nav__label${collapsed ? " admin-nav__label--hidden" : ""}`}>退出登录</span>
          </button>
        </div>
      </aside>

      {/* 退出弹窗 */}
      <div className={`admin-modal-overlay${showLogout ? " admin-modal-overlay--open" : ""}`} onClick={(e) => { if (e.target === e.currentTarget) setShowLogout(false); }}>
        <div className="admin-modal">
          <h3 className="admin-modal__title">退出登录</h3>
          <p className="admin-modal__desc">确定要退出管理后台吗？</p>
          <div className="admin-modal__actions">
            <button className="admin-btn" onClick={() => setShowLogout(false)}>取消</button>
            <button className="admin-btn admin-btn--danger" onClick={handleLogout}>退出</button>
          </div>
        </div>
      </div>
    </>
  );
}
