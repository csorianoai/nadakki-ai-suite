"use client";
import { useState } from "react";

const mentions = [
  { id: 1, platform: "x", user: "@tech_news", content: "Increíble el nuevo producto de @nadakki! 🔥", sentiment: "positive", reach: "45K", time: "Hace 15 min" },
  { id: 2, platform: "instagram", user: "@lifestyle_blogger", content: "Probando la solución de Nadakki para mi negocio", sentiment: "positive", reach: "23K", time: "Hace 1 hora" },
  { id: 3, platform: "linkedin", user: "CEO de TechCorp", content: "Recomiendo Nadakki para automatización de marketing", sentiment: "positive", reach: "12K", time: "Hace 2 horas" },
  { id: 4, platform: "facebook", user: "Usuario Anónimo", content: "Tuve problemas con el soporte de Nadakki...", sentiment: "negative", reach: "500", time: "Hace 3 horas" },
];

export default function BrandMonitorPage() {
  const [data] = useState(mentions);

  const sentimentColors: Record<string, string> = { positive: "#22c55e", negative: "#ef4444", neutral: "#64748b" };
  const platformIcons: Record<string, string> = { x: "🐦", instagram: "📸", linkedin: "💼", facebook: "📘" };

  const positiveCount = data.filter(m => m.sentiment === "positive").length;
  const sentimentScore = Math.round((positiveCount / data.length) * 100);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>👁️ Brand Monitor</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>Monitoreo de menciones con SentimentAnalyzerIA</p>
      </div>

      {/* Overview */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
          <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>Menciones Hoy</p>
          <p style={{ color: "#f8fafc", fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>{data.length}</p>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
          <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>Sentimiento General</p>
          <p style={{ color: sentimentScore >= 70 ? "#22c55e" : "#f59e0b", fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>{sentimentScore}%</p>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
          <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>Alcance Total</p>
          <p style={{ color: "#3b82f6", fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>80.5K</p>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
          <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>Alertas</p>
          <p style={{ color: "#ef4444", fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>1</p>
        </div>
      </div>

      {/* Mentions Feed */}
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
        <h2 style={{ color: "#f8fafc", fontSize: 18, marginBottom: 20 }}>📢 Feed de Menciones</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {data.map(mention => (
            <div key={mention.id} style={{
              backgroundColor: mention.sentiment === "negative" ? "rgba(239,68,68,0.1)" : "rgba(0,0,0,0.2)",
              border: mention.sentiment === "negative" ? "1px solid rgba(239,68,68,0.3)" : "1px solid rgba(51,65,85,0.3)",
              borderRadius: 12, padding: 16
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ display: "flex", gap: 12 }}>
                  <span style={{ fontSize: 24 }}>{platformIcons[mention.platform]}</span>
                  <div>
                    <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{mention.user}</p>
                    <p style={{ color: "#94a3b8", fontSize: 14, margin: "8px 0 0 0", lineHeight: 1.5 }}>{mention.content}</p>
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span style={{
                    backgroundColor: `${sentimentColors[mention.sentiment]}20`,
                    color: sentimentColors[mention.sentiment],
                    padding: "4px 10px", borderRadius: 20, fontSize: 11
                  }}>
                    {mention.sentiment === "positive" ? "😊 Positivo" : mention.sentiment === "negative" ? "😟 Negativo" : "😐 Neutral"}
                  </span>
                  <p style={{ color: "#64748b", fontSize: 12, margin: "8px 0 0 0" }}>{mention.time}</p>
                  <p style={{ color: "#3b82f6", fontSize: 12, margin: "4px 0 0 0" }}>👁️ {mention.reach} alcance</p>
                </div>
              </div>
              {mention.sentiment === "negative" && (
                <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                  <button style={{ padding: "6px 12px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 6, color: "white", cursor: "pointer", fontSize: 12 }}>🤖 Responder con IA</button>
                  <button style={{ padding: "6px 12px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 6, color: "white", cursor: "pointer", fontSize: 12 }}>📋 Crear ticket</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
