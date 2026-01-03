"use client";
import MarketingNav from "@/components/marketing/MarketingNav";
import AgentExecutor from "@/components/marketing/AgentExecutor";

const AGENTS = [
  { id: "channelattributia", name: "Atribuidor de Canales", desc: "Atribuye conversiones a canales de marketing", color: "#06b6d4", input: { model: "multi_touch" } },
  { id: "attributionmodelia", name: "Modelador de Atribución", desc: "Crea modelos de atribución personalizados", color: "#0891b2", input: { window: "30d" } },
  { id: "budgetforecastia", name: "Pronosticador de Presupuesto", desc: "Predice ROI y optimiza asignación de presupuesto", color: "#0e7490", input: { period: "Q1" } },
  { id: "marketingmixmodelia", name: "Modelador de Mix Marketing", desc: "Optimiza el mix de canales para máximo ROI", color: "#155e75", input: { channels: ["paid", "organic"] } },
];

export default function AnalyticsPage() {
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📊 Analytics & Attribution</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Agentes de análisis y atribución de marketing</p>
        </div>
        <span style={{ backgroundColor: "rgba(6,182,212,0.2)", color: "#06b6d4", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
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
