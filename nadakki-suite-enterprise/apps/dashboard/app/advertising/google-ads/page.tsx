'use client';

import { useEffect, useState } from 'react';
import { getAdvertisingAPI } from '@/packages/api-client';
import type { Agent, Metrics } from '@/packages/api-client/types';

export default function GoogleAdsDashboard() {
  const api = getAdvertisingAPI();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [agentsData, metricsData] = await Promise.all([
          api.getAllAgents(),
          api.getMetrics(),
        ]);
        setAgents(agentsData);
        setMetrics(metricsData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [api]);

  if (loading) return <div className="p-8 text-center">Cargando datos...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">🔍 Google Ads Dashboard</h1>

      {metrics && (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="p-4 border rounded bg-white">
            <p className="text-gray-600 text-sm">Gasto Total</p>
            <p className="text-2xl font-bold">${metrics.totalSpent}</p>
          </div>
          <div className="p-4 border rounded bg-white">
            <p className="text-gray-600 text-sm">Conversiones</p>
            <p className="text-2xl font-bold">{metrics.totalConversions}</p>
          </div>
          <div className="p-4 border rounded bg-white">
            <p className="text-gray-600 text-sm">CPC Promedio</p>
            <p className="text-2xl font-bold">${metrics.averageCpc.toFixed(2)}</p>
          </div>
          <div className="p-4 border rounded bg-white">
            <p className="text-gray-600 text-sm">ROAS</p>
            <p className="text-2xl font-bold">${metrics.averageRoas.toFixed(2)}x</p>
          </div>
        </div>
      )}

      <h2 className="text-2xl font-bold mb-4">🤖 Agentes IA</h2>
      <div className="grid grid-cols-2 gap-4">
        {agents.length > 0 ? (
          agents.map((agent) => (
            <div key={agent.id} className="p-4 border rounded bg-white">
              <h3 className="font-bold">{agent.name}</h3>
              <p className="text-sm text-gray-600">{agent.description}</p>
              <p className={`text-sm mt-2 font-semibold ${agent.status === 'ACTIVE' ? 'text-green-600' : 'text-gray-400'}`}>
                {agent.status}
              </p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No hay agentes disponibles</p>
        )}
      </div>
    </div>
  );
}
