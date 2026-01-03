"use client";
import MarketingNav from "@/components/marketing/MarketingNav";

export default function CommandCenterPage() {
  const kpis = [
    { label: "Revenue Generado", value: "$156,234", change: "+12.5%", color: "#22c55e" },
    { label: "Leads Totales", value: "1,247", change: "+8.3%", color: "#3b82f6" },
    { label: "Conversión", value: "3.2%", change: "+0.4%", color: "#a855f7" },
    { label: "CAC", value: "$42", change: "-15%", color: "#f59e0b" },
    { label: "LTV", value: "$890", change: "+5.2%", color: "#ec4899" },
    { label: "ROI", value: "340%", change: "+22%", color: "#22c55e" },
  ];

  const channels = [
    { name: "Email Marketing", revenue: "$45,234", leads: 423, conversion: "4.2%", color: "#f59e0b" },
    { name: "Social Media", revenue: "$32,456", leads: 312, conversion: "2.8%", color: "#3b82f6" },
    { name: "SEO/Orgánico", revenue: "$28,123", leads: 256, conversion: "3.5%", color: "#22c55e" },
    { name: "Paid Ads", revenue: "$50,421", leads: 256, conversion: "2.1%", color: "#ef4444" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎛️ Command Center</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>Vista ejecutiva de todo el sistema de marketing</p>
      </div>

      <MarketingNav />

      {/* KPIs Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 16, marginBottom: 32 }}>
        {kpis.map((kpi, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 16 }}>
            <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>{kpi.label}</p>
            <p style={{ color: "#f8fafc", fontSize: 24, fontWeight: 700, margin: "8px 0 4px 0" }}>{kpi.value}</p>
            <span style={{ backgroundColor: `${kpi.color}20`, color: kpi.color, padding: "2px 8px", borderRadius: 10, fontSize: 11 }}>
              {kpi.change}
            </span>
          </div>
        ))}
      </div>

      {/* Channels Performance */}
      <h2 style={{ color: "#f8fafc", fontSize: 20, marginBottom: 16 }}>Rendimiento por Canal</h2>
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Canal", "Revenue", "Leads", "Conversión", "Tendencia"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {channels.map((ch, i) => (
              <tr key={i} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                <td style={{ padding: 16, display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: ch.color }} />
                  <span style={{ color: "#f8fafc", fontWeight: 600 }}>{ch.name}</span>
                </td>
                <td style={{ padding: 16, color: "#22c55e", fontWeight: 600 }}>{ch.revenue}</td>
                <td style={{ padding: 16, color: "#f8fafc" }}>{ch.leads}</td>
                <td style={{ padding: 16, color: "#a855f7" }}>{ch.conversion}</td>
                <td style={{ padding: 16 }}>
                  <div style={{ width: 80, height: 24, background: `linear-gradient(90deg, ${ch.color}40, ${ch.color})`, borderRadius: 4 }} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
