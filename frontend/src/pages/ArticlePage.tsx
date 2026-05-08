import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useArticle } from '../hooks/useArticles';
import { useSeoMeta } from '../hooks/useSeoMeta';
import ArticleContent from '../components/articles/ArticleContent';
import { formatDate } from '../utils/formatDate';
import { estimateReadingTime } from '../utils/readingTime';
import EmptyState from '../components/ui/EmptyState';
import GlassPanel from '../components/ui/GlassPanel';

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data: article, loading, error } = useArticle(slug!);

  useSeoMeta(article);

  if (loading) return <EmptyState title="文章加载中" />;
  if (error) return <EmptyState title="文章读取失败" description={error} />;
  if (!article) return <EmptyState title="文章不存在" />;

  const readingTime = estimateReadingTime(article.content || article.summary);
  const cover = article.cover_image || '/images/brand/fallback-article.webp';

  return (
    <article className="mx-auto max-w-5xl">
      <motion.button
        onClick={() => navigate(-1)}
        whileHover={{ x: -3 }}
        className="mb-6 inline-flex items-center gap-2 text-sm font-bold text-text-muted transition-colors hover:text-accent dark:text-text-muted-dark"
      >
        <span aria-hidden="true">←</span>
        返回上一页
      </motion.button>

      {/* Article number */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-mono text-sm text-text-muted/50 dark:text-text-muted-dark/30 mb-4"
      >
        EXP-{String(article.id).padStart(4, '0')}
      </motion.p>

      <motion.header
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl">
          {article.title}
        </h1>
        <p className="mt-6 max-w-3xl text-lg leading-9 text-text-secondary dark:text-text-secondary-dark">
          {article.summary}
        </p>

        {/* Metadata row */}
        <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 border-y border-border py-4 text-sm font-bold text-text-muted dark:border-border-dark dark:text-text-muted-dark">
          <span>{formatDate(article.created_at) || '未标注日期'}</span>
          <span aria-hidden="true" className="text-border dark:text-border-dark">·</span>
          <span>{readingTime} min read</span>
          <span aria-hidden="true" className="text-border dark:text-border-dark">·</span>
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <Link key={tag.id} to={`/blog?tag=${encodeURIComponent(tag.name)}`} className="lab-chip text-[10px] px-1.5 py-0.5">
                #{tag.name}
              </Link>
            ))}
          </div>
        </div>
      </motion.header>

      {/* Cover image */}
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.04 }}
        className="mb-8"
      >
        <GlassPanel accentLine className="overflow-hidden">
          <img src={cover} alt={article.cover_image ? article.title : ''} decoding="async" className="aspect-[16/9] w-full object-cover" aria-hidden={!article.cover_image} />
        </GlassPanel>
      </motion.div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
      >
        <GlassPanel accentLine className="px-5 py-7 sm:px-9 sm:py-10">
          <ArticleContent content={article.content} />
        </GlassPanel>
      </motion.div>
    </article>
  );
}
