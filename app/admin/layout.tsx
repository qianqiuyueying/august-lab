import { AdminSidebar } from "@/components/admin/sidebar";
import "./admin.css";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="admin-body">
      <div className="admin-layout">
        <AdminSidebar />
        <main className="admin-main">
          <div className="admin-main__inner">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
