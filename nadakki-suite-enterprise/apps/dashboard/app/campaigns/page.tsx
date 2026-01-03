"use client";
import { useState } from "react";
import Link from "next/link";

export default function CampaignsPage() {
  const stats = [
    { label: "Campañas Activas", value: "12", icon: "🚀", color: "#22c55e" },
    { label: "En Borrador", value: "5", icon: "📝", color: "#f59e0b" },
    { label: "Completadas", value: "34", icon: "✅", color: "#3b82f6" },
    { label: "ROI Promedio", value: "340%", icon: "📈", color: "#8b5cf6" },
  ];

  const campaigns = [
    { id: 1, name: "Black Friday 2026", status: "active", type: "Multi-channel", budget: 15000, spent: 8500, leads: 234, roi: 420 },
    { id: 2, name: "Lanzamiento Q1", status: "active", type: "Social", budget: 8000, spent: 3200, leads: 89, roi: 280 },
    { id: 3, name: "Retargeting Enero", status: "draft", type: "Email", budget: 3000, spent: 0, leads: 0, roi: 0 },
    { id: 4, name: "Brand Awareness", status: "completed", type: "Display", budget: 20000, spent: 20000, leads: 567, roi: 380 },
  ];

  const statusColors: Record<string, string> = { active: "#22c55e", draft: "#f59e0b", completed: "#64748b", paused: "#ef4444" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📢 Centro de Campañas</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Gestiona todas tus campañas de marketing</p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link href="/campaigns/autogen" style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, textDecoration: "none" }}>
            🤖 Auto-Generar con IA
          </Link>
          <Link href="/campaigns/new" style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, textDecoration: "none" }}>
            + Nueva Campaña
          </Link>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {stats.map((s, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div>
                <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{s.label}</p>
                <p style={{ color: "#f8fafc", fontSize: 32, fontWeight: 700, margin: "8px 0 0 0" }}>{s.value}</p>
              </div>
              <span style={{ fontSize: 32 }}>{s.icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
        <Link href="/campaigns/active" style={{ padding: "8px 16px", backgroundColor: "rgba(34,197,94,0.2)", borderRadius: 8, color: "#22c55e", textDecoration: "none" }}>🚀 Activas</Link>
        <Link href="/campaigns/history" style={{ padding: "8px 16px", backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 8, color: "white", textDecoration: "none" }}>📊 Histórico</Link>
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Campaña", "Estado", "Tipo", "Presupuesto", "Gastado", "Leads", "ROI", "Acciones"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {campaigns.map(c => (
              <tr key={c.id} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                <td style={{ padding: 16, color: "#f8fafc", fontWeight: 600 }}>{c.name}</td>
                <td style={{ padding: 16 }}>
                  <span style={{ backgroundColor: `${statusColors[c.status]}20`, color: statusColors[c.status], padding: "4px 12px", borderRadius: 20, fontSize: 12 }}>{c.status}</span>
                </td>
                <td style={{ padding: 16, color: "#94a3b8" }}>{c.type}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>${c.budget.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>${c.spent.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#22c55e", fontWeight: 600 }}>{c.leads}</td>
                <td style={{ padding: 16, color: c.roi > 300 ? "#22c55e" : "#f59e0b", fontWeight: 700 }}>{c.roi}%</td>
                <td style={{ padding: 16 }}>
                  <button style={{ padding: "6px 12px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 6, color: "white", cursor: "pointer", marginRight: 8 }}>Ver</button>
                  <button style={{ padding: "6px 12px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 6, color: "white", cursor: "pointer" }}>✏️</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
