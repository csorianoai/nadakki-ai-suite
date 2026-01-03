"use client";
import { useState } from "react";

const socialNetworks = [
  { id: "meta", name: "Meta (Facebook/Instagram)", icon: "📘", color: "#1877F2", status: "disconnected" },
  { id: "x", name: "X (Twitter)", icon: "🐦", color: "#000000", status: "disconnected" },
  { id: "tiktok", name: "TikTok", icon: "🎵", color: "#000000", status: "disconnected" },
  { id: "linkedin", name: "LinkedIn", icon: "💼", color: "#0A66C2", status: "disconnected" },
  { id: "pinterest", name: "Pinterest", icon: "📌", color: "#E60023", status: "disconnected" },
  { id: "youtube", name: "YouTube", icon: "▶️", color: "#FF0000", status: "disconnected" },
  { id: "whatsapp", name: "WhatsApp Business", icon: "💬", color: "#25D366", status: "disconnected" },
];

export default function SocialConnectionsPage() {
  const [networks, setNetworks] = useState(socialNetworks);
  const [connecting, setConnecting] = useState<string | null>(null);

  const connectNetwork = async (networkId: string) => {
    setConnecting(networkId);
    // Simular conexión OAuth
    setTimeout(() => {
      setNetworks(prev => prev.map(n => 
        n.id === networkId ? { ...n, status: "connected" } : n
      ));
      setConnecting(null);
    }, 2000);
  };

  const disconnectNetwork = (networkId: string) => {
    setNetworks(prev => prev.map(n => 
      n.id === networkId ? { ...n, status: "disconnected" } : n
    ));
  };

  const connectedCount = networks.filter(n => n.status === "connected").length;

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🔗 Conexiones de Redes Sociales</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>{connectedCount} de {networks.length} redes conectadas</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 20 }}>
        {networks.map((network) => (
          <div key={network.id} style={{
            backgroundColor: "rgba(30,41,59,0.5)",
            border: `2px solid ${network.status === "connected" ? "#22c55e" : "rgba(51,65,85,0.5)"}`,
            borderRadius: 16,
            padding: 24,
            transition: "all 0.3s"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
              <div style={{ fontSize: 40 }}>{network.icon}</div>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: 0 }}>{network.name}</h3>
                <p style={{ 
                  color: network.status === "connected" ? "#22c55e" : "#ef4444",
                  fontSize: 13,
                  margin: "4px 0 0 0",
                  fontWeight: 500
                }}>
                  {network.status === "connected" ? "✓ Conectado" : "○ Desconectado"}
                </p>
              </div>
            </div>

            {network.status === "connected" ? (
              <div>
                <div style={{ backgroundColor: "rgba(34,197,94,0.1)", borderRadius: 8, padding: 12, marginBottom: 12 }}>
                  <p style={{ color: "#22c55e", fontSize: 12, margin: 0 }}>Cuenta: @nadakki_oficial</p>
                  <p style={{ color: "#64748b", fontSize: 11, margin: "4px 0 0 0" }}>Conectado hace 2 días</p>
                </div>
                <button onClick={() => disconnectNetwork(network.id)} style={{
                  width: "100%", padding: 12, backgroundColor: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8,
                  color: "#ef4444", fontWeight: 600, cursor: "pointer"
                }}>
                  Desconectar
                </button>
              </div>
            ) : (
              <button onClick={() => connectNetwork(network.id)} disabled={connecting === network.id} style={{
                width: "100%", padding: 14,
                backgroundColor: connecting === network.id ? "#475569" : network.color,
                border: "none", borderRadius: 8,
                color: "white", fontWeight: 600, fontSize: 14,
                cursor: connecting === network.id ? "not-allowed" : "pointer"
              }}>
                {connecting === network.id ? "⏳ Conectando..." : "🔗 Conectar con OAuth"}
              </button>
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 40, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
        <h2 style={{ color: "#f8fafc", fontSize: 20, marginBottom: 16 }}>📋 Adaptadores Disponibles</h2>
        <p style={{ color: "#94a3b8", fontSize: 14, marginBottom: 16 }}>
          Ubicación: <code style={{ backgroundColor: "rgba(0,0,0,0.3)", padding: "2px 8px", borderRadius: 4 }}>NadakkiSocialAdapters/adapters/</code>
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
          {["meta_adapter.py", "x_adapter.py", "tiktok_adapter.py", "linkedin_adapter.py", "pinterest_adapter.py", "youtube_adapter.py"].map(file => (
            <div key={file} style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
              <code style={{ color: "#22c55e", fontSize: 13 }}>✓ {file}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
