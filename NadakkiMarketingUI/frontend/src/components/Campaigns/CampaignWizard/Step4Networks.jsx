import React from "react";

const platformIcons = { facebook: "📘", instagram: "📸", tiktok: "🎵", x: "✖️", linkedin: "💼" };

export default function Step4Networks({ data, onChange, connections = [] }) {
  const togglePage = (conn) => {
    const pages = data.target_pages || [];
    const exists = pages.find(p => p.connection_id === conn.id);
    if (exists) {
      onChange({ target_pages: pages.filter(p => p.connection_id !== conn.id) });
    } else {
      onChange({ target_pages: [...pages, { platform: conn.platform, page_id: conn.page_id, page_name: conn.page_name, connection_id: conn.id }] });
    }
  };

  const isSelected = (id) => (data.target_pages || []).some(p => p.connection_id === id);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">¿Dónde publicar?</h3>
      {connections.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <span className="text-4xl">🔗</span>
          <p className="mt-3">No tienes redes conectadas</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {connections.map((conn) => (
            <button key={conn.id} type="button" onClick={() => togglePage(conn)}
              className={`p-4 text-left rounded-lg border-2 ${isSelected(conn.id) ? "border-indigo-500 bg-indigo-50" : "border-gray-200"}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{platformIcons[conn.platform] || "🔗"}</span>
                  <span className="font-medium">{conn.page_name}</span>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${isSelected(conn.id) ? "border-indigo-500 bg-indigo-500 text-white" : "border-gray-300"}`}>
                  {isSelected(conn.id) && "✓"}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
      {(data.target_pages?.length || 0) > 0 && (
        <div className="p-4 bg-green-50 rounded-lg">
          <h4 className="font-medium text-green-800">{data.target_pages.length} redes seleccionadas</h4>
        </div>
      )}
    </div>
  );
}
