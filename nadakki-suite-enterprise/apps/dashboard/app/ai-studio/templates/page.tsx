"use client";
export default function AITemplatesPage() {
  const templates = [
    { name: "Launch Post", category: "Social", uses: 234, rating: 4.8 },
    { name: "Promo Email", category: "Email", uses: 189, rating: 4.6 },
    { name: "Product Description", category: "Copy", uses: 456, rating: 4.9 },
    { name: "Ad Copy", category: "Ads", uses: 567, rating: 4.8 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📋 Plantillas IA</h1>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>+ Crear Plantilla</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
        {templates.map((t, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 20 }}>
            <h3 style={{ color: "#f8fafc", fontSize: 16, margin: "0 0 4px 0" }}>{t.name}</h3>
            <span style={{ color: "#8b5cf6", fontSize: 12 }}>{t.category}</span>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
              <span style={{ color: "#f59e0b" }}>⭐ {t.rating}</span>
              <span style={{ color: "#64748b", fontSize: 13 }}>{t.uses} usos</span>
            </div>
            <button style={{ width: "100%", marginTop: 12, padding: 10, backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>Usar →</button>
          </div>
        ))}
      </div>
    </div>
  );
}
