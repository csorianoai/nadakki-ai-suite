'use client';

import { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
  tenant: string;
}

export default function UsuariosPage() {
  const [users, setUsers] = useState<User[]>([
    { id: '1', name: 'Admin Principal', email: 'admin@credicefi.com', role: 'admin', status: 'active', tenant: 'credicefi' },
    { id: '2', name: 'Analista Riesgo', email: 'riesgo@credicefi.com', role: 'analyst', status: 'active', tenant: 'credicefi' },
    { id: '3', name: 'Operador', email: 'ops@bancoabc.com', role: 'operator', status: 'active', tenant: 'banco_abc' },
  ]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">👥 Gestión de Usuarios</h1>
      
      <div className="mb-4 flex gap-4">
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          + Nuevo Usuario
        </button>
        <input 
          type="text" 
          placeholder="Buscar usuario..." 
          className="border px-4 py-2 rounded flex-1"
        />
      </div>

      <table className="w-full border-collapse border">
        <thead className="bg-gray-100">
          <tr>
            <th className="border p-3 text-left">Nombre</th>
            <th className="border p-3 text-left">Email</th>
            <th className="border p-3 text-left">Rol</th>
            <th className="border p-3 text-left">Tenant</th>
            <th className="border p-3 text-left">Estado</th>
            <th className="border p-3 text-left">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-gray-50">
              <td className="border p-3">{user.name}</td>
              <td className="border p-3">{user.email}</td>
              <td className="border p-3">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  {user.role}
                </span>
              </td>
              <td className="border p-3">{user.tenant}</td>
              <td className="border p-3">
                <span className={`px-2 py-1 rounded text-sm ${
                  user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {user.status === 'active' ? '✅ Activo' : '❌ Inactivo'}
                </span>
              </td>
              <td className="border p-3">
                <button className="text-blue-600 hover:underline mr-2">Editar</button>
                <button className="text-red-600 hover:underline">Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}