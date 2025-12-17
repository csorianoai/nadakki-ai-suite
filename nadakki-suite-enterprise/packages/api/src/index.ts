import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://nadakki-ai-suite.onrender.com';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || 'credicefi';
const API_KEY = process.env.API_KEY || 'nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I';

class NadakkiAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': TENANT_ID,
        'X-API-Key': API_KEY,
      },
    });
  }

  // Health check
  async health() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Get all agents
  async getAgents() {
    const response = await this.client.get('/agents');
    return response.data;
  }

  // Get agent categories
  async getCategories() {
    const response = await this.client.get('/agents/categories');
    return response.data;
  }

  // Get usage by tenant
  async getUsage(tenantId: string = TENANT_ID) {
    const response = await this.client.get(`/usage/${tenantId}`);
    return response.data;
  }

  // Execute marketing agent
  async executeMarketingAgent(agentId: string, data: any) {
    const response = await this.client.post(`/api/marketing/${agentId}/execute`, data);
    return response.data;
  }

  // Lead Scoring
  async leadScoring(data: any) {
    const response = await this.client.post('/api/marketing/lead-scoring', data);
    return response.data;
  }

  // Campaign Optimizer
  async campaignOptimizer(data: any) {
    const response = await this.client.post('/api/marketing/campaign-optimizer', data);
    return response.data;
  }

  // Customer Segmentation
  async customerSegmentation(data: any) {
    const response = await this.client.post('/api/marketing/customer-segmentation', data);
    return response.data;
  }

  // Get service info
  async getServiceInfo() {
    const response = await this.client.get('/');
    return response.data;
  }
}

export const nadakkiAPI = new NadakkiAPI();
export default nadakkiAPI;
