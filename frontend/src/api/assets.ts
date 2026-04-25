import client from './client';
import type { Asset, AssetListResponse } from '../types';

export const getAssets = async (page = 1, pageSize = 24, search?: string) => {
  const params: Record<string, string | number> = { page, page_size: pageSize, kind: 'image' };
  if (search) params.search = search;
  const { data } = await client.get<AssetListResponse>('/admin/assets', { params });
  return data;
};

export const uploadAsset = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post<Asset>('/admin/assets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const deleteAsset = async (id: number) => {
  await client.delete(`/admin/assets/${id}`);
};
