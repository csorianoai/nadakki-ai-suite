"use client";
import { useState } from "react";

const mockCampaigns = [
  { id: 1, name: "Welcome Series", status: "active", sent: 12500, opened: 8750, clicked: 2100, converted: 450, openRate: 70, clickRate: 16.8 },
  { id: 2, name: "Product Launch", status: "completed", sent: 45000, opened: 22500, clicked: 6750, converted: 890, openRate: 50, clickRate: 15 },
  { id: 3, name: "Re-engagement", status: "draft", sent: 0, opened: 0, clicked: 0, converted: 0, openRate: 0, clickRate: 0 },
  { id: 4, name: "Newsletter Enero", status: "scheduled", sent: 0, opened: 0, clicked: 0, converted: 0, openRate: 0, clickRate: 0 },
];

export default function EmailCampaignsPage() {
  const [campaigns] = useState(mockCampaigns);
  const statusColors: Record<string, string> = { active: "#22c55e", completed: "#64748b", draft: "#f59e0b", scheduled: "#3b82f6" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>✉️ Email Campaigns</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Gestiona tus campañas de email marketing</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Nueva Campaña
        </button>
      </div>

      {/* Stats Overview */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {[
          { label: "Emails Enviados", value: "57.5K", icon: "📤" },
          { label: "Tasa Apertura Prom.", value: "52.3%", icon: "📬" },
          { label: "Tasa Click Prom.", value: "15.2%", icon: "🖱️" },
          { label: "Conversiones", value: "1,340", icon: "🎯" },
        ].map((stat, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{stat.label}</p>
                <p style={{ color: "#f8fafc", fontSize: 28, fontWeight: 700, margin: "8px 0 0 0" }}>{stat.value}</p>
              </div>
              <span style={{ fontSize: 32 }}>{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Campaigns Table */}
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Campaña", "Estado", "Enviados", "Abiertos", "Clicks", "Conversiones", "Open Rate", "CTR", "Acciones"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13, fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {campaigns.map(campaign => (
              <tr key={campaign.id} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                <td style={{ padding: 16 }}>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{campaign.name}</p>
                </td>
                <td style={{ padding: 16 }}>
                  <span style={{ backgroundColor: `${statusColors[campaign.status]}20`, color: statusColors[campaign.status], padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
                    {campaign.status}
                  </span>
                </td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{campaign.sent.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{campaign.opened.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{campaign.clicked.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#22c55e", fontWeight: 600 }}>{campaign.converted.toLocaleString()}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{campaign.openRate}%</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{campaign.clickRate}%</td>
                <td style={{ padding: 16 }}>
                  <button style={{ padding: "6px 12px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 6, color: "white", cursor: "pointer", marginRight: 8 }}>📊</button>
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
