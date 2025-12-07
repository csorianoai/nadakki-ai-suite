import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_RENDER_API_URL || 'https://nadakki-ai-suite.onrender.com';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || 'credicefi';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'sk_live_credicefi_12345678abcdefgh';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': TENANT_ID,
    'X-API-Key': API_KEY,
  }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = \Bearer \\;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  getCores: () => apiClient.get('/cores'),
  getCore: (id: string) => apiClient.get(\/cores/\\),
  getAgents: () => apiClient.get('/agents'),
  executeAgent: (id: string, payload: any) => apiClient.post(\/agents/\/execute\, payload),
  getMetrics: () => apiClient.get('/dashboard/metrics'),
  getHealth: () => apiClient.get('/health'),
  getTenants: () => apiClient.get('/tenants'),
  createTenant: (data: any) => apiClient.post('/tenants', data),
  getInvoices: () => apiClient.get('/billing/invoices'),
};

export default apiClient;
