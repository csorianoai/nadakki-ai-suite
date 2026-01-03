"use client";
export default function CampaignHistoryPage() {
  const history = [
    { name: "Cyber Monday 2025", dates: "Nov 25 - Dic 2", budget: 25000, leads: 890, roi: 520, status: "success" },
    { name: "Summer Sale", dates: "Jul 1 - Jul 15", budget: 15000, leads: 450, roi: 280, status: "success" },
    { name: "Spring Promo", dates: "Mar 1 - Mar 15", budget: 8000, leads: 120, roi: 85, status: "underperformed" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📊 Histórico de Campañas</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {history.map((c, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 20, margin: 0 }}>{c.name}</h3>
                <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{c.dates}</p>
              </div>
              <span style={{ backgroundColor: c.status === "success" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)",
                color: c.status === "success" ? "#22c55e" : "#ef4444", padding: "6px 14px", borderRadius: 20, fontSize: 12 }}>
                {c.status === "success" ? "✓ Exitosa" : "⚠ Bajo rendimiento"}
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Presupuesto</p>
                <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>${c.budget.toLocaleString()}</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Leads</p>
                <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{c.leads}</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>ROI</p>
                <p style={{ color: c.roi > 200 ? "#22c55e" : "#f59e0b", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{c.roi}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
