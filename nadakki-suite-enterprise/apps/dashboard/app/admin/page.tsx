"use client";
import Link from "next/link";

export default function AdminPage() {
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🛠️ Administración</h1>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <Link href="/admin/agents" style={{ textDecoration: "none" }}>
          <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
            <span style={{ fontSize: 32 }}>🤖</span>
            <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>Agentes IA</h3>
            <p style={{ color: "#64748b", margin: 0 }}>Activar/desactivar agentes</p>
          </div>
        </Link>
        <Link href="/admin/logs" style={{ textDecoration: "none" }}>
          <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
            <span style={{ fontSize: 32 }}>📜</span>
            <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>Logs del Sistema</h3>
            <p style={{ color: "#64748b", margin: 0 }}>Historial de decisiones IA</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
