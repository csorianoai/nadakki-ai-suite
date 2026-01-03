"use client";
import Link from "next/link";

export default function SchedulerPage() {
  const stats = { queued: 24, running: 3, completed: 156, failed: 2 };
  
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>⏱️ Scheduler Central</h1>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {[
          { label: "En Cola", value: stats.queued, color: "#3b82f6" },
          { label: "Ejecutando", value: stats.running, color: "#22c55e" },
          { label: "Completados", value: stats.completed, color: "#8b5cf6" },
          { label: "Fallidos", value: stats.failed, color: "#ef4444" },
        ].map((s, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 20 }}>
            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{s.label}</p>
            <p style={{ color: s.color, fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 16 }}>
        <Link href="/scheduler/jobs" style={{ flex: 1, padding: 24, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, textDecoration: "none" }}>
          <h3 style={{ color: "#f8fafc", margin: "0 0 8px 0" }}>📋 Ver Trabajos</h3>
          <p style={{ color: "#64748b", margin: 0 }}>Lista de tareas programadas</p>
        </Link>
        <Link href="/scheduler/new-job" style={{ flex: 1, padding: 24, backgroundColor: "rgba(139,92,246,0.2)", borderRadius: 16, textDecoration: "none" }}>
          <h3 style={{ color: "#8b5cf6", margin: "0 0 8px 0" }}>+ Nueva Automatización</h3>
          <p style={{ color: "#64748b", margin: 0 }}>Crear tarea recurrente</p>
        </Link>
      </div>
    </div>
  );
}
