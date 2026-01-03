"use client";
import Link from "next/link";

export default function AudiencesPage() {
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>👥 Audiencias</h1>
      <Link href="/audiences/manager" style={{ textDecoration: "none" }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24, maxWidth: 400, cursor: "pointer" }}>
          <span style={{ fontSize: 40 }}>🎯</span>
          <h3 style={{ color: "#f8fafc", margin: "12px 0 8px 0" }}>Audience Manager</h3>
          <p style={{ color: "#64748b", margin: 0 }}>Segmentación inteligente</p>
        </div>
      </Link>
    </div>
  );
}
