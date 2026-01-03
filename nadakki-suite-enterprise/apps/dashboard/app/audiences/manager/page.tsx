"use client";
export default function AudienceManagerPage() {
  const audiences = [
    { name: "High-Value Customers", size: "12,450", criteria: "LTV > $1000", lastUpdated: "Hace 1 hora" },
    { name: "Engaged Subscribers", size: "45,230", criteria: "Open rate > 50%", lastUpdated: "Hace 2 horas" },
    { name: "At-Risk Customers", size: "3,120", criteria: "No activity 30+ days", lastUpdated: "Hace 30 min" },
    { name: "New Leads This Month", size: "890", criteria: "Created date = this month", lastUpdated: "Hace 15 min" },
  ];
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>👥 Audience Manager</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Segmentación con AudienceSegmenterIA</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>+ Crear Audiencia</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
        {audiences.map((a, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: 0 }}>{a.name}</h3>
              <span style={{ color: "#8b5cf6", fontSize: 24, fontWeight: 700 }}>{a.size}</span>
            </div>
            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>Criterio: {a.criteria}</p>
            <p style={{ color: "#64748b", fontSize: 12, margin: "8px 0 0 0" }}>Actualizado: {a.lastUpdated}</p>
            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              <button style={{ flex: 1, padding: 10, backgroundColor: "#8b5cf6", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>📢 Crear Campaña</button>
              <button style={{ padding: 10, backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>✏️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
