"use client";
import Link from "next/link";

export default function SettingsPage() {
  const sections = [
    { name: "Branding", href: "/settings/branding", icon: "🎨", desc: "Logo, colores, identidad visual" },
    { name: "IA", href: "/settings/ia", icon: "🤖", desc: "Tono, estilo, preferencias de IA" },
    { name: "Integraciones", href: "/settings/integrations", icon: "🔗", desc: "APIs y conexiones externas" },
    { name: "Notificaciones", href: "/settings/notifications", icon: "🔔", desc: "Alertas y preferencias" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>⚙️ Configuración</h1>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20 }}>
        {sections.map((s, i) => (
          <Link key={i} href={s.href} style={{ textDecoration: "none" }}>
            <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
              <span style={{ fontSize: 32 }}>{s.icon}</span>
              <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>{s.name}</h3>
              <p style={{ color: "#64748b", margin: 0 }}>{s.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
