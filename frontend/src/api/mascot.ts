import client from './client';
import type { MascotSettings, MascotSettingsAdmin } from '../types';

export const getMascotSettings = async (): Promise<MascotSettings> => {
  const { data } = await client.get<MascotSettings>('/mascot/settings');
  return data;
};

export const sendMascotChat = async (message: string, context?: string) => {
  const { data } = await client.post<{ reply: string }>('/mascot/chat', {
    message,
    context,
  });
  return data;
};

export const getAdminMascotSettings = async (): Promise<MascotSettingsAdmin> => {
  const { data } = await client.get<MascotSettingsAdmin>('/mascot/admin/settings');
  return data;
};

export const updateAdminMascotSettings = async (
  settings: Partial<MascotSettingsAdmin>
): Promise<MascotSettingsAdmin> => {
  const { data } = await client.put<MascotSettingsAdmin>('/mascot/admin/settings', settings);
  return data;
};
