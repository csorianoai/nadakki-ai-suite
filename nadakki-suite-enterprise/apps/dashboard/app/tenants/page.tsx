"use client";
import { useState } from "react";

export default function TenantsPage() {
  const [tenants] = useState([
    { id: "credicefi", name: "CrediCeFi", industry: "Fintech", agents: 35, campaigns: 12, status: "active" },
    { id: "bancomex", name: "BancoMex", industry: "Banking", agents: 28, campaigns: 8, status: "active" },
    { id: "segurosplus", name: "SegurosPlus", industry: "Insurance", agents: 22, campaigns: 5, status: "pending" },
  ]);

  const [selected, setSelected] = useState("credicefi");

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🏢 Multi-Tenant</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Gestiona múltiples organizaciones</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Nuevo Tenant
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {tenants.map(t => (
          <div key={t.id} onClick={() => setSelected(t.id)}
            style={{ backgroundColor: "rgba(30,41,59,0.5)", border: selected === t.id ? "2px solid #8b5cf6" : "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24, cursor: "pointer" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <h3 style={{ color: "#f8fafc", margin: "0 0 4px 0" }}>{t.name}</h3>
                <span style={{ color: "#8b5cf6", fontSize: 12 }}>{t.industry}</span>
              </div>
              <span style={{ backgroundColor: t.status === "active" ? "rgba(34,197,94,0.1)" : "rgba(245,158,11,0.1)",
                color: t.status === "active" ? "#22c55e" : "#f59e0b", padding: "4px 10px", borderRadius: 20, fontSize: 11 }}>
                {t.status}
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Agentes</p>
                <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{t.agents}</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Campañas</p>
                <p style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: "4px 0 0 0" }}>{t.campaigns}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
