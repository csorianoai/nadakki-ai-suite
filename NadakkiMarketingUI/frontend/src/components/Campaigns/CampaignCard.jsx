import React from "react";

const statusConfig = {
  draft: { label: "Borrador", color: "bg-gray-100 text-gray-700" },
  scheduled: { label: "Programada", color: "bg-blue-100 text-blue-700" },
  published: { label: "Publicada", color: "bg-green-100 text-green-700" },
  failed: { label: "Fallida", color: "bg-red-100 text-red-700" }
};
const platformIcons = { facebook: "📘", instagram: "📸", tiktok: "🎵", x: "✖️", linkedin: "💼" };

export default function CampaignCard({ campaign, onEdit, onDelete, onPublish }) {
  const status = statusConfig[campaign.status] || statusConfig.draft;

  return (
    <div className="bg-white rounded-lg border shadow-sm hover:shadow-md">
      <div className="p-4">
        <div className="flex justify-between">
          <div>
            <h3 className="font-semibold">{campaign.name}</h3>
            <p className="text-sm text-gray-500 line-clamp-2">{campaign.content_text?.substring(0, 100) || "Sin contenido"}</p>
          </div>
          <span className={`px-2 py-1 text-xs rounded-full ${status.color}`}>{status.label}</span>
        </div>
        <div className="flex gap-1 mt-3">
          {campaign.target_pages?.map((p, i) => <span key={i}>{platformIcons[p.platform] || "🔗"}</span>)}
        </div>
      </div>
      <div className="border-t px-4 py-2 flex justify-end gap-2">
        {campaign.status === "draft" && (
          <>
            <button onClick={() => onEdit(campaign)} className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded">Editar</button>
            <button onClick={() => onPublish(campaign.id)} className="px-3 py-1 text-sm text-indigo-600 hover:bg-indigo-50 rounded">Publicar</button>
          </>
        )}
        {campaign.status === "scheduled" && (
          <button onClick={() => onDelete(campaign.id)} className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">Cancelar</button>
        )}
      </div>
    </div>
  );
}
