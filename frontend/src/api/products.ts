import client from './client';
import type { Product } from '../types';

export const getProducts = async () => {
  const { data } = await client.get<Product[]>('/products');
  return data;
};

export const createProduct = async (product: { slug: string; title: string; description?: string; status: string }) => {
  const { data } = await client.post<Product>('/products', product);
  return data;
};

export const updateProduct = async (id: number, product: Partial<{ title: string; description: string; status: string }>) => {
  const { data } = await client.put<Product>(`/products/${id}`, product);
  return data;
};

export const deleteProduct = async (id: number) => {
  await client.delete(`/products/${id}`);
};

export const uploadProductZip = async (productId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post(`/products/${productId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};
