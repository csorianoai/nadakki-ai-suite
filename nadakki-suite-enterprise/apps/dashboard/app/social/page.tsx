"use client";
import Link from "next/link";

export default function SocialPage() {
  const modules = [
    { name: "Conexiones", href: "/social/connections", icon: "🔗", desc: "Conectar redes sociales" },
    { name: "Programador", href: "/social/scheduler", icon: "📅", desc: "Programar publicaciones" },
    { name: "Monitoreo", href: "/social/monitoring", icon: "📡", desc: "Engagement en tiempo real" },
    { name: "Analytics", href: "/social/analytics", icon: "📊", desc: "Métricas por plataforma" },
    { name: "Inbox", href: "/social/inbox", icon: "📬", desc: "Bandeja unificada" },
    { name: "Editor", href: "/social/editor", icon: "🎨", desc: "Editor multiplataforma" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📱 Social Media Hub</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {modules.map((m, i) => (
          <Link key={i} href={m.href} style={{ textDecoration: "none" }}>
            <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
              <span style={{ fontSize: 40 }}>{m.icon}</span>
              <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>{m.name}</h3>
              <p style={{ color: "#64748b", fontSize: 14, margin: 0 }}>{m.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
