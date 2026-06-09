"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";

interface RecentArticle { id: number; slug: string; title: string; tags: string[]; published: boolean; createdAt: string; }
interface TagItem { label: string; count: number; }

export function DashboardClient({
  articleCount, productCount, publishedArticles, draftArticles, tagCount,
  recentArticles, tagChart: initialChart,
}: {
  articleCount: number; productCount: number; publishedArticles: number;
  draftArticles: number; tagCount: number;
  recentArticles: RecentArticle[];
  tagChart: TagItem[];
}) {
  const [chartData, setChartData] = useState<TagItem[]>([]);
  const [chartMax, setChartMax] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshLabel, setRefreshLabel] = useState(" 上次更新：刚刚");
  const chartRef = useRef<HTMLDivElement>(null);
  const animated = useRef(false);

  const barColors = ["tag-chart__bar--s1", "tag-chart__bar--s2", "tag-chart__bar--s3", "tag-chart__bar--s4", "tag-chart__bar--s5", ""];

  /* Init chart data from props */
  useEffect(() => {
    setChartData(initialChart);
    setChartMax(Math.max(...initialChart.map((d) => d.count), 1));
  }, [initialChart]);

  /* Animate chart on mount */
  useEffect(() => {
    if (animated.current || chartData.length === 0) return;
    const el = chartRef.current;
    if (!el) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            setChartData([...chartData]); // trigger re-render for animation
          }, 100);
          observer.disconnect();
          animated.current = true;
        }
      });
    }, { threshold: 0.3 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [chartData]);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    const s = chartData.map(() => ({ count: 0 }));
    setChartData(s.map((_, i) => ({ label: chartData[i].label, count: 0 })));
    setTimeout(() => {
      const updated = chartData.map(() => ({ label: "", count: 1 + Math.floor(Math.random() * 12) })).map((d, i) => ({
        label: chartData[i].label,
        count: d.count,
      }));
      setChartData(updated);
      setChartMax(Math.max(...updated.map((d) => d.count), 1));
      const now = new Date();
      setRefreshLabel(` 上次更新：${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`);
      setRefreshing(false);
    }, 1200);
  }, [chartData]);

  return (
    <>
      <div className="admin-page-header">
        <div>
          <div className="admin-page-header__label">Console</div>
          <h1 className="admin-page-header__title">仪表盘</h1>
          <p className="admin-page-header__desc">
            站点概览与快捷操作
            <span style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>{refreshLabel}</span>
          </p>
        </div>
        <div className="admin-page-header__actions">
          <button className={`dashboard-refresh-btn${refreshing ? " dashboard-refresh-btn--loading" : ""}`} onClick={handleRefresh}>
            <span className="dashboard-refresh-btn__icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </span>
            刷新
          </button>
        </div>
      </div>

      <div className="admin-stats">
        <Link href="/admin/articles" className="admin-stat-card">
          <div className="admin-stat-card__label admin-stat-card__label--blue">文章</div>
          <div className="admin-stat-card__value">{articleCount}</div>
          <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginTop: 4 }}>{publishedArticles} 已发布 · {draftArticles} 草稿</div>
        </Link>
        <Link href="/admin/products" className="admin-stat-card">
          <div className="admin-stat-card__label admin-stat-card__label--green">产品</div>
          <div className="admin-stat-card__value">{productCount}</div>
          <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginTop: 4 }}>主题 &amp; 模板</div>
        </Link>
        <div className="admin-stat-card">
          <div className="admin-stat-card__label admin-stat-card__label--amber">页面</div>
          <div className="admin-stat-card__value">1</div>
          <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginTop: 4 }}>静态页面</div>
        </div>
        <div className="admin-stat-card">
          <div className="admin-stat-card__label admin-stat-card__label--zinc">标签</div>
          <div className="admin-stat-card__value">{tagCount}</div>
          <div style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)", marginTop: 4 }}>分类标签</div>
        </div>
      </div>

      <div className="admin-grid-2">
        <div className="admin-panel">
          <h2 className="admin-panel__title">标签分布</h2>
          <div className="admin-panel__body">
            <div className="tag-chart" ref={chartRef}>
              {chartData.map((d, i) => (
                <div key={d.label} className="tag-chart__column">
                  <span className="tag-chart__count">{d.count}</span>
                  <div className={`tag-chart__bar ${barColors[i] || ""}`} style={{ height: `${Math.max((d.count / (chartMax || 1)) * 100, 5)}%` }}></div>
                  <span className="tag-chart__label">{d.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="admin-panel">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--sp-lg) var(--sp-lg) 0" }}>
            <h2 className="admin-panel__title" style={{ padding: 0, margin: 0 }}>近期文章</h2>
            <Link href="/admin/articles" className="admin-action-link">查看全部</Link>
          </div>
          <div className="admin-panel__body">
            {recentArticles.map((a) => (
              <div key={a.id} className="recent-item">
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="recent-item__title">{a.title}</div>
                  <div className="recent-item__meta">
                    <span className={`admin-badge ${a.published ? "admin-badge--published" : "admin-badge--draft"}`}>{a.published ? "已发布" : "草稿"}</span>
                    <span style={{ fontSize: "var(--fs-meta)", color: "var(--c-fg-dim)" }}>{a.createdAt.slice(5, 10)}</span>
                  </div>
                  {a.tags && a.tags.length > 0 && (
                    <div className="recent-item__tags">
                      {a.tags.map((t) => <span key={t} className="recent-item__tag">{t}</span>)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="admin-panel">
        <h2 className="admin-panel__title">系统状态</h2>
        <div className="admin-panel__body">
          <div className="sys-status-grid">
            <div className="admin-status-indicator"><span className="admin-status-indicator__dot admin-status-indicator__dot--blue"></span><span className="admin-status-indicator__label">数据库</span><span className="admin-status-indicator__value">PostgreSQL</span></div>
            <div className="admin-status-indicator"><span className="admin-status-indicator__dot admin-status-indicator__dot--green"></span><span className="admin-status-indicator__label">用户数</span><span className="admin-status-indicator__value">1</span></div>
            <div className="admin-status-indicator"><span className="admin-status-indicator__dot admin-status-indicator__dot--green"></span><span className="admin-status-indicator__label">API 状态</span><span className="admin-status-indicator__value" style={{ color: "oklch(0.65 0.12 160)" }}>运行中</span></div>
          </div>
        </div>
      </div>

      <div className="admin-panel">
        <h2 className="admin-panel__title">快捷操作</h2>
        <div className="admin-panel__body">
          <div className="admin-quick-actions">
            <Link href="/admin/articles/new" className="admin-btn admin-btn--primary">上传文章</Link>
            <Link href="/admin/products/new" className="admin-btn">创建产品</Link>
            <Link href="/admin/about" className="admin-btn">编辑关于页</Link>
            <Link href="/admin/mascot" className="admin-btn">配置看板娘</Link>
          </div>
        </div>
      </div>
    </>
  );
}
