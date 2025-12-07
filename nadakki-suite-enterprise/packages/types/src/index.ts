export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'healthy' | 'error' | 'unknown';
  category: string;
  lastRun?: string;
}

export interface Core {
  id: string;
  name: string;
  description: string;
  agents: Agent[];
  icon: string;
  color: string;
}

export interface Tenant {
  id: string;
  name: string;
  email: string;
  plan: 'starter' | 'professional' | 'enterprise';
  status: 'active' | 'inactive';
}

export interface DashboardMetrics {
  total_evaluations: number;
  agents_active: number;
  revenue_today: number;
  uptime_percentage: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
}

export interface Invoice {
  id: string;
  invoice_number: string;
  tenant_id: string;
  amount: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  due_date: string;
  created_at: string;
}
