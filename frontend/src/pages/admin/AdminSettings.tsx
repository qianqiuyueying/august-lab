export default function AdminSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">站点设置</h1>
      <div className="text-zinc-500 dark:text-zinc-400 text-sm">
        关于页配置已迁移至 <a href="/admin/pages" className="text-accent hover:underline">关于页</a>。
      </div>
    </div>
  );
}
