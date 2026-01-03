"use client";
import { useState } from "react";

export default function NotificationSettingsPage() {
  const [settings, setSettings] = useState({
    email: true, push: true, slack: false, leads: true, campaigns: true, mentions: true
  });

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🔔 Configuración de Notificaciones</h1>
      <div style={{ maxWidth: 600, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <h3 style={{ color: "#f8fafc", marginBottom: 24 }}>Canales</h3>
        {[
          { key: "email", label: "Email" },
          { key: "push", label: "Push Notifications" },
          { key: "slack", label: "Slack" },
        ].map(item => (
          <div key={item.key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <span style={{ color: "#f8fafc" }}>{item.label}</span>
            <button onClick={() => setSettings({...settings, [item.key]: !settings[item.key as keyof typeof settings]})}
              style={{ width: 50, height: 26, borderRadius: 13, backgroundColor: settings[item.key as keyof typeof settings] ? "#22c55e" : "rgba(255,255,255,0.2)", border: "none", cursor: "pointer", position: "relative" }}>
              <div style={{ width: 22, height: 22, borderRadius: "50%", backgroundColor: "white", position: "absolute", top: 2, left: settings[item.key as keyof typeof settings] ? 26 : 2, transition: "left 0.2s" }} />
            </button>
          </div>
        ))}

        <h3 style={{ color: "#f8fafc", marginTop: 32, marginBottom: 24 }}>Tipos de Alertas</h3>
        {[
          { key: "leads", label: "Nuevos Leads" },
          { key: "campaigns", label: "Campañas" },
          { key: "mentions", label: "Menciones de Marca" },
        ].map(item => (
          <div key={item.key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <span style={{ color: "#f8fafc" }}>{item.label}</span>
            <button onClick={() => setSettings({...settings, [item.key]: !settings[item.key as keyof typeof settings]})}
              style={{ width: 50, height: 26, borderRadius: 13, backgroundColor: settings[item.key as keyof typeof settings] ? "#22c55e" : "rgba(255,255,255,0.2)", border: "none", cursor: "pointer", position: "relative" }}>
              <div style={{ width: 22, height: 22, borderRadius: "50%", backgroundColor: "white", position: "absolute", top: 2, left: settings[item.key as keyof typeof settings] ? 26 : 2, transition: "left 0.2s" }} />
            </button>
          </div>
        ))}

        <button style={{ width: "100%", marginTop: 24, padding: 14, backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          💾 Guardar Preferencias
        </button>
      </div>
    </div>
  );
}
