"use client";
export default function ExportPage() {
  const exports = [
    { name: "Reporte Campañas Q4", format: "PDF", size: "2.4 MB", date: "Hace 2 días" },
    { name: "Leads Export", format: "CSV", size: "1.1 MB", date: "Hace 1 semana" },
    { name: "Analytics Dashboard", format: "Excel", size: "3.8 MB", date: "Hace 3 días" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📤 Centro de Exportación</h1>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Nueva Exportación
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 32 }}>
        {["PDF", "Excel", "CSV"].map(f => (
          <div key={f} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 20, textAlign: "center", cursor: "pointer" }}>
            <span style={{ fontSize: 32 }}>{f === "PDF" ? "📄" : f === "Excel" ? "📊" : "📋"}</span>
            <p style={{ color: "#f8fafc", fontWeight: 600, margin: "8px 0 0 0" }}>Exportar a {f}</p>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
        <h3 style={{ color: "#f8fafc", marginBottom: 16 }}>Exportaciones Recientes</h3>
        {exports.map((e, i) => (
          <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 8, padding: 16, marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{e.name}</p>
              <p style={{ color: "#64748b", fontSize: 12, margin: "4px 0 0 0" }}>{e.format} • {e.size} • {e.date}</p>
            </div>
            <button style={{ padding: "8px 16px", backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>⬇️ Descargar</button>
          </div>
        ))}
      </div>
    </div>
  );
}
