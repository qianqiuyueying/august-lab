import client from './client';
import type { Article, ArticleListResponse } from '../types';

export const getArticles = async (page = 1, pageSize = 10, tag?: string, search?: string) => {
  const params: Record<string, any> = { page, page_size: pageSize };
  if (tag) params.tag = tag;
  if (search) params.search = search;
  const { data } = await client.get<ArticleListResponse>('/articles', { params });
  return data;
};

export const getArticle = async (slug: string) => {
  const { data } = await client.get<Article>(`/articles/${slug}`);
  return data;
};

export const createArticle = async (article: { title: string; content: string; summary?: string; status: string; tags: string[] }) => {
  const { data } = await client.post<Article>('/articles', article);
  return data;
};

export const updateArticle = async (id: number, article: Partial<{ title: string; content: string; summary: string; status: string; tags: string[] }>) => {
  const { data } = await client.put<Article>(`/articles/${id}`, article);
  return data;
};

export const deleteArticle = async (id: number) => {
  await client.delete(`/articles/${id}`);
};
