import client from './client';
import type { User } from '../types';

export const register = async (username: string, password: string) => {
  const { data } = await client.post<User>('/auth/register', { username, password });
  return data;
};

export const login = async (username: string, password: string) => {
  const { data } = await client.post<{ access_token: string }>('/auth/login', { username, password });
  return data;
};

export const getMe = async () => {
  const { data } = await client.get<User>('/auth/me');
  return data;
};
