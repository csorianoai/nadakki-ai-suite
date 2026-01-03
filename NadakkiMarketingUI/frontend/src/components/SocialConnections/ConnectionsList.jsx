import React from "react";
import ConnectionCard from "./ConnectionCard";
import ConnectButton from "./ConnectButton";

export default function ConnectionsList({ connections = [], loading, onConnect, onDisconnect }) {
  if (loading) return <div className="flex items-center justify-center py-12"><span className="animate-spin text-4xl">⏳</span></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Redes Sociales Conectadas</h2>
          <p className="text-sm text-gray-500">{connections.length} conexiones</p>
        </div>
        <ConnectButton onConnect={onConnect} />
      </div>
      {connections.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <span className="text-4xl">🔗</span>
          <p className="mt-3 text-gray-600">No tienes redes conectadas</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {connections.map((conn) => <ConnectionCard key={conn.id} connection={conn} onDisconnect={onDisconnect} />)}
        </div>
      )}
    </div>
  );
}
