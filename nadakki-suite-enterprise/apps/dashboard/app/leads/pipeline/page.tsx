"use client";
import { useState } from "react";

const stages = [
  { id: "new", name: "Nuevos", color: "#3b82f6", leads: [
    { id: 1, name: "María García", company: "TechCorp", value: 15000 },
    { id: 2, name: "Carlos López", company: "StartupXYZ", value: 8000 },
  ]},
  { id: "contacted", name: "Contactados", color: "#8b5cf6", leads: [
    { id: 3, name: "Ana Martínez", company: "BigEnterprise", value: 45000 },
  ]},
  { id: "qualified", name: "Calificados", color: "#f59e0b", leads: [
    { id: 4, name: "Pedro Sánchez", company: "MidMarket", value: 22000 },
    { id: 5, name: "Laura Torres", company: "InnovateCo", value: 18000 },
  ]},
  { id: "proposal", name: "Propuesta", color: "#ec4899", leads: [
    { id: 6, name: "Roberto Díaz", company: "GlobalTech", value: 65000 },
  ]},
  { id: "negotiation", name: "Negociación", color: "#22c55e", leads: [
    { id: 7, name: "Sandra Ruiz", company: "MegaCorp", value: 120000 },
  ]},
];

export default function LeadPipelinePage() {
  const [pipeline] = useState(stages);

  const totalValue = pipeline.reduce((acc, stage) => acc + stage.leads.reduce((a, l) => a + l.value, 0), 0);
  const totalLeads = pipeline.reduce((acc, stage) => acc + stage.leads.length, 0);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🚀 Lead Pipeline</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>{totalLeads} leads • ${totalValue.toLocaleString()} valor total</p>
        </div>
        <button style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Agregar Lead
        </button>
      </div>

      {/* Pipeline Kanban */}
      <div style={{ display: "flex", gap: 16, overflowX: "auto", paddingBottom: 20 }}>
        {pipeline.map(stage => (
          <div key={stage.id} style={{ minWidth: 280, backgroundColor: "rgba(30,41,59,0.3)", borderRadius: 16, padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: stage.color }} />
                <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, margin: 0 }}>{stage.name}</h3>
              </div>
              <span style={{ backgroundColor: "rgba(255,255,255,0.1)", color: "#94a3b8", padding: "2px 8px", borderRadius: 10, fontSize: 12 }}>
                {stage.leads.length}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {stage.leads.map(lead => (
                <div key={lead.id} style={{
                  backgroundColor: "rgba(30,41,59,0.8)", border: "1px solid rgba(51,65,85,0.5)",
                  borderRadius: 12, padding: 16, cursor: "grab"
                }}>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{lead.name}</p>
                  <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{lead.company}</p>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
                    <span style={{ color: "#22c55e", fontWeight: 700 }}>${lead.value.toLocaleString()}</span>
                    <button style={{ padding: "4px 8px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 4, color: "#94a3b8", cursor: "pointer", fontSize: 12 }}>
                      •••
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 16, padding: 12, backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 8 }}>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Valor en etapa</p>
              <p style={{ color: stage.color, fontSize: 18, fontWeight: 700, margin: "4px 0 0 0" }}>
                ${stage.leads.reduce((a, l) => a + l.value, 0).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
