"use client";
import Link from "next/link";

export default function AnalyticsPage() {
  const kpis = [
    { label: "Revenue Total", value: "$156K", change: "+23%", color: "#22c55e" },
    { label: "Leads Generados", value: "1,247", change: "+15%", color: "#3b82f6" },
    { label: "Conversión", value: "3.2%", change: "+0.4%", color: "#8b5cf6" },
    { label: "CAC", value: "$42", change: "-12%", color: "#22c55e" },
  ];

  const modules = [
    { name: "Por Campaña", href: "/analytics/campaigns", icon: "📢" },
    { name: "Por Canal Social", href: "/social/analytics", icon: "📱" },
    { name: "Conversiones", href: "/analytics/conversions", icon: "🎯" },
    { name: "Por Agente IA", href: "/analytics/agents", icon: "🤖" },
    { name: "ROI Calculator", href: "/analytics/roi", icon: "📊" },
    { name: "Reportes", href: "/analytics/reports", icon: "📑" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📊 Analytics Hub</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {kpis.map((k, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 20 }}>
            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{k.label}</p>
            <p style={{ color: "#f8fafc", fontSize: 32, fontWeight: 700, margin: "8px 0 0 0" }}>{k.value}</p>
            <p style={{ color: k.color, fontSize: 13, margin: "8px 0 0 0" }}>{k.change} vs mes anterior</p>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {modules.map((m, i) => (
          <Link key={i} href={m.href} style={{ textDecoration: "none" }}>
            <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
              <span style={{ fontSize: 32 }}>{m.icon}</span>
              <h3 style={{ color: "#f8fafc", margin: "12px 0 0 0" }}>{m.name}</h3>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
