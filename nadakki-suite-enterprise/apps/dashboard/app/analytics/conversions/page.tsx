"use client";
export default function AnalyticsConversionsPage() {
  const funnel = [
    { stage: "Visitantes", value: 50000, percentage: 100 },
    { stage: "Leads", value: 2500, percentage: 5 },
    { stage: "MQL", value: 750, percentage: 1.5 },
    { stage: "SQL", value: 225, percentage: 0.45 },
    { stage: "Clientes", value: 68, percentage: 0.14 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🎯 Funnel de Conversión</h1>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {funnel.map((f, i) => (
            <div key={i}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ color: "#f8fafc", fontWeight: 600 }}>{f.stage}</span>
                <span style={{ color: "#8b5cf6" }}>{f.value.toLocaleString()} ({f.percentage}%)</span>
              </div>
              <div style={{ height: 40, backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 8, overflow: "hidden" }}>
                <div style={{ width: `${f.percentage}%`, height: "100%", backgroundColor: "#8b5cf6", minWidth: f.percentage < 1 ? "2%" : undefined }} />
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 32, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
            <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Tasa Lead → MQL</p>
            <p style={{ color: "#22c55e", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>30%</p>
          </div>
          <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
            <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Tasa MQL → SQL</p>
            <p style={{ color: "#f59e0b", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>30%</p>
          </div>
          <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
            <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Tasa SQL → Cliente</p>
            <p style={{ color: "#3b82f6", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>30.2%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
