import { apiClient } from './client';
export type SocialPlatform = 'facebook' | 'instagram' | 'twitter' | 'linkedin' | 'tiktok' | 'youtube';
export interface SocialConnection {
  id: string; platform: SocialPlatform; account_name: string; status: 'connected' | 'disconnected';
  metrics: { followers: number; posts: number; engagement_rate: number }; connected_at: string;
}
export const socialApi = {
  list: () => apiClient.get<SocialConnection[]>('/api/v1/connections'),
  connect: (platform: SocialPlatform) => apiClient.post<{auth_url: string}>('/api/v1/connections/connect', { platform }),
  disconnect: (id: string) => apiClient.delete(`/api/v1/connections/${id}`),
};
