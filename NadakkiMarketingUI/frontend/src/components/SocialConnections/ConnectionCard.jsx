import React from "react";

const platformIcons = { facebook: "📘", instagram: "📸", tiktok: "🎵", x: "✖️", linkedin: "💼", pinterest: "📌", youtube: "▶️" };
const platformColors = { facebook: "bg-blue-100 border-blue-500", instagram: "bg-pink-100 border-pink-500", tiktok: "bg-gray-100 border-gray-800", x: "bg-gray-100 border-gray-600", linkedin: "bg-blue-100 border-blue-700" };
const statusColors = { active: "bg-green-500", expired: "bg-yellow-500", error: "bg-red-500" };

export default function ConnectionCard({ connection, onDisconnect }) {
  const { id, platform, page_name, page_username, followers_count, status } = connection;
  const icon = platformIcons[platform] || "🔗";
  const colorClass = platformColors[platform] || "bg-gray-100 border-gray-400";
  const statusColor = statusColors[status] || "bg-gray-400";

  return (
    <div className={`p-4 rounded-lg border-l-4 ${colorClass} shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className="font-semibold text-gray-800">{page_name}</h3>
            {page_username && <p className="text-sm text-gray-500">@{page_username}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${statusColor}`}></span>
          <span className="text-xs text-gray-500 capitalize">{status}</span>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-4 text-sm text-gray-600">
        <span className="font-medium">{followers_count?.toLocaleString() || 0}</span> seguidores
      </div>
      <div className="mt-4 flex justify-end">
        <button onClick={() => onDisconnect(id)} className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">Desconectar</button>
      </div>
    </div>
  );
}
