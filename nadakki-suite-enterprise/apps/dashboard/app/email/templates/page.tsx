"use client";
export default function EmailTemplatesPage() {
  const templates = [
    { name: "Welcome Series", category: "Onboarding", uses: 1234, conversion: "45%" },
    { name: "Product Launch", category: "Promotional", uses: 567, conversion: "32%" },
    { name: "Re-engagement", category: "Retention", uses: 890, conversion: "28%" },
    { name: "Newsletter", category: "Content", uses: 2345, conversion: "18%" },
  ];
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📧 Email Templates</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Plantillas optimizadas para conversión</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>+ Nueva Plantilla</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {templates.map((t, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <div style={{ height: 120, backgroundColor: "rgba(139,92,246,0.1)", borderRadius: 8, marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 40 }}>✉️</span>
            </div>
            <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, margin: "0 0 4px 0" }}>{t.name}</h3>
            <p style={{ color: "#64748b", fontSize: 12, margin: "0 0 12px 0" }}>{t.category}</p>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#94a3b8", fontSize: 12 }}>{t.uses} usos</span>
              <span style={{ color: "#22c55e", fontSize: 12, fontWeight: 600 }}>{t.conversion} conv.</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
