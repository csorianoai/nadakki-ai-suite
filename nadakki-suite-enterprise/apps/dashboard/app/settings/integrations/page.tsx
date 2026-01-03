"use client";
export default function IntegrationsPage() {
  const integrations = [
    { name: "Mailchimp", status: "connected", icon: "📧" },
    { name: "HubSpot", status: "disconnected", icon: "🔶" },
    { name: "Google Analytics", status: "connected", icon: "📊" },
    { name: "Zapier", status: "disconnected", icon: "⚡" },
    { name: "Slack", status: "connected", icon: "💬" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🔗 Integraciones</h1>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {integrations.map((i, idx) => (
          <div key={idx} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ fontSize: 28 }}>{i.icon}</span>
              <div>
                <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{i.name}</p>
                <span style={{ color: i.status === "connected" ? "#22c55e" : "#64748b", fontSize: 12 }}>
                  {i.status === "connected" ? "✓ Conectado" : "○ Desconectado"}
                </span>
              </div>
            </div>
            <button style={{ padding: "8px 16px", backgroundColor: i.status === "connected" ? "rgba(239,68,68,0.1)" : "#8b5cf6", border: "none", borderRadius: 8, color: i.status === "connected" ? "#ef4444" : "white", cursor: "pointer" }}>
              {i.status === "connected" ? "Desconectar" : "Conectar"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
