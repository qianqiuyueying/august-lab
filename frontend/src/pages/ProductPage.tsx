import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getProduct } from '../api/products';
import type { Product } from '../types';
import EmptyState from '../components/ui/EmptyState';
import StatusBadge from '../components/ui/StatusBadge';
import { formatDate } from '../utils/formatDate';

export default function ProductPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [panelOpen, setPanelOpen] = useState(false);

  useEffect(() => {
    if (!slug) return;
    getProduct(slug)
      .then(setProduct)
      .catch((err) => setError(err.response?.data?.detail || '产品不存在'))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <EmptyState title="作品加载中" />;
  if (error) return <EmptyState title="作品读取失败" description={error} />;
  if (!product) return <EmptyState title="作品不存在" />;

  return (
    <div className="h-[calc(100vh-72px)] overflow-hidden bg-background dark:bg-background-dark">
      <div className="relative h-full">
        {product.runtime_url ? (
          <iframe
            title={product.title}
            src={product.runtime_url}
            className="h-full w-full border-0 bg-white"
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads"
          />
        ) : (
          <div className="flex h-full items-center justify-center p-6">
            <EmptyState
              title="作品尚未上传运行文件"
              description="这个产品已经发布，但还没有可运行的 ZIP 静态页面。"
            />
          </div>
        )}

        <div className="absolute left-4 top-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="focus-ring rounded-lg border border-border bg-white/90 px-3 py-2 text-sm font-bold text-zinc-700 shadow-sm backdrop-blur transition-colors hover:text-accent dark:border-border-dark dark:bg-zinc-950/85 dark:text-zinc-200"
          >
            返回
          </button>
          {product.runtime_url && (
            <a
              href={product.runtime_url}
              target="_blank"
              rel="noreferrer"
              className="focus-ring rounded-lg border border-border bg-white/90 px-3 py-2 text-sm font-bold text-zinc-700 shadow-sm backdrop-blur transition-colors hover:text-accent dark:border-border-dark dark:bg-zinc-950/85 dark:text-zinc-200"
            >
              新窗口打开
            </a>
          )}
        </div>

        <button
          type="button"
          onClick={() => setPanelOpen((current) => !current)}
          className="focus-ring absolute right-4 top-4 rounded-lg bg-zinc-950 px-3 py-2 text-sm font-bold text-white shadow-lg transition-colors hover:bg-accent"
        >
          {panelOpen ? '收起信息' : '作品信息'}
        </button>

        <motion.aside
          initial={false}
          animate={{ x: panelOpen ? 0 : 'calc(100% - 56px)' }}
          transition={{ type: 'spring', stiffness: 260, damping: 28 }}
          className="absolute bottom-4 right-4 top-16 flex w-[min(380px,calc(100vw-32px))] overflow-hidden rounded-lg border border-border bg-white/95 shadow-xl backdrop-blur dark:border-border-dark dark:bg-zinc-950/95"
        >
          <button
            type="button"
            onClick={() => setPanelOpen((current) => !current)}
            className="flex w-14 shrink-0 items-center justify-center border-r border-border text-xs font-bold text-text-muted [writing-mode:vertical-rl] hover:text-accent dark:border-border-dark dark:text-text-muted-dark"
          >
            信息
          </button>
          <div className="min-w-0 flex-1 overflow-auto p-5">
            <img
              src={product.cover_image || '/images/brand/fallback-product.webp'}
              alt={product.cover_image ? product.title : ''}
              aria-hidden={!product.cover_image}
              className="aspect-[16/9] w-full rounded-lg object-cover"
            />
            <div className="mt-4 flex items-center justify-between gap-3">
              <p className="section-label">Product</p>
              <StatusBadge status={product.status} />
            </div>
            <h1 className="mt-2 text-2xl font-extrabold leading-tight text-text-primary dark:text-text-primary-dark">
              {product.title}
            </h1>
            <p className="mt-4 text-sm leading-7 text-text-secondary dark:text-text-secondary-dark">
              {product.description || '暂无描述'}
            </p>
            <dl className="mt-5 space-y-3 border-t border-border pt-4 text-sm dark:border-border-dark">
              <div className="flex justify-between gap-4">
                <dt className="text-text-muted dark:text-text-muted-dark">Slug</dt>
                <dd className="font-bold text-zinc-900 dark:text-white">/{product.slug}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-text-muted dark:text-text-muted-dark">运行文件</dt>
                <dd className="font-bold text-zinc-900 dark:text-white">{product.runtime_url ? '已上传' : '未上传'}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-text-muted dark:text-text-muted-dark">更新</dt>
                <dd className="font-bold text-zinc-900 dark:text-white">{formatDate(product.updated_at || product.created_at) || '无记录'}</dd>
              </div>
            </dl>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}
