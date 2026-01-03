import { apiClient } from './client';
export interface SchedulerStatus { running: boolean; jobs_count: number; active_jobs: number; next_scheduled: string | null; }
export interface ScheduledJob { id: string; name: string; status: string; cron_expression: string | null; last_run: string | null; }
export const schedulerApi = {
  getStatus: () => apiClient.get<SchedulerStatus>('/api/v1/scheduler/status'),
  listJobs: () => apiClient.get<ScheduledJob[]>('/api/v1/scheduler/jobs'),
  start: () => apiClient.post('/api/v1/scheduler/start', {}),
  stop: () => apiClient.post('/api/v1/scheduler/stop', {}),
};
