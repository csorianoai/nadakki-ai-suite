"use client";
import { useState } from "react";

export default function NewJobPage() {
  const [job, setJob] = useState({ name: "", action: "", schedule: "daily", time: "09:00" });

  const actions = [
    { id: "social_post", name: "Publicar en Redes", icon: "📱" },
    { id: "email_send", name: "Enviar Email", icon: "✉️" },
    { id: "lead_score", name: "Actualizar Lead Scores", icon: "🎯" },
    { id: "report_gen", name: "Generar Reporte", icon: "📊" },
    { id: "competitor", name: "Análisis Competencia", icon: "🔍" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>+ Nueva Automatización</h1>
      
      <div style={{ maxWidth: 600, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Nombre</label>
          <input value={job.name} onChange={e => setJob({...job, name: e.target.value})}
            placeholder="Ej: Daily Instagram Post"
            style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Acción</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
            {actions.map(a => (
              <button key={a.id} onClick={() => setJob({...job, action: a.id})}
                style={{ padding: 16, backgroundColor: job.action === a.id ? "#8b5cf6" : "rgba(0,0,0,0.2)",
                  border: "none", borderRadius: 8, color: "white", cursor: "pointer", textAlign: "left" }}>
                <span style={{ fontSize: 20 }}>{a.icon}</span>
                <p style={{ margin: "8px 0 0 0", fontSize: 14 }}>{a.name}</p>
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
          <div>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Frecuencia</label>
            <select value={job.schedule} onChange={e => setJob({...job, schedule: e.target.value})}
              style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }}>
              <option value="hourly">Cada hora</option>
              <option value="daily">Diario</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensual</option>
            </select>
          </div>
          <div>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Hora</label>
            <input type="time" value={job.time} onChange={e => setJob({...job, time: e.target.value})}
              style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
          </div>
        </div>

        <button style={{ width: "100%", padding: 14, backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          ✓ Crear Automatización
        </button>
      </div>
    </div>
  );
}
