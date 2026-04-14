import client from './client';
import type { Comment } from '../types';

export const getComments = async (articleId: number) => {
  const { data } = await client.get<Comment[]>(`/articles/${articleId}/comments`);
  return data;
};

export const createComment = async (articleId: number, comment: { author_name: string; author_email: string; content: string }) => {
  const { data } = await client.post<Comment>(`/articles/${articleId}/comments`, comment);
  return data;
};

export const deleteComment = async (id: number) => {
  await client.delete(`/comments/${id}`);
};
