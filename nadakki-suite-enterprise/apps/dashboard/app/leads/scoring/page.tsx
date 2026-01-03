"use client";
import { useState, useEffect } from "react";

export default function LeadScoringPage() {
  const [leads, setLeads] = useState([
    { id: 1, name: "María García", company: "TechCorp", email: "maria@techcorp.com", score: 92, status: "hot", source: "LinkedIn", lastActivity: "Hace 2 horas" },
    { id: 2, name: "Carlos López", company: "StartupXYZ", email: "carlos@startupxyz.com", score: 78, status: "warm", source: "Website", lastActivity: "Hace 1 día" },
    { id: 3, name: "Ana Martínez", company: "BigEnterprise", email: "ana@bigent.com", score: 85, status: "hot", source: "Referral", lastActivity: "Hace 5 horas" },
    { id: 4, name: "Pedro Sánchez", company: "MidMarket Inc", email: "pedro@midmarket.com", score: 45, status: "cold", source: "Facebook Ad", lastActivity: "Hace 5 días" },
    { id: 5, name: "Laura Torres", company: "InnovateCo", email: "laura@innovate.co", score: 67, status: "warm", source: "Webinar", lastActivity: "Hace 12 horas" },
  ]);

  const [processing, setProcessing] = useState(false);

  const runLeadScoring = async () => {
    setProcessing(true);
    try {
      await fetch("https://nadakki-ai-suite.onrender.com/agents/marketing/leadscoringia/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_data: { leads: leads.map(l => l.id) }, tenant_id: "credicefi" })
      });
      // Simular actualización de scores
      setLeads(prev => prev.map(l => ({ ...l, score: Math.min(100, l.score + Math.floor(Math.random() * 10)) })));
    } finally {
      setProcessing(false);
    }
  };

  const statusColors: Record<string, string> = { hot: "#ef4444", warm: "#f59e0b", cold: "#3b82f6" };
  const getScoreColor = (score: number) => score >= 80 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎯 Lead Scoring</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Puntuación automática con LeadScoringIA</p>
        </div>
        <button onClick={runLeadScoring} disabled={processing} style={{
          padding: "12px 24px", backgroundColor: processing ? "#475569" : "#22c55e",
          border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: processing ? "not-allowed" : "pointer"
        }}>
          {processing ? "⏳ Procesando..." : "🤖 Ejecutar Lead Scoring"}
        </button>
      </div>

      {/* Score Distribution */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 32 }}>
        {[
          { label: "Hot Leads (80+)", count: leads.filter(l => l.score >= 80).length, color: "#ef4444", icon: "🔥" },
          { label: "Warm Leads (50-79)", count: leads.filter(l => l.score >= 50 && l.score < 80).length, color: "#f59e0b", icon: "☀️" },
          { label: "Cold Leads (<50)", count: leads.filter(l => l.score < 50).length, color: "#3b82f6", icon: "❄️" },
        ].map((stat, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: `2px solid ${stat.color}40`, borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ color: "#94a3b8", fontSize: 14, margin: 0 }}>{stat.label}</p>
                <p style={{ color: "#f8fafc", fontSize: 36, fontWeight: 700, margin: "8px 0 0 0" }}>{stat.count}</p>
              </div>
              <span style={{ fontSize: 40 }}>{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Leads Table */}
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Lead", "Empresa", "Score", "Status", "Fuente", "Última Actividad", "Acciones"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13, fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {leads.sort((a, b) => b.score - a.score).map(lead => (
              <tr key={lead.id} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                <td style={{ padding: 16 }}>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{lead.name}</p>
                  <p style={{ color: "#64748b", fontSize: 12, margin: "4px 0 0 0" }}>{lead.email}</p>
                </td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{lead.company}</td>
                <td style={{ padding: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 60, height: 8, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 4 }}>
                      <div style={{ width: `${lead.score}%`, height: "100%", backgroundColor: getScoreColor(lead.score), borderRadius: 4 }} />
                    </div>
                    <span style={{ color: getScoreColor(lead.score), fontWeight: 700 }}>{lead.score}</span>
                  </div>
                </td>
                <td style={{ padding: 16 }}>
                  <span style={{ backgroundColor: `${statusColors[lead.status]}20`, color: statusColors[lead.status], padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600, textTransform: "uppercase" }}>
                    {lead.status}
                  </span>
                </td>
                <td style={{ padding: 16, color: "#94a3b8" }}>{lead.source}</td>
                <td style={{ padding: 16, color: "#64748b", fontSize: 13 }}>{lead.lastActivity}</td>
                <td style={{ padding: 16 }}>
                  <button style={{ padding: "6px 12px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 6, color: "white", cursor: "pointer" }}>Ver Perfil</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
