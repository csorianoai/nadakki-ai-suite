"use client";
import Link from "next/link";
import MarketingNav from "@/components/marketing/MarketingNav";

const MODULES = [
  { name: "Lead Management", href: "/marketing/leads", icon: "🎯", count: 3, color: "#22c55e", desc: "Scoring y predicción de leads" },
  { name: "Content Generation", href: "/marketing/content", icon: "✍️", count: 4, color: "#a855f7", desc: "Generación de contenido con IA" },
  { name: "Social Media", href: "/marketing/social", icon: "📱", count: 4, color: "#3b82f6", desc: "Monitoreo y análisis social" },
  { name: "Analytics", href: "/marketing/analytics", icon: "📊", count: 4, color: "#06b6d4", desc: "Attribution y forecasting" },
  { name: "Campaigns", href: "/marketing/campaigns", icon: "📢", count: 4, color: "#f59e0b", desc: "Optimización de campañas" },
  { name: "Segmentation", href: "/marketing/segmentation", icon: "👥", count: 4, color: "#8b5cf6", desc: "Segmentación avanzada" },
  { name: "Retention", href: "/marketing/retention", icon: "💚", count: 4, color: "#10b981", desc: "Retención y journey" },
  { name: "Ver 35 Agentes", href: "/marketing/agents", icon: "🤖", count: 35, color: "#ec4899", desc: "Catálogo completo" },
];

export default function MarketingPage() {
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 36, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🚀 Marketing Automation Hub</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>35 agentes de IA para automatización de marketing</p>
      </div>

      <MarketingNav />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {[
          { label: "Agentes Activos", value: "35", color: "#22c55e" },
          { label: "Leads Procesados", value: "1,247", color: "#3b82f6" },
          { label: "Contenido Generado", value: "456", color: "#a855f7" },
          { label: "ROI Promedio", value: "340%", color: "#f59e0b" },
        ].map((stat, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{stat.label}</p>
            <p style={{ color: stat.color, fontSize: 32, fontWeight: 700, margin: "8px 0 0 0" }}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {MODULES.map((mod, i) => (
          <Link key={i} href={mod.href} style={{ textDecoration: "none" }}>
            <div style={{
              backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)",
              borderRadius: 16, padding: 20, cursor: "pointer", transition: "all 0.2s",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <span style={{ fontSize: 36 }}>{mod.icon}</span>
                <span style={{ backgroundColor: `${mod.color}20`, color: mod.color, padding: "4px 12px", borderRadius: 20, fontSize: 13, fontWeight: 700 }}>
                  {mod.count}
                </span>
              </div>
              <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "12px 0 4px 0" }}>{mod.name}</h3>
              <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{mod.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
