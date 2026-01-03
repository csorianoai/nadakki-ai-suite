import { apiClient } from './client';
export type ExportFormat = 'csv' | 'json' | 'xlsx' | 'pdf';
export interface ExportJob {
  id: string; name: string; format: ExportFormat; status: 'pending' | 'processing' | 'completed' | 'failed';
  file_url: string | null; created_at: string;
}
export const exportApi = {
  list: () => apiClient.get<ExportJob[]>('/api/v1/export'),
  create: (data: { name: string; format: ExportFormat; resource_type: string }) => apiClient.post<ExportJob>('/api/v1/export', data),
  download: (id: string) => apiClient.get<{download_url: string}>(`/api/v1/export/${id}/download`),
};
