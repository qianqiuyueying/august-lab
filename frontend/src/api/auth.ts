import client from './client';
import type { User } from '../types';

export const login = async (username: string, password: string) => {
  const { data } = await client.post<{ access_token: string }>('/auth/login', { username, password });
  return data;
};

export const getMe = async () => {
  const { data } = await client.get<User>('/auth/me');
  return data;
};
