"use client";
import { useState } from "react";

export default function IASettingsPage() {
  const [config, setConfig] = useState({ tone: "professional", creativity: 70, autoPublish: false, language: "es" });

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🤖 Configuración de IA</h1>
      
      <div style={{ maxWidth: 600, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Tono de comunicación</label>
          <select value={config.tone} onChange={e => setConfig({...config, tone: e.target.value})}
            style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }}>
            <option value="professional">Profesional</option>
            <option value="casual">Casual</option>
            <option value="friendly">Amigable</option>
            <option value="formal">Formal</option>
          </select>
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Nivel de creatividad: {config.creativity}%</label>
          <input type="range" min="0" max="100" value={config.creativity} onChange={e => setConfig({...config, creativity: Number(e.target.value)})}
            style={{ width: "100%" }} />
        </div>

        <div style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <p style={{ color: "#f8fafc", margin: 0 }}>Auto-publicar contenido</p>
            <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>Publicar automáticamente contenido aprobado</p>
          </div>
          <button onClick={() => setConfig({...config, autoPublish: !config.autoPublish})}
            style={{ width: 50, height: 26, borderRadius: 13, backgroundColor: config.autoPublish ? "#22c55e" : "rgba(255,255,255,0.2)", border: "none", cursor: "pointer", position: "relative" }}>
            <div style={{ width: 22, height: 22, borderRadius: "50%", backgroundColor: "white", position: "absolute", top: 2, left: config.autoPublish ? 26 : 2, transition: "left 0.2s" }} />
          </button>
        </div>

        <button style={{ width: "100%", padding: 14, backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          💾 Guardar Configuración
        </button>
      </div>
    </div>
  );
}
