import { useState, useEffect } from 'react';
import { getArticles, getArticle, createArticle, updateArticle, deleteArticle } from '../api/articles';
import type { Article, ArticleListResponse } from '../types';

export function useArticles(page = 1, pageSize = 10, tag?: string, search?: string) {
  const [data, setData] = useState<ArticleListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getArticles(page, pageSize, tag, search)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [page, pageSize, tag, search]);

  return { data, loading, error, refetch: () => getArticles(page, pageSize, tag, search).then(setData) };
}

export function useArticle(slug: string) {
  const [data, setData] = useState<Article | null>(null);
  const [loading, setLoading] = useState(!!slug);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      setLoading(false);
      return;
    }
    setLoading(true);
    getArticle(slug)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug]);

  return { data, loading, error, refetch: () => getArticle(slug).then(setData) };
}

export function useArticleMutations() {
  return { createArticle, updateArticle, deleteArticle };
}
