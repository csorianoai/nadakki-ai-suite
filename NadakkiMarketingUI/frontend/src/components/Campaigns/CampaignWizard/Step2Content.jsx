import React, { useState } from "react";

const contentTypes = [
  { id: "text", name: "Solo Texto", icon: "📝" },
  { id: "image", name: "Imagen", icon: "🖼️" },
  { id: "video", name: "Video", icon: "🎬" },
  { id: "carousel", name: "Carrusel", icon: "📚" }
];

export default function Step2Content({ data, onChange, onGenerateAI }) {
  const [generating, setGenerating] = useState(false);
  const charsRemaining = 2200 - (data.content_text?.length || 0);

  const handleGenerateAI = async () => {
    setGenerating(true);
    try { if (onGenerateAI) await onGenerateAI(); }
    finally { setGenerating(false); }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Contenido de tu publicación</h3>
      <div>
        <label className="block text-sm font-medium mb-2">Tipo de contenido</label>
        <div className="flex gap-3">
          {contentTypes.map((type) => (
            <button key={type.id} type="button" onClick={() => onChange({ content_type: type.id })}
              className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${data.content_type === type.id ? "border-indigo-500 bg-indigo-50" : "border-gray-200"}`}>
              <span>{type.icon}</span><span>{type.name}</span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-sm font-medium">Texto del post</label>
          <button type="button" onClick={handleGenerateAI} disabled={generating} className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-full">
            {generating ? "⏳" : "✨"} Generar con IA
          </button>
        </div>
        <textarea value={data.content_text || ""} onChange={(e) => onChange({ content_text: e.target.value })}
          placeholder="Escribe tu publicación..." rows={5} maxLength={2200}
          className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500" />
        <span className={`text-sm ${charsRemaining < 100 ? "text-orange-500" : "text-gray-400"}`}>{charsRemaining} caracteres</span>
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Hashtags</label>
        <input type="text" value={(data.hashtags || []).map(h => `#${h}`).join(" ")}
          onChange={(e) => onChange({ hashtags: e.target.value.split(/[,\s]+/).map(h => h.replace("#", "").trim()).filter(Boolean) })}
          placeholder="#marketing #ai" className="w-full px-4 py-2 border rounded-lg" />
      </div>
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium mb-3">Vista previa</h4>
        <div className="bg-white p-4 border rounded-lg">
          <p>{data.content_text || "Tu texto aquí..."}</p>
          {data.hashtags?.length > 0 && <p className="text-blue-600 mt-2">{data.hashtags.map(h => `#${h}`).join(" ")}</p>}
        </div>
      </div>
    </div>
  );
}
