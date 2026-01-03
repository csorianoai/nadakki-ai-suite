import React, { useState } from "react";

const platforms = [
  { id: "facebook", name: "Facebook", icon: "📘" },
  { id: "instagram", name: "Instagram", icon: "📸" },
  { id: "tiktok", name: "TikTok", icon: "🎵" },
  { id: "x", name: "X (Twitter)", icon: "✖️" },
  { id: "linkedin", name: "LinkedIn", icon: "💼" },
  { id: "pinterest", name: "Pinterest", icon: "📌" },
  { id: "youtube", name: "YouTube", icon: "▶️" }
];

export default function ConnectButton({ onConnect, loading }) {
  const [showDropdown, setShowDropdown] = useState(false);

  const handleConnect = async (platformId) => {
    setShowDropdown(false);
    if (onConnect) await onConnect(platformId);
  };

  return (
    <div className="relative">
      <button onClick={() => setShowDropdown(!showDropdown)} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {loading ? "⏳" : "➕"} Conectar Red Social
      </button>
      {showDropdown && (
        <div className="absolute top-full mt-2 right-0 w-56 bg-white rounded-lg shadow-lg border z-50">
          <div className="p-2">
            {platforms.map((p) => (
              <button key={p.id} onClick={() => handleConnect(p.id)} className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded">
                <span className="text-xl">{p.icon}</span>
                <span>{p.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
