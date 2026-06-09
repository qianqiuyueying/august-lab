import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getProduct } from '../api/products';
import type { Product } from '../types';
import EmptyState from '../components/ui/EmptyState';
import StatusDot from '../components/ui/StatusDot';
import { formatDate } from '../utils/formatDate';

const panelVariants = {
  hidden: { y: '100%' },
  visible: { y: 0 },
};

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
    <div className="relative h-[calc(100vh-72px)] overflow-hidden bg-background">
      {/* iframe */}
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

      {/* Top toolbar */}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-20 flex justify-center p-3">
        <div className="pointer-events-auto flex items-center gap-2 rounded-xl border border-border bg-background/90 px-3 py-2 shadow-lg backdrop-blur-md">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="focus-ring rounded-lg px-3 py-1.5 text-sm font-bold text-text-secondary transition-colors hover:text-accent"
          >
            ← 返回
          </button>

          <span className="hidden select-none border-l border-border px-2 text-sm font-bold text-paper sm:block">
            {product.title}
          </span>

          {product.runtime_url && (
            <a
              href={product.runtime_url}
              target="_blank"
              rel="noreferrer"
              className="focus-ring rounded-lg border border-border px-3 py-1.5 text-sm font-bold text-text-secondary transition-colors hover:text-accent"
            >
              新窗口打开
            </a>
          )}

          <button
            type="button"
            onClick={() => setPanelOpen((current) => !current)}
            className="focus-ring rounded-lg bg-accent px-3 py-1.5 text-sm font-bold text-background transition-colors hover:bg-accent-hover"
          >
            {panelOpen ? '收起 ▲' : '作品信息 ▼'}
          </button>
        </div>
      </div>

      {/* Bottom info panel */}
      <AnimatePresence>
        {panelOpen && (
          <motion.aside
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={panelVariants}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="absolute bottom-0 left-0 right-0 z-20 mx-auto flex max-w-3xl flex-col rounded-t-2xl border border-b-0 border-border bg-background/95 shadow-2xl backdrop-blur-md"
            style={{ maxHeight: '45vh' }}
          >
            {/* Drag handle */}
            <button
              type="button"
              onClick={() => setPanelOpen(false)}
              className="flex w-full shrink-0 cursor-pointer items-center justify-center pt-3 pb-1"
            >
              <div className="h-1.5 w-10 rounded-full bg-text-muted/30" />
            </button>

            {/* Scrollable content */}
            <div className="min-w-0 flex-1 overflow-auto px-5 pb-5">
              <div className="mt-2 flex items-start gap-4">
                <img
                  src={product.cover_image || '/images/preview/fallback_product_00001_.webp'}
                  alt={product.cover_image ? product.title : ''}
                  aria-hidden={!product.cover_image}
                  loading="lazy"
                  decoding="async"
                  className="h-20 w-28 shrink-0 rounded-lg object-cover"
                />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="section-label">Product</p>
                    <StatusDot status={product.status} />
                  </div>
                  <h1 className="mt-1 text-xl font-extrabold leading-tight text-paper">
                    {product.title}
                  </h1>
                </div>
              </div>

              <p className="mt-3 text-sm leading-7 text-text-secondary">
                {product.description || '暂无描述'}
              </p>

              <dl className="mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-3 text-sm">
                <div>
                  <dt className="text-text-muted">Slug</dt>
                  <dd className="font-bold text-paper">/{product.slug}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">运行文件</dt>
                  <dd className="font-bold text-paper">{product.runtime_url ? '已上传' : '未上传'}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">更新</dt>
                  <dd className="font-bold text-paper">{formatDate(product.updated_at || product.created_at) || '无记录'}</dd>
                </div>
              </dl>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
