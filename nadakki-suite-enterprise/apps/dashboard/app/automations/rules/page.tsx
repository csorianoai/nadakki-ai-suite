"use client";
import { useState } from "react";
export default function AutomationsPage() {
  const [rules] = useState([
    { id: 1, name: "Lead Score > 80 → Notify Sales", status: "active", triggers: 45, lastRun: "Hace 10 min" },
    { id: 2, name: "New Follower → Welcome DM", status: "active", triggers: 234, lastRun: "Hace 2 min" },
    { id: 3, name: "Negative Mention → Alert Team", status: "active", triggers: 12, lastRun: "Hace 1 hora" },
    { id: 4, name: "Cart Abandoned → Email Sequence", status: "paused", triggers: 89, lastRun: "Hace 2 días" },
  ]);
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>⚡ Automations</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Reglas y triggers automáticos</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>+ Nueva Regla</button>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {rules.map(rule => (
          <div key={rule.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: rule.status === "active" ? "#22c55e" : "#64748b" }} />
              <div>
                <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{rule.name}</p>
                <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>Ejecutado {rule.triggers} veces • {rule.lastRun}</p>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button style={{ padding: "8px 16px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 6, color: "white", cursor: "pointer" }}>✏️</button>
              <button style={{ padding: "8px 16px", backgroundColor: rule.status === "active" ? "rgba(239,68,68,0.1)" : "rgba(34,197,94,0.1)", border: "none", borderRadius: 6, color: rule.status === "active" ? "#ef4444" : "#22c55e", cursor: "pointer" }}>
                {rule.status === "active" ? "⏸️" : "▶️"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
