"use client";
import { useState } from "react";

export default function AISettingsPage() {
  const [settings, setSettings] = useState({ tone: "professional", brandVoice: "", keywords: "" });

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>⚙️ Configuración de IA</h1>
      <div style={{ maxWidth: 600, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Tono por Defecto</label>
          <select value={settings.tone} onChange={e => setSettings({...settings, tone: e.target.value})}
            style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }}>
            <option value="professional">Profesional</option>
            <option value="casual">Casual</option>
            <option value="friendly">Amigable</option>
          </select>
        </div>
        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Voz de Marca</label>
          <textarea value={settings.brandVoice} onChange={e => setSettings({...settings, brandVoice: e.target.value})}
            placeholder="Describe la personalidad de tu marca..."
            style={{ width: "100%", minHeight: 80, padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
        </div>
        <button style={{ width: "100%", padding: 14, backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>💾 Guardar</button>
      </div>
    </div>
  );
}
