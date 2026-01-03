import { apiClient } from './client';
export interface Tenant {
  id: string; name: string; slug: string; industry: string; logo_url: string | null;
  subscription: { plan: string; status: string; expires_at: string };
}
export const tenantsApi = {
  list: () => apiClient.get<Tenant[]>('/api/v1/tenants'),
  getCurrent: () => apiClient.get<Tenant>('/api/v1/tenants/current'),
  switchTenant: (tenantId: string) => apiClient.post<{token: string}>('/api/v1/tenants/switch', { tenant_id: tenantId }),
};
