import client from './client';
import type { AboutPage } from '../types';

export const getAbout = async () => {
  const { data } = await client.get<AboutPage>('/about');
  return data;
};

export const updateAbout = async (data: Partial<AboutPage>) => {
  const { data: result } = await client.put<AboutPage>('/about', data);
  return result;
};
