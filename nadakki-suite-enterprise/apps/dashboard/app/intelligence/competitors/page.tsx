"use client";
import { useState } from "react";

const competitors = [
  { id: 1, name: "CompetitorA", logo: "🏢", followers: { instagram: "125K", x: "89K", linkedin: "45K" }, sentiment: 72, mentions: 234, trend: "up" },
  { id: 2, name: "CompetitorB", logo: "🏬", followers: { instagram: "98K", x: "156K", linkedin: "67K" }, sentiment: 65, mentions: 189, trend: "down" },
  { id: 3, name: "CompetitorC", logo: "🏭", followers: { instagram: "234K", x: "45K", linkedin: "123K" }, sentiment: 81, mentions: 456, trend: "up" },
];

export default function CompetitiveIntelPage() {
  const [data] = useState(competitors);
  const [analyzing, setAnalyzing] = useState(false);

  const runAnalysis = async () => {
    setAnalyzing(true);
    await fetch("https://nadakki-ai-suite.onrender.com/agents/marketing/competitoranalyzeria/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_data: { competitors: data.map(c => c.name) }, tenant_id: "credicefi" })
    });
    setTimeout(() => setAnalyzing(false), 2000);
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🔍 Competitive Intelligence</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Monitor de competencia con CompetitorAnalyzerIA</p>
        </div>
        <button onClick={runAnalysis} disabled={analyzing} style={{
          padding: "12px 24px", backgroundColor: analyzing ? "#475569" : "#ef4444",
          border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: analyzing ? "not-allowed" : "pointer"
        }}>
          {analyzing ? "⏳ Analizando..." : "🔄 Actualizar Análisis"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
        {data.map(comp => (
          <div key={comp.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
              <span style={{ fontSize: 48 }}>{comp.logo}</span>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 20, fontWeight: 600, margin: 0 }}>{comp.name}</h3>
                <span style={{ color: comp.trend === "up" ? "#22c55e" : "#ef4444", fontSize: 13 }}>
                  {comp.trend === "up" ? "📈 Creciendo" : "📉 Bajando"}
                </span>
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <p style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>Seguidores</p>
              <div style={{ display: "flex", gap: 12 }}>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 8, borderRadius: 8, textAlign: "center", flex: 1 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>📸 IG</p>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: "4px 0 0 0" }}>{comp.followers.instagram}</p>
                </div>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 8, borderRadius: 8, textAlign: "center", flex: 1 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>🐦 X</p>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: "4px 0 0 0" }}>{comp.followers.x}</p>
                </div>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 8, borderRadius: 8, textAlign: "center", flex: 1 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>💼 LI</p>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: "4px 0 0 0" }}>{comp.followers.linkedin}</p>
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Sentimiento</p>
                <p style={{ color: comp.sentiment >= 70 ? "#22c55e" : "#f59e0b", fontSize: 24, fontWeight: 700, margin: "4px 0 0 0" }}>{comp.sentiment}%</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Menciones/día</p>
                <p style={{ color: "#3b82f6", fontSize: 24, fontWeight: 700, margin: "4px 0 0 0" }}>{comp.mentions}</p>
              </div>
            </div>

            <button style={{ width: "100%", marginTop: 16, padding: 12, backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>
              Ver Análisis Detallado →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
