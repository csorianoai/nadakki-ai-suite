const API_URL = process.env.NEXT_PUBLIC_RENDER_API_URL || 'https://nadakki-ai-suite.onrender.com';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || 'credicefi';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface ApiResponse<T> { data: T | null; error: string | null; status: number; }

class ApiClient {
  private headers(): HeadersInit {
    return { 'Content-Type': 'application/json', 'X-Tenant-ID': TENANT_ID, 'X-API-Key': API_KEY };
  }
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const res = await fetch(`${API_URL}${endpoint}`, { headers: this.headers() });
      const data = await res.json();
      return { data: res.ok ? data : null, error: res.ok ? null : data.detail || 'Error', status: res.status };
    } catch (e) { return { data: null, error: (e as Error).message, status: 0 }; }
  }
  async post<T>(endpoint: string, body: unknown): Promise<ApiResponse<T>> {
    try {
      const res = await fetch(`${API_URL}${endpoint}`, { method: 'POST', headers: this.headers(), body: JSON.stringify(body) });
      const data = await res.json();
      return { data: res.ok ? data : null, error: res.ok ? null : data.detail || 'Error', status: res.status };
    } catch (e) { return { data: null, error: (e as Error).message, status: 0 }; }
  }
  async patch<T>(endpoint: string, body: unknown): Promise<ApiResponse<T>> {
    try {
      const res = await fetch(`${API_URL}${endpoint}`, { method: 'PATCH', headers: this.headers(), body: JSON.stringify(body) });
      const data = await res.json();
      return { data: res.ok ? data : null, error: res.ok ? null : data.detail || 'Error', status: res.status };
    } catch (e) { return { data: null, error: (e as Error).message, status: 0 }; }
  }
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const res = await fetch(`${API_URL}${endpoint}`, { method: 'DELETE', headers: this.headers() });
      const data = res.status !== 204 ? await res.json() : null;
      return { data: res.ok ? data : null, error: res.ok ? null : data?.detail || 'Error', status: res.status };
    } catch (e) { return { data: null, error: (e as Error).message, status: 0 }; }
  }
}
export const apiClient = new ApiClient();
