import client from './client';
import type { Tag } from '../types';

export const getTags = async () => {
  const { data } = await client.get<Tag[]>('/tags');
  return data;
};

export const createTag = async (name: string) => {
  const { data } = await client.post<Tag>('/tags', { name });
  return data;
};

export const deleteTag = async (id: number) => {
  await client.delete(`/tags/${id}`);
};
