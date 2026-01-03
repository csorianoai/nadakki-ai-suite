"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const NAV_ITEMS = [
  { name: "Hub", href: "/marketing", icon: "🚀", color: "#8b5cf6" },
  { name: "Leads", href: "/marketing/leads", icon: "🎯", color: "#22c55e" },
  { name: "Content", href: "/marketing/content", icon: "✍️", color: "#a855f7" },
  { name: "Social", href: "/marketing/social", icon: "📱", color: "#3b82f6" },
  { name: "Analytics", href: "/marketing/analytics", icon: "📊", color: "#06b6d4" },
  { name: "Campaigns", href: "/marketing/campaigns", icon: "📢", color: "#f59e0b" },
  { name: "Agentes", href: "/marketing/agents", icon: "🤖", color: "#ec4899" },
];

export default function MarketingNav() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={() => router.back()} style={{
          display: "flex", alignItems: "center", gap: 6, padding: "8px 16px",
          backgroundColor: "rgba(100,116,139,0.2)", border: "1px solid rgba(100,116,139,0.3)",
          borderRadius: 8, color: "#94a3b8", cursor: "pointer", fontSize: 14, fontWeight: 500,
        }}>
          <span style={{ fontSize: 16 }}>←</span> Atrás
        </button>
        <button onClick={() => router.forward()} style={{
          display: "flex", alignItems: "center", gap: 6, padding: "8px 16px",
          backgroundColor: "rgba(100,116,139,0.2)", border: "1px solid rgba(100,116,139,0.3)",
          borderRadius: 8, color: "#94a3b8", cursor: "pointer", fontSize: 14, fontWeight: 500,
        }}>
          Adelante <span style={{ fontSize: 16 }}>→</span>
        </button>
        <div style={{ marginLeft: "auto" }}>
          <Link href="/" style={{ textDecoration: "none" }}>
            <button style={{
              padding: "8px 16px", backgroundColor: "rgba(59,130,246,0.1)",
              border: "1px solid rgba(59,130,246,0.3)", borderRadius: 8,
              color: "#3b82f6", cursor: "pointer", fontSize: 14, fontWeight: 500,
            }}>🏠 Dashboard</button>
          </Link>
        </div>
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} style={{ textDecoration: "none" }}>
              <button style={{
                display: "flex", alignItems: "center", gap: 8, padding: "10px 18px",
                backgroundColor: isActive ? item.color : `${item.color}15`,
                border: `2px solid ${isActive ? item.color : item.color + "40"}`,
                borderRadius: 12, color: isActive ? "white" : item.color,
                cursor: "pointer", fontSize: 14, fontWeight: 600,
              }}>
                <span>{item.icon}</span> <span>{item.name}</span>
              </button>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
