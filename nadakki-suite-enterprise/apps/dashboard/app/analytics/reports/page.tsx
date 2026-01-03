"use client";
export default function ReportsHubPage() {
  const reports = [
    { name: "Reporte Semanal Marketing", type: "PDF", generated: "Hace 2 días", size: "2.4 MB" },
    { name: "Análisis de Campañas Q4", type: "Excel", generated: "Hace 1 semana", size: "5.1 MB" },
    { name: "ROI por Canal", type: "PDF", generated: "Hace 3 días", size: "1.8 MB" },
  ];
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📑 Reports Hub</h1>
      <div style={{ display: "grid", gap: 16 }}>
        {reports.map((r, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{r.name}</p>
              <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{r.type} • {r.size} • {r.generated}</p>
            </div>
            <button style={{ padding: "10px 20px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>⬇️ Descargar</button>
          </div>
        ))}
      </div>
      <button style={{ marginTop: 24, padding: "14px 28px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>+ Generar Nuevo Reporte</button>
    </div>
  );
}
