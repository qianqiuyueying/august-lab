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
import PageIntro from '../components/ui/PageIntro';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] as const } },
};

export default function BlogPage() {
  const [searchParams] = useSearchParams();
  const tag = searchParams.get('tag') || undefined;
  const search = searchParams.get('search') || undefined;
  const filterKey = `${tag ?? ''}\u0001${search ?? ''}`;
  const [pageState, setPageState] = useState({ key: filterKey, page: 1 });
  const page = pageState.key === filterKey ? pageState.page : 1;

  const { data, loading, error } = useArticles(page, 10, tag, search);
  const { data: tags, loading: tagsLoading } = useTags();

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;
  const title = tag ? `#${tag}` : search ? `搜索：${search}` : '实验笔记目录';

  return (
    <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_18rem]">
      <div className="min-w-0">
        <div className="mb-8">
          <PageIntro eyebrow="Notebook" title={title}>
            {data && !tag && !search && (
              <span className="lab-chip">{data.total} 篇公开笔记</span>
            )}
          </PageIntro>
        </div>

        <div className="mb-8 flex flex-col gap-4 border-y border-border py-5 dark:border-border-dark sm:flex-row sm:items-center sm:justify-between">
          <SearchBar />
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 rounded-lg border border-danger/20 bg-danger-subtle p-4 text-sm font-semibold text-danger dark:bg-danger-subtle-dark"
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
          <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-5">
            {data.items.map((article, index) => (
              <motion.div key={article.id} variants={itemVariants}>
                <ArticleCard article={article} variant={page === 1 && index === 0 ? 'featured' : 'default'} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <EmptyState title="没有找到文章" />
        )}

        {data && data.total > data.page_size && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <motion.button
              onClick={() => setPageState({ key: filterKey, page: Math.max(1, page - 1) })}
              disabled={page === 1}
              whileTap={{ scale: page === 1 ? 1 : 0.96 }}
              className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-45"
            >
              上一页
            </motion.button>
            <span className="text-sm font-bold text-text-muted dark:text-text-muted-dark">
              {data.page} / {totalPages}
            </span>
            <motion.button
              onClick={() => setPageState({ key: filterKey, page: page + 1 })}
              disabled={page * data.page_size >= data.total}
              whileTap={{ scale: page * data.page_size >= data.total ? 1 : 0.96 }}
              className="lab-button-secondary disabled:cursor-not-allowed disabled:opacity-45"
            >
              下一页
            </motion.button>
          </motion.div>
        )}
      </div>

      <aside className="lg:pt-8">
        <div className="sticky top-24 space-y-6">
          <div className="overflow-hidden rounded-lg border border-border bg-paper shadow-sm dark:border-border-dark dark:bg-surface-dark">
            <img
              src="/images/brand/blog-field-notes.png"
              alt=""
              aria-hidden="true"
              className="aspect-square w-full object-cover"
            />
          </div>
          <div>
            <p className="section-label mb-3">Topics</p>
            <h2 className="text-2xl font-extrabold text-text-primary dark:text-text-primary-dark">主题标签</h2>
          </div>
          <TagList tags={tags} loading={tagsLoading} />
        </div>
      </aside>
    </div>
  );
}
