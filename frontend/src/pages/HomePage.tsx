import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useArticles } from '../hooks/useArticles';
import { useTags } from '../hooks/useTags';
import ArticleCard from '../components/articles/ArticleCard';
import TagList from '../components/tags/TagList';
import SearchBar from '../components/search/SearchBar';

export default function HomePage() {
  const [searchParams] = useSearchParams();
  const [page, setPage] = useState(1);
  const tag = searchParams.get('tag') || undefined;
  const search = searchParams.get('search') || undefined;

  const { data, loading, error } = useArticles(page, 10, tag, search);
  const { data: tags, loading: tagsLoading } = useTags();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div className="lg:col-span-3 space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {tag ? `标签: ${tag}` : search ? `搜索: ${search}` : '最新文章'}
          </h1>
          <SearchBar />
        </div>

        {error && <div className="text-red-600 bg-red-50 dark:bg-red-900/20 p-4 rounded">{error}</div>}

        {loading ? (
          <div className="text-gray-500">加载中...</div>
        ) : (
          <>
            <div className="space-y-4">
              {data?.items.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
              {data?.items.length === 0 && (
                <div className="text-gray-500 text-center py-8">暂无文章</div>
              )}
            </div>

            {data && data.total > data.page_size && (
              <div className="flex justify-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 rounded border disabled:opacity-50"
                >
                  上一页
                </button>
                <span className="px-3 py-1">
                  第 {data.page} 页 / 共 {Math.ceil(data.total / data.page_size)} 页
                </span>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * data.page_size >= data.total}
                  className="px-3 py-1 rounded border disabled:opacity-50"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <aside className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">标签</h2>
          <TagList tags={tags} loading={tagsLoading} />
        </div>
      </aside>
    </div>
  );
}
