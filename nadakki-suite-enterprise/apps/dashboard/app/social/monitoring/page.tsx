"use client";
import { useState } from "react";

export default function SocialMonitoringPage() {
  const [feed] = useState([
    { platform: "instagram", type: "comment", user: "@maria_garcia", content: "Me encanta este producto!", time: "Hace 5 min", sentiment: "positive" },
    { platform: "x", type: "mention", user: "@tech_news", content: "Gran artículo de @nadakki sobre IA", time: "Hace 12 min", sentiment: "positive" },
    { platform: "facebook", type: "comment", user: "Carlos López", content: "¿Cuándo estará disponible en mi país?", time: "Hace 25 min", sentiment: "neutral" },
    { platform: "linkedin", type: "share", user: "Ana CEO", content: "Compartió tu publicación", time: "Hace 1 hora", sentiment: "positive" },
    { platform: "tiktok", type: "comment", user: "@viral_content", content: "🔥🔥🔥", time: "Hace 2 horas", sentiment: "positive" },
  ]);

  const platformIcons: Record<string, string> = { instagram: "📸", x: "🐦", facebook: "📘", linkedin: "💼", tiktok: "🎵" };
  const sentimentColors: Record<string, string> = { positive: "#22c55e", negative: "#ef4444", neutral: "#64748b" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 8 }}>📡 Social Monitoring</h1>
      <p style={{ color: "#94a3b8", marginBottom: 32 }}>Engagement en tiempo real • {feed.length} interacciones recientes</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16, marginBottom: 32 }}>
        {Object.entries(platformIcons).map(([p, icon]) => (
          <div key={p} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16, textAlign: "center" }}>
            <span style={{ fontSize: 28 }}>{icon}</span>
            <p style={{ color: "#f8fafc", fontSize: 20, fontWeight: 700, margin: "8px 0 4px 0" }}>{feed.filter(f => f.platform === p).length}</p>
            <p style={{ color: "#64748b", fontSize: 12, margin: 0, textTransform: "capitalize" }}>{p}</p>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
        <h2 style={{ color: "#f8fafc", fontSize: 18, marginBottom: 20 }}>Feed en Tiempo Real</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {feed.map((f, i) => (
            <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                <span style={{ fontSize: 24 }}>{platformIcons[f.platform]}</span>
                <div>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{f.user}</p>
                  <p style={{ color: "#94a3b8", fontSize: 13, margin: "4px 0 0 0" }}>{f.content}</p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <span style={{ color: "#64748b", fontSize: 12 }}>{f.time}</span>
                <span style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: sentimentColors[f.sentiment] }} />
                <button style={{ padding: "6px 12px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 6, color: "white", cursor: "pointer", fontSize: 12 }}>Responder</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
