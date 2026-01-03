import { apiClient, ApiResponse } from './client';
export interface Campaign {
  id: string; name: string; description: string;
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed';
  platforms: string[]; content: string; scheduled_at: string | null;
  metrics: { impressions: number; clicks: number; conversions: number; engagement_rate: number };
  created_at: string;
}
export const campaignsApi = {
  list: (page = 1) => apiClient.get<{items: Campaign[]; total: number}>(`/api/v1/campaigns?page=${page}`),
  get: (id: string) => apiClient.get<Campaign>(`/api/v1/campaigns/${id}`),
  create: (data: Partial<Campaign>) => apiClient.post<Campaign>('/api/v1/campaigns', data),
  update: (id: string, data: Partial<Campaign>) => apiClient.patch<Campaign>(`/api/v1/campaigns/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/v1/campaigns/${id}`),
};
