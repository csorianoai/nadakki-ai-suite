'use client';

import { useState } from 'react';

export default function ConfiguracionPage() {
  const [config, setConfig] = useState({
    apiUrl: 'https://nadakki-ai-suite.onrender.com',
    defaultTenant: 'credicefi',
    maxAgentsPerTenant: 50,
    trialDays: 14,
    enableBilling: true,
    enableMultiTenant: true,
  });

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">⚙️ Configuración del Sistema</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">🔌 Conexión API</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">URL del Backend</label>
              <input 
                type="text" 
                value={config.apiUrl}
                onChange={(e) => setConfig({...config, apiUrl: e.target.value})}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tenant por Defecto</label>
              <input 
                type="text" 
                value={config.defaultTenant}
                onChange={(e) => setConfig({...config, defaultTenant: e.target.value})}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded">
              <span className="text-green-600">✅</span>
              <span>Backend conectado y funcionando</span>
            </div>
          </div>
        </div>

        {/* Multi-tenant Configuration */}
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">🏢 Multi-Tenant</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Habilitar Multi-Tenant</span>
              <input 
                type="checkbox" 
                checked={config.enableMultiTenant}
                onChange={(e) => setConfig({...config, enableMultiTenant: e.target.checked})}
                className="w-5 h-5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Máx. Agentes por Tenant</label>
              <input 
                type="number" 
                value={config.maxAgentsPerTenant}
                onChange={(e) => setConfig({...config, maxAgentsPerTenant: parseInt(e.target.value)})}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Días de Trial</label>
              <input 
                type="number" 
                value={config.trialDays}
                onChange={(e) => setConfig({...config, trialDays: parseInt(e.target.value)})}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
          </div>
        </div>

        {/* Billing Configuration */}
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">💰 Facturación</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Habilitar Sistema de Facturación</span>
              <input 
                type="checkbox" 
                checked={config.enableBilling}
                onChange={(e) => setConfig({...config, enableBilling: e.target.checked})}
                className="w-5 h-5"
              />
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="font-semibold">Planes Disponibles:</p>
              <ul className="text-sm mt-2 space-y-1">
                <li>• Starter: $499/mes (5 agentes)</li>
                <li>• Professional: $1,499/mes (15 agentes)</li>
                <li>• Enterprise: $2,999/mes (50 agentes)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">📊 Estado del Sistema</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>Backend API</span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">✅ Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Base de Datos</span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">✅ Conectada</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Agentes IA</span>
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">276 activos</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Versión</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">v3.4.3</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <button className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
          💾 Guardar Configuración
        </button>
      </div>
    </div>
  );
}