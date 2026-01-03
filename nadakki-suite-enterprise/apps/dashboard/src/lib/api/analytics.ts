import { apiClient } from './client';
export interface DashboardMetrics {
  total_campaigns: number; active_campaigns: number; total_impressions: number;
  total_clicks: number; total_conversions: number;
  growth: { campaigns: number; impressions: number; clicks: number; conversions: number };
}
export const analyticsApi = {
  getDashboard: () => apiClient.get<DashboardMetrics>('/api/v1/analytics/dashboard'),
  getReports: () => apiClient.get('/api/v1/analytics/reports'),
};
