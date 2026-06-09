import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticles } from '../hooks/useArticles';
import { useTags } from '../hooks/useTags';
import ArticleCard from '../components/articles/ArticleCard';
import TagList from '../components/tags/TagList';
import SearchBar from '../components/search/SearchBar';
import { Skeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import GlassPanel from '../components/ui/GlassPanel';
import SectionNumber from '../components/ui/SectionNumber';

export default function BlogPage() {
  const [searchParams] = useSearchParams();
  const tag = searchParams.get('tag') || undefined;
  const search = searchParams.get('search') || undefined;
  const filterKey = `${tag ?? ''}${search ?? ''}`;
  const [pageState, setPageState] = useState({ key: filterKey, page: 1 });
  const page = pageState.key === filterKey ? pageState.page : 1;

  const { data, loading, error } = useArticles(page, 10, tag, search);
  const { data: tags, loading: tagsLoading } = useTags();

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;
  const title = tag ? `#${tag}` : search ? `搜索：${search}` : '实验笔记目录';

  return (
    <div className="mx-auto max-w-7xl">
      {/* ===== Page header ===== */}
      <motion.section
        className="relative mb-10 overflow-hidden rounded-2xl"
        style={{ minHeight: '40vh' }}
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.25, 1, 0.5, 1] }}>
        <div className="absolute inset-0 z-0" style={{ margin: '-5%' }}>
          <img
            src="/images/preview/s04_darkroom_bg_00001_.webp"
            alt=""
            loading="lazy"
            className="h-full w-full object-cover"
            style={{ transform: 'scale(1.1)' }}
          />
        </div>
        <div className="absolute inset-0 z-1 pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(10,15,26,.5) 100%)' }}
        />

        {/* Foreground */}
        <div className="a-float1 absolute z-2 pointer-events-none hidden sm:block" style={{ width: 'clamp(140px,18vw,320px)', top: '22%', left: '2%' }}>
          <img src="/images/preview/s04_film_00001_.webp" alt="" className="w-full h-auto" />
        </div>
        <div className="a-float2 absolute z-2 pointer-events-none hidden sm:block" style={{ width: 'clamp(50px,7vw,120px)', top: '12%', right: '7%' }}>
          <img src="/images/preview/s04_tweezers_00001_.webp" alt="" className="w-full h-auto" />
        </div>

        {/* Content */}
        <div className="relative z-10 text-center py-[clamp(60px,12vh,100px)]">
          <p className="text-xs font-extrabold text-accent tracking-wider uppercase mb-2">Notebook</p>
          <h1 className="text-paper mb-3">{title}</h1>
          <p className="text-text-muted max-w-md mx-auto text-sm sm:text-base">技术探索的记录，慢慢成形的想法</p>

          <div className="max-w-md mx-auto mt-5">
            <SearchBar />
          </div>

          {data && !tag && !search && (
            <span className="lab-chip mt-4 inline-block">{data.total} 篇公开笔记</span>
          )}
        </div>
      </motion.section>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_18rem]">
        <div className="min-w-0">
          {/* Tag cloud */}
          <div className="mb-6">
            <GlassPanel className="p-4">
              <div className="flex flex-wrap gap-2 justify-center">
                {tagsLoading ? (
                  <span className="text-xs text-text-muted">加载标签中...</span>
                ) : tags?.length ? (
                  tags.map((t) => (
                    <a
                      key={t.id}
                      href={`/blog?tag=${encodeURIComponent(t.name)}`}
                      onClick={(e) => {
                        e.preventDefault();
                        window.history.pushState(null, '', `/blog?tag=${encodeURIComponent(t.name)}`);
                        window.dispatchEvent(new PopStateEvent('popstate'));
                      }}
                      className="text-xs px-3 py-1.5 rounded-full border border-blueprint/20 bg-blueprint/10 text-blueprint font-bold transition-all hover:bg-blueprint/25 hover:text-paper hover:-translate-y-px no-underline"
                    >
                      {t.name}
                    </a>
                  ))
                ) : null}
              </div>
            </GlassPanel>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-6 rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger"
            >
              {error}
            </motion.div>
          )}

          {loading ? (
            <div className="space-y-5">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-44" />
              ))}
            </div>
          ) : data?.items.length ? (
            <div className="space-y-4">
              {data.items.map((article, i) => (
                <motion.div
                  key={article.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
                >
                  <ArticleCard article={article} />
                </motion.div>
              ))}
            </div>
          ) : (
            <EmptyState title="没有找到文章" />
          )}

          {data && data.total > data.page_size && (
            <div className="mt-10 flex items-center justify-center gap-4">
              <button
                onClick={() => setPageState({ key: filterKey, page: Math.max(1, page - 1) })}
                disabled={page === 1}
                className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-40"
              >
                上一页
              </button>
              <span className="font-mono text-sm font-bold text-text-muted">
                {data.page} / {totalPages}
              </span>
              <button
                onClick={() => setPageState({ key: filterKey, page: page + 1 })}
                disabled={page * data.page_size >= data.total}
                className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-40"
              >
                下一页
              </button>
            </div>
          )}
        </div>

        <aside className="lg:pt-4">
          <div className="sticky top-24 space-y-6">
            <GlassPanel className="p-5" accentLine>
              <SectionNumber number="" label="主题标签" />
              <div className="mt-4">
                <TagList tags={tags} loading={tagsLoading} />
              </div>
            </GlassPanel>
          </div>
        </aside>
      </div>
    </div>
  );
}
