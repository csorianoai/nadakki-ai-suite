"use client";
import { useState } from "react";

const experiments = [
  { id: 1, name: "Landing Page CTA", status: "running", variantA: { name: "Azul", conversions: 234, visitors: 5000 }, variantB: { name: "Verde", conversions: 312, visitors: 5100 }, winner: "B", confidence: 95 },
  { id: 2, name: "Email Subject Line", status: "running", variantA: { name: "Urgencia", conversions: 890, visitors: 12000 }, variantB: { name: "Beneficio", conversions: 756, visitors: 11800 }, winner: "A", confidence: 87 },
  { id: 3, name: "Pricing Display", status: "completed", variantA: { name: "Mensual", conversions: 145, visitors: 3200 }, variantB: { name: "Anual destacado", conversions: 198, visitors: 3100 }, winner: "B", confidence: 99 },
];

export default function ABTestingLabPage() {
  const [tests] = useState(experiments);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🧪 A/B Testing Lab</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Centro de experimentación con ABTestingIA</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Nuevo Experimento
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {tests.map(test => {
          const convA = (test.variantA.conversions / test.variantA.visitors * 100).toFixed(2);
          const convB = (test.variantB.conversions / test.variantB.visitors * 100).toFixed(2);
          
          return (
            <div key={test.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <div>
                  <h3 style={{ color: "#f8fafc", fontSize: 20, fontWeight: 600, margin: 0 }}>{test.name}</h3>
                  <span style={{
                    display: "inline-block", marginTop: 8,
                    backgroundColor: test.status === "running" ? "rgba(34,197,94,0.1)" : "rgba(100,116,139,0.1)",
                    color: test.status === "running" ? "#22c55e" : "#64748b",
                    padding: "4px 12px", borderRadius: 20, fontSize: 12
                  }}>
                    {test.status === "running" ? "🔄 En progreso" : "✓ Completado"}
                  </span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Confianza estadística</p>
                  <p style={{ color: test.confidence >= 95 ? "#22c55e" : "#f59e0b", fontSize: 24, fontWeight: 700, margin: 0 }}>{test.confidence}%</p>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div style={{
                  backgroundColor: test.winner === "A" ? "rgba(34,197,94,0.1)" : "rgba(0,0,0,0.2)",
                  border: test.winner === "A" ? "2px solid #22c55e" : "1px solid rgba(51,65,85,0.5)",
                  borderRadius: 12, padding: 20
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <span style={{ color: "#f8fafc", fontWeight: 600 }}>Variante A: {test.variantA.name}</span>
                    {test.winner === "A" && <span style={{ backgroundColor: "#22c55e", color: "white", padding: "2px 8px", borderRadius: 4, fontSize: 11 }}>GANADOR</span>}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Visitantes</p>
                      <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{test.variantA.visitors.toLocaleString()}</p>
                    </div>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Conversiones</p>
                      <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{test.variantA.conversions}</p>
                    </div>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Tasa</p>
                      <p style={{ color: "#22c55e", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{convA}%</p>
                    </div>
                  </div>
                </div>

                <div style={{
                  backgroundColor: test.winner === "B" ? "rgba(34,197,94,0.1)" : "rgba(0,0,0,0.2)",
                  border: test.winner === "B" ? "2px solid #22c55e" : "1px solid rgba(51,65,85,0.5)",
                  borderRadius: 12, padding: 20
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <span style={{ color: "#f8fafc", fontWeight: 600 }}>Variante B: {test.variantB.name}</span>
                    {test.winner === "B" && <span style={{ backgroundColor: "#22c55e", color: "white", padding: "2px 8px", borderRadius: 4, fontSize: 11 }}>GANADOR</span>}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Visitantes</p>
                      <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{test.variantB.visitors.toLocaleString()}</p>
                    </div>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Conversiones</p>
                      <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{test.variantB.conversions}</p>
                    </div>
                    <div>
                      <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Tasa</p>
                      <p style={{ color: "#22c55e", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{convB}%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
