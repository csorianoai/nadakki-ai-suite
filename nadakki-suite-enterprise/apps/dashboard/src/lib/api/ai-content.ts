import { apiClient } from './client';
export interface AITemplate { id: string; name: string; description: string; category: string; }
export interface GeneratedContent { id: string; content: string; template_id: string; generated_at: string; }
export const aiContentApi = {
  getTemplates: () => apiClient.get<AITemplate[]>('/api/v1/ai/templates'),
  generate: (data: { prompt: string; tone?: string; platform?: string }) => apiClient.post<GeneratedContent>('/api/v1/ai/generate', data),
  getHistory: () => apiClient.get<GeneratedContent[]>('/api/v1/ai/history'),
};
