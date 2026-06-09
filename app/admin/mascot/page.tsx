import { StateCard } from "@/components/state-card";

export default function MascotPage() {
  return (
    <div>
      <h1 className="admin-page-title">看板娘</h1>
      <StateCard type="empty" title="功能开发中" desc="看板娘管理功能即将上线。" minHeight="300px" />
    </div>
  );
}
