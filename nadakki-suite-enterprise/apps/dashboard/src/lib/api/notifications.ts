import { apiClient } from './client';
export interface Notification {
  id: string; title: string; message: string; type: 'info' | 'success' | 'warning' | 'error';
  read: boolean; created_at: string;
}
export const notificationsApi = {
  list: (unreadOnly = false) => apiClient.get<Notification[]>(`/api/v1/notifications${unreadOnly ? '?unread=true' : ''}`),
  markAsRead: (id: string) => apiClient.patch(`/api/v1/notifications/${id}`, { read: true }),
  markAllAsRead: () => apiClient.post('/api/v1/notifications/mark-all-read', {}),
};
