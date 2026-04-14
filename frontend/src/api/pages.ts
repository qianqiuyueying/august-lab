import client from './client';
import type { Page } from '../types';

export const getPages = async () => {
  const { data } = await client.get<Page[]>('/pages');
  return data;
};

export const getPage = async (slug: string) => {
  const { data } = await client.get<Page>(`/pages/${slug}`);
  return data;
};

export const createPage = async (page: { slug: string; title: string; content: string; status: string }) => {
  const { data } = await client.post<Page>('/pages', page);
  return data;
};

export const updatePage = async (id: number, page: Partial<{ title: string; content: string; status: string }>) => {
  const { data } = await client.put<Page>(`/pages/${id}`, page);
  return data;
};

export const deletePage = async (id: number) => {
  await client.delete(`/pages/${id}`);
};
