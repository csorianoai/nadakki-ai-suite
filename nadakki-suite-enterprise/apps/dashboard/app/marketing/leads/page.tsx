"use client";
import MarketingNav from "@/components/marketing/MarketingNav";
import AgentExecutor from "@/components/marketing/AgentExecutor";

const AGENTS = [
  { id: "leadscoria", name: "Puntuador de Leads", desc: "Califica leads con ML para priorizar seguimiento", color: "#22c55e", input: { lead_id: "lead-001" } },
  { id: "leadscoringia", name: "Calificador de Leads", desc: "Sistema avanzado de scoring basado en comportamiento", color: "#10b981", input: { segment: "warm" } },
  { id: "predictiveleadia", name: "Predictor de Leads", desc: "Predice probabilidad de conversión con IA", color: "#059669", input: { model: "conversion" } },
];

export default function LeadsPage() {
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎯 Lead Management</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Agentes de scoring y predicción de leads</p>
        </div>
        <span style={{ backgroundColor: "rgba(34,197,94,0.2)", color: "#22c55e", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
          {AGENTS.length} agentes
        </span>
      </div>
      <MarketingNav />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 20 }}>
        {AGENTS.map((agent) => (
          <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: 0 }}>{agent.name}</h3>
                <code style={{ color: "#64748b", fontSize: 11 }}>{agent.id}</code>
              </div>
              <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#22c55e" }} />
            </div>
            <p style={{ color: "#94a3b8", fontSize: 14, margin: "0 0 16px 0" }}>{agent.desc}</p>
            <AgentExecutor agentId={agent.id} agentName={agent.name} color={agent.color} defaultInput={agent.input} />
          </div>
        ))}
      </div>
    </div>
  );
}
