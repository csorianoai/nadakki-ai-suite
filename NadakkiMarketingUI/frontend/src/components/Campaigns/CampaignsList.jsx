import React, { useState } from "react";
import CampaignCard from "./CampaignCard";

const statusFilters = [
  { id: "all", name: "Todas" }, { id: "draft", name: "Borradores" },
  { id: "scheduled", name: "Programadas" }, { id: "published", name: "Publicadas" }
];

export default function CampaignsList({ campaigns = [], loading, onEdit, onDelete, onPublish, onCreateNew }) {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? campaigns : campaigns.filter(c => c.status === filter);

  if (loading) return <div className="flex justify-center py-12"><span className="animate-spin text-4xl">⏳</span></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <h2 className="text-xl font-bold">Mis Campañas</h2>
          <p className="text-sm text-gray-500">{campaigns.length} campañas</p>
        </div>
        <button onClick={onCreateNew} className="px-4 py-2 bg-indigo-600 text-white rounded-lg">➕ Nueva Campaña</button>
      </div>
      <div className="flex gap-2">
        {statusFilters.map((sf) => (
          <button key={sf.id} onClick={() => setFilter(sf.id)}
            className={`px-4 py-2 rounded-full text-sm ${filter === sf.id ? "bg-indigo-600 text-white" : "bg-gray-100"}`}>
            {sf.name}
          </button>
        ))}
      </div>
      {filtered.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <span className="text-4xl">📋</span>
          <p className="mt-3">No hay campañas</p>
          {filter === "all" && <button onClick={onCreateNew} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg">Crear primera</button>}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((c) => <CampaignCard key={c.id} campaign={c} onEdit={onEdit} onDelete={onDelete} onPublish={onPublish} />)}
        </div>
      )}
    </div>
  );
}
