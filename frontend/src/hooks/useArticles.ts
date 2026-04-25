import { useEffect, useMemo, useState } from 'react';
import { getArticles, getArticle, createArticle, updateArticle, deleteArticle } from '../api/articles';
import type { Article, ArticleListResponse } from '../types';

interface ArticlesState {
  key: string;
  data: ArticleListResponse | null;
  error: string | null;
}

interface ArticleState {
  key: string;
  data: Article | null;
  error: string | null;
}

export function useArticles(page = 1, pageSize = 10, tag?: string, search?: string) {
  const requestKey = useMemo(() => [page, pageSize, tag ?? '', search ?? ''].join('\u0001'), [page, pageSize, tag, search]);
  const [state, setState] = useState<ArticlesState>({ key: '', data: null, error: null });

  useEffect(() => {
    let cancelled = false;

    getArticles(page, pageSize, tag, search)
      .then((data) => {
        if (!cancelled) setState({ key: requestKey, data, error: null });
      })
      .catch((e) => {
        if (!cancelled) setState({ key: requestKey, data: null, error: e.message });
      });

    return () => {
      cancelled = true;
    };
  }, [page, pageSize, tag, search, requestKey]);

  const refetch = () =>
    getArticles(page, pageSize, tag, search).then((data) => {
      setState({ key: requestKey, data, error: null });
      return data;
    });

  return { data: state.data, loading: state.key !== requestKey, error: state.key === requestKey ? state.error : null, refetch };
}

export function useArticle(slug: string) {
  const requestKey = slug || '__missing__';
  const [state, setState] = useState<ArticleState>({ key: '', data: null, error: null });

  useEffect(() => {
    if (!slug) return;

    let cancelled = false;
    getArticle(slug)
      .then((data) => {
        if (!cancelled) setState({ key: requestKey, data, error: null });
      })
      .catch((e) => {
        if (!cancelled) setState({ key: requestKey, data: null, error: e.message });
      });

    return () => {
      cancelled = true;
    };
  }, [slug, requestKey]);

  const refetch = () =>
    getArticle(slug).then((data) => {
      setState({ key: requestKey, data, error: null });
      return data;
    });

  return { data: state.data, loading: !!slug && state.key !== requestKey, error: state.key === requestKey ? state.error : null, refetch };
}

export function useArticleMutations() {
  return { createArticle, updateArticle, deleteArticle };
}
