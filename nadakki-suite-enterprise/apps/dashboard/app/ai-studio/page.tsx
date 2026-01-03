"use client";
import Link from "next/link";

export default function AIStudioPage() {
  const modules = [
    { name: "Generador de Contenido", href: "/ai-studio/generate", icon: "✨", desc: "Crea posts, emails y ads con IA" },
    { name: "Plantillas IA", href: "/ai-studio/templates", icon: "📋", desc: "Plantillas optimizadas" },
    { name: "Historial", href: "/ai-studio/history", icon: "📜", desc: "Todo el contenido generado" },
    { name: "Agentes IA", href: "/ai-studio/agents", icon: "🤖", desc: "Control de agentes" },
    { name: "Configuración", href: "/ai-studio/settings", icon: "⚙️", desc: "Tono y preferencias" },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎨 AI Studio</h1>
      <p style={{ color: "#94a3b8", marginTop: 8, marginBottom: 32 }}>Centro de creación con Inteligencia Artificial</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {modules.map((m, i) => (
          <Link key={i} href={m.href} style={{ textDecoration: "none" }}>
            <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
              <span style={{ fontSize: 40 }}>{m.icon}</span>
              <h3 style={{ color: "#f8fafc", fontSize: 18, margin: "16px 0 8px 0" }}>{m.name}</h3>
              <p style={{ color: "#64748b", fontSize: 14, margin: 0 }}>{m.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
