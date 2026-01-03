"use client";
import { useState } from "react";

const mockCampaigns = [
  { id: 1, name: "Black Friday 2026", status: "active", platforms: ["meta", "tiktok"], budget: 5000, spent: 2340, leads: 156, impressions: 45000 },
  { id: 2, name: "Lanzamiento Producto X", status: "active", platforms: ["linkedin", "x"], budget: 3000, spent: 1200, leads: 89, impressions: 23000 },
  { id: 3, name: "Brand Awareness Q1", status: "scheduled", platforms: ["youtube", "meta"], budget: 8000, spent: 0, leads: 0, impressions: 0 },
  { id: 4, name: "Retargeting Clientes", status: "paused", platforms: ["meta"], budget: 2000, spent: 890, leads: 34, impressions: 12000 },
];

export default function ActiveCampaignsPage() {
  const [campaigns] = useState(mockCampaigns);
  const [filter, setFilter] = useState("all");

  const filtered = filter === "all" ? campaigns : campaigns.filter(c => c.status === filter);

  const platformIcons: Record<string, string> = {
    meta: "📘", x: "🐦", tiktok: "🎵", linkedin: "💼", youtube: "▶️", pinterest: "📌"
  };

  const statusColors: Record<string, string> = {
    active: "#22c55e", scheduled: "#3b82f6", paused: "#f59e0b", completed: "#64748b"
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📢 Campañas Activas</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>{campaigns.filter(c => c.status === "active").length} campañas en ejecución</p>
        </div>
        <button style={{
          padding: "12px 24px", backgroundColor: "#8B5CF6", border: "none",
          borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer"
        }}>
          + Nueva Campaña
        </button>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
        {["all", "active", "scheduled", "paused"].map(status => (
          <button key={status} onClick={() => setFilter(status)} style={{
            padding: "8px 16px",
            backgroundColor: filter === status ? "#8B5CF6" : "rgba(30,41,59,0.5)",
            border: "none", borderRadius: 8, color: "white", cursor: "pointer"
          }}>
            {status === "all" ? "Todas" : status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {filtered.map((campaign) => (
          <div key={campaign.id} style={{
            backgroundColor: "rgba(30,41,59,0.5)",
            border: "1px solid rgba(51,65,85,0.5)",
            borderRadius: 16,
            padding: 24
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <h3 style={{ color: "#f8fafc", fontSize: 20, fontWeight: 600, margin: 0 }}>{campaign.name}</h3>
                  <span style={{
                    backgroundColor: `${statusColors[campaign.status]}20`,
                    color: statusColors[campaign.status],
                    padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600
                  }}>
                    {campaign.status.toUpperCase()}
                  </span>
                </div>
                <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                  {campaign.platforms.map(p => (
                    <span key={p} style={{ fontSize: 20 }}>{platformIcons[p]}</span>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <p style={{ color: "#94a3b8", fontSize: 12, margin: 0 }}>Presupuesto</p>
                <p style={{ color: "#f8fafc", fontSize: 24, fontWeight: 700, margin: 0 }}>${campaign.budget.toLocaleString()}</p>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Gastado</p>
                <p style={{ color: "#f8fafc", fontSize: 20, fontWeight: 600, margin: "4px 0 0 0" }}>${campaign.spent.toLocaleString()}</p>
                <p style={{ color: "#94a3b8", fontSize: 11, margin: "2px 0 0 0" }}>{((campaign.spent/campaign.budget)*100).toFixed(0)}% del presupuesto</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Leads</p>
                <p style={{ color: "#22c55e", fontSize: 20, fontWeight: 600, margin: "4px 0 0 0" }}>{campaign.leads}</p>
                <p style={{ color: "#94a3b8", fontSize: 11, margin: "2px 0 0 0" }}>${campaign.spent > 0 ? (campaign.spent/campaign.leads).toFixed(2) : 0}/lead</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Impresiones</p>
                <p style={{ color: "#3b82f6", fontSize: 20, fontWeight: 600, margin: "4px 0 0 0" }}>{(campaign.impressions/1000).toFixed(1)}K</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>CTR</p>
                <p style={{ color: "#f59e0b", fontSize: 20, fontWeight: 600, margin: "4px 0 0 0" }}>{campaign.impressions > 0 ? ((campaign.leads/campaign.impressions)*100).toFixed(2) : 0}%</p>
              </div>
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
              <button style={{ padding: "10px 20px", backgroundColor: "#3b82f6", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>📊 Ver Analytics</button>
              <button style={{ padding: "10px 20px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>✏️ Editar</button>
              <button style={{ padding: "10px 20px", backgroundColor: "rgba(239,68,68,0.1)", border: "none", borderRadius: 8, color: "#ef4444", cursor: "pointer" }}>⏸️ Pausar</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
