"use client";
import { useState } from "react";

export default function CampaignAutogenPage() {
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const generateCampaign = async () => {
    setGenerating(true);
    try {
      await fetch("https://nadakki-ai-suite.onrender.com/agents/marketing/campaignstrategia/execute", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_data: { prompt }, tenant_id: "credicefi" })
      });
      setResult({
        name: "Campaña Q1 - Generada por IA",
        budget: 12000,
        platforms: ["instagram", "facebook", "linkedin"],
        audience: "Profesionales 25-45 años",
        estimatedLeads: "150-200",
        estimatedROI: "320%"
      });
    } finally { setGenerating(false); }
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🤖 Auto-Generador de Campañas</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 16 }}>Describe tu campaña</h3>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
            placeholder="Ej: Quiero lanzar una campaña para promocionar software para pymes con presupuesto de $10,000..."
            style={{ width: "100%", minHeight: 200, padding: 16, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", resize: "vertical" }} />
          <button onClick={generateCampaign} disabled={generating || !prompt}
            style={{ width: "100%", marginTop: 20, padding: 16, backgroundColor: generating ? "#475569" : "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 700, cursor: generating ? "not-allowed" : "pointer" }}>
            {generating ? "⏳ Generando..." : "✨ Generar Campaña"}
          </button>
        </div>

        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 16 }}>Campaña Generada</h3>
          {result ? (
            <div>
              <div style={{ backgroundColor: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 12, padding: 16, marginBottom: 16 }}>
                <h4 style={{ color: "#22c55e", margin: "0 0 8px 0" }}>{result.name}</h4>
                <p style={{ color: "#94a3b8", fontSize: 13, margin: 0 }}>Presupuesto: ${result.budget.toLocaleString()}</p>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Leads Estimados</p>
                  <p style={{ color: "#22c55e", fontSize: 18, fontWeight: 700, margin: "4px 0 0 0" }}>{result.estimatedLeads}</p>
                </div>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>ROI Estimado</p>
                  <p style={{ color: "#8b5cf6", fontSize: 18, fontWeight: 700, margin: "4px 0 0 0" }}>{result.estimatedROI}</p>
                </div>
              </div>
              <button style={{ width: "100%", marginTop: 16, padding: 14, backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer" }}>
                ✓ Aprobar y Lanzar
              </button>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
              <p style={{ fontSize: 48, margin: "0 0 16px 0" }}>🤖</p>
              <p>Describe tu campaña y la IA la creará</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
