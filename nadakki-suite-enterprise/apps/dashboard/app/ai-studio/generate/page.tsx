"use client";
import { useState } from "react";

export default function AIGeneratePage() {
  const [config, setConfig] = useState({ type: "social", platform: "instagram", tone: "professional", prompt: "" });
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState<string[]>([]);

  const generate = async () => {
    setGenerating(true);
    try {
      await fetch("https://nadakki-ai-suite.onrender.com/agents/marketing/contentgeneratoria/execute", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_data: config, tenant_id: "credicefi" })
      });
      setResults([
        "🚀 ¡Transforma tu negocio hoy! Nuestra solución de IA automatiza tu marketing. 💡 Resultados en 7 días. ¿Listo? 👇 #Marketing #AI",
        "¿Sabías que el 73% de las empresas exitosas usan IA? 📊 No te quedes atrás → Link en bio ✨ #Innovacion",
        "ANTES: 8 horas creando contenido 😩\nDESPUÉS: 30 minutos con IA 🎯\n\n👉 Agenda tu demo #ProductividadMaxima"
      ]);
    } finally { setGenerating(false); }
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>✨ Generador de Contenido</h1>
      <div style={{ display: "grid", gridTemplateColumns: "400px 1fr", gap: 24 }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 20 }}>Configuración</h3>
          <div style={{ marginBottom: 16 }}>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 8 }}>Tipo</label>
            <select value={config.type} onChange={e => setConfig({...config, type: e.target.value})}
              style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }}>
              <option value="social">Post Social</option>
              <option value="email">Email</option>
              <option value="blog">Blog</option>
              <option value="ad">Ad Copy</option>
            </select>
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 8 }}>Descripción</label>
            <textarea value={config.prompt} onChange={e => setConfig({...config, prompt: e.target.value})}
              placeholder="Describe el contenido..."
              style={{ width: "100%", minHeight: 100, padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", resize: "vertical" }} />
          </div>
          <button onClick={generate} disabled={generating}
            style={{ width: "100%", padding: 14, backgroundColor: generating ? "#475569" : "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: generating ? "not-allowed" : "pointer" }}>
            {generating ? "⏳ Generando..." : "✨ Generar 3 Variantes"}
          </button>
        </div>

        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 20 }}>Resultados</h3>
          {results.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {results.map((r, i) => (
                <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                    <span style={{ color: "#8b5cf6", fontSize: 13, fontWeight: 600 }}>Variante {i + 1}</span>
                    <button style={{ padding: "6px 12px", backgroundColor: "#22c55e", border: "none", borderRadius: 6, color: "white", cursor: "pointer", fontSize: 12 }}>📅 Programar</button>
                  </div>
                  <p style={{ color: "#f8fafc", fontSize: 14, lineHeight: 1.6, margin: 0, whiteSpace: "pre-wrap" }}>{r}</p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: 80, color: "#64748b" }}>
              <p style={{ fontSize: 48, margin: "0 0 16px 0" }}>✨</p>
              <p>Configura y genera contenido con IA</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
