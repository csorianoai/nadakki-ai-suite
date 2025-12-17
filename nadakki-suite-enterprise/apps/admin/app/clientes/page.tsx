'use client';

import { useState } from 'react';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: 'starter' | 'professional' | 'enterprise';
  status: 'active' | 'trial' | 'suspended';
  users: number;
  agents: number;
  monthlyFee: number;
  createdAt: string;
}

export default function ClientesPage() {
  const [tenants, setTenants] = useState<Tenant[]>([
    { 
      id: '1', name: 'Credicefi', slug: 'credicefi', plan: 'enterprise', 
      status: 'active', users: 15, agents: 24, monthlyFee: 2999, createdAt: '2024-01-15' 
    },
    { 
      id: '2', name: 'Banco ABC', slug: 'banco_abc', plan: 'professional', 
      status: 'active', users: 8, agents: 12, monthlyFee: 1499, createdAt: '2024-06-20' 
    },
    { 
      id: '3', name: 'Cooperativa XYZ', slug: 'coop_xyz', plan: 'starter', 
      status: 'trial', users: 3, agents: 5, monthlyFee: 499, createdAt: '2024-11-01' 
    },
  ]);

  const getPlanColor = (plan: string) => {
    switch(plan) {
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      case 'professional': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'trial': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">🏦 Clientes / Instituciones</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Total Clientes</p>
          <p className="text-3xl font-bold">{tenants.length}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Activos</p>
          <p className="text-3xl font-bold">{tenants.filter(t => t.status === 'active').length}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">En Trial</p>
          <p className="text-3xl font-bold">{tenants.filter(t => t.status === 'trial').length}</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Revenue Mensual</p>
          <p className="text-3xl font-bold">${tenants.reduce((a, t) => a + t.monthlyFee, 0).toLocaleString()}</p>
        </div>
      </div>

      <div className="mb-4">
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          + Nueva Institución
        </button>
      </div>

      <table className="w-full border-collapse border">
        <thead className="bg-gray-100">
          <tr>
            <th className="border p-3 text-left">Institución</th>
            <th className="border p-3 text-left">Plan</th>
            <th className="border p-3 text-left">Estado</th>
            <th className="border p-3 text-left">Usuarios</th>
            <th className="border p-3 text-left">Agentes IA</th>
            <th className="border p-3 text-left">Mensualidad</th>
            <th className="border p-3 text-left">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {tenants.map((tenant) => (
            <tr key={tenant.id} className="hover:bg-gray-50">
              <td className="border p-3">
                <div>
                  <p className="font-semibold">{tenant.name}</p>
                  <p className="text-sm text-gray-500">{tenant.slug}</p>
                </div>
              </td>
              <td className="border p-3">
                <span className={`px-2 py-1 rounded text-sm ${getPlanColor(tenant.plan)}`}>
                  {tenant.plan.toUpperCase()}
                </span>
              </td>
              <td className="border p-3">
                <span className={`px-2 py-1 rounded text-sm ${getStatusColor(tenant.status)}`}>
                  {tenant.status}
                </span>
              </td>
              <td className="border p-3">{tenant.users}</td>
              <td className="border p-3">{tenant.agents}</td>
              <td className="border p-3 font-semibold">${tenant.monthlyFee.toLocaleString()}</td>
              <td className="border p-3">
                <button className="text-blue-600 hover:underline mr-2">Ver</button>
                <button className="text-green-600 hover:underline mr-2">Configurar</button>
                <button className="text-red-600 hover:underline">Suspender</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}