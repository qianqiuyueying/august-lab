import client from './client';

export const getSetting = async (key: string) => {
  const { data } = await client.get<{ key: string; value: string }>(`/settings/${key}`);
  return data;
};

export const updateSetting = async (key: string, value: string) => {
  const { data } = await client.put<{ key: string; value: string }>(`/settings/${key}`, { value });
  return data;
};
