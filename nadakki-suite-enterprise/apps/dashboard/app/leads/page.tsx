"use client";
import Link from "next/link";

export default function LeadsPage() {
  const stats = [
    { label: "Total Leads", value: "1,247", color: "#3b82f6" },
    { label: "Hot Leads", value: "234", color: "#ef4444" },
    { label: "Warm Leads", value: "567", color: "#f59e0b" },
    { label: "Cold Leads", value: "446", color: "#64748b" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>👥 Gestión de Leads</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {stats.map((s, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 20 }}>
            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{s.label}</p>
            <p style={{ color: s.color, fontSize: 32, fontWeight: 700, margin: "8px 0 0 0" }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <Link href="/leads/scoring" style={{ textDecoration: "none" }}>
          <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
            <span style={{ fontSize: 32 }}>🎯</span>
            <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>Lead Scoring</h3>
            <p style={{ color: "#64748b", margin: 0 }}>Puntuación automática con IA</p>
          </div>
        </Link>
        <Link href="/leads/pipeline" style={{ textDecoration: "none" }}>
          <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
            <span style={{ fontSize: 32 }}>🚀</span>
            <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>Pipeline</h3>
            <p style={{ color: "#64748b", margin: 0 }}>Visualización Kanban</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
