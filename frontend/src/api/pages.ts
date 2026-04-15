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

export const createPage = async (page: { slug: string; title: string; content: string; description?: string; content_type?: string; status: string }) => {
  const { data } = await client.post<Page>('/pages', page);
  return data;
};

export const updatePage = async (id: number, page: Partial<{ title: string; content: string; description: string; content_type: string; status: string }>) => {
  const { data } = await client.put<Page>(`/pages/${id}`, page);
  return data;
};

export const deletePage = async (id: number) => {
  await client.delete(`/pages/${id}`);
};

export const uploadProductZip = async (pageId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post(`/pages/${pageId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};
