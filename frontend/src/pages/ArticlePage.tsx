import { useParams, useNavigate } from 'react-router-dom';
import { useArticle } from '../hooks/useArticles';
import { useComments } from '../hooks/useComments';
import ArticleContent from '../components/articles/ArticleContent';
import CommentForm from '../components/comments/CommentForm';
import CommentList from '../components/comments/CommentList';
import { formatDate } from '../utils/formatDate';

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data: article, loading, error } = useArticle(slug!);
  const { data: comments, loading: commentsLoading, addComment } = useComments(article?.id || 0);

  if (loading) return <div className="text-gray-500 text-center py-12">加载中...</div>;
  if (error) return <div className="text-red-600 text-center py-12">{error}</div>;
  if (!article) return <div className="text-gray-500 text-center py-12">文章不存在</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 text-indigo-600 hover:text-indigo-500"
      >
        &larr; 返回
      </button>

      <article className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 sm:p-8">
        <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">{article.title}</h1>

        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags.map((tag) => (
            <span
              key={tag.id}
              className="bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-xs px-2 py-1 rounded"
            >
              #{tag.name}
            </span>
          ))}
        </div>

        <time className="text-sm text-gray-500 dark:text-gray-400 mb-6 block">
          {formatDate(article.created_at)}
        </time>

        <ArticleContent content={article.content} />
      </article>

      <section className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6 sm:p-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">评论 ({comments.length})</h2>
        <CommentForm onSubmit={(comment) => addComment(comment)} />
        <div className="mt-6">
          <CommentList comments={comments} loading={commentsLoading} />
        </div>
      </section>
    </div>
  );
}
