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
        className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-text-muted transition-colors hover:text-accent dark:text-text-muted-dark"
      >
        <span aria-hidden="true">←</span>
        返回上一页
      </motion.button>

      <motion.header
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10 grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end"
      >
        <div>
          <div className="mb-5 flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <Link key={tag.id} to={`/blog?tag=${encodeURIComponent(tag.name)}`} className="lab-chip">
                #{tag.name}
              </Link>
            ))}
          </div>
          <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary dark:text-text-primary-dark sm:text-5xl lg:text-6xl">
            {article.title}
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-9 text-text-secondary dark:text-text-secondary-dark">
            {article.summary}
          </p>
          <div className="mt-7 flex flex-wrap gap-4 border-y border-border py-4 text-sm font-bold text-text-muted dark:border-border-dark dark:text-text-muted-dark">
            <span>{formatDate(article.created_at) || '未标注日期'}</span>
            <span aria-hidden="true">/</span>
            <span>{readingTime} min read</span>
          </div>
        </div>

        <GlassPanel className="overflow-hidden">
          <img src={cover} alt={article.cover_image ? article.title : ''} className="aspect-[4/3] w-full object-cover" aria-hidden={!article.cover_image} />
        </GlassPanel>
      </motion.header>

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
      >
        <GlassPanel className="px-5 py-7 sm:px-9 sm:py-10">
          <ArticleContent content={article.content} />
        </GlassPanel>
      </motion.div>
    </article>
  );
}
