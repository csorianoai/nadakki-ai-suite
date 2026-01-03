"use client";
import { useState } from "react";
import MarketingNav from "@/components/marketing/MarketingNav";
import AgentExecutor from "@/components/marketing/AgentExecutor";

const ALL_AGENTS = [
  { id: "leadscoria", name: "Puntuador de Leads", cat: "leads", color: "#22c55e" },
  { id: "leadscoringia", name: "Calificador de Leads", cat: "leads", color: "#22c55e" },
  { id: "predictiveleadia", name: "Predictor de Leads", cat: "leads", color: "#22c55e" },
  { id: "abtestingia", name: "Analizador de Pruebas A/B", cat: "testing", color: "#f59e0b" },
  { id: "abtestingimpactia", name: "Medidor de Impacto A/B", cat: "testing", color: "#f59e0b" },
  { id: "campaignoptimizeria", name: "Optimizador de Campañas", cat: "campaigns", color: "#ef4444" },
  { id: "contentgeneratoria", name: "Generador de Contenido", cat: "content", color: "#a855f7" },
  { id: "contentperformanceia", name: "Analizador de Contenido", cat: "content", color: "#a855f7" },
  { id: "socialpostgeneratoria", name: "Generador de Posts Sociales", cat: "content", color: "#a855f7" },
  { id: "sentimentanalyzeria", name: "Analizador de Sentimiento", cat: "social", color: "#3b82f6" },
  { id: "sociallisteningia", name: "Monitor de Redes Sociales", cat: "social", color: "#3b82f6" },
  { id: "competitoranalyzeria", name: "Analizador de Competencia", cat: "competitive", color: "#ec4899" },
  { id: "competitorintelligenceia", name: "Inteligencia Competitiva", cat: "competitive", color: "#ec4899" },
  { id: "channelattributia", name: "Atribuidor de Canales", cat: "analytics", color: "#06b6d4" },
  { id: "attributionmodelia", name: "Modelador de Atribución", cat: "analytics", color: "#06b6d4" },
  { id: "budgetforecastia", name: "Pronosticador de Presupuesto", cat: "analytics", color: "#06b6d4" },
  { id: "marketingmixmodelia", name: "Modelador de Mix Marketing", cat: "analytics", color: "#06b6d4" },
  { id: "audiencesegmenteria", name: "Segmentador de Audiencias", cat: "segmentation", color: "#8b5cf6" },
  { id: "customersegmentatonia", name: "Segmentador de Clientes", cat: "segmentation", color: "#8b5cf6" },
  { id: "geosegmentationia", name: "Segmentador Geográfico", cat: "segmentation", color: "#8b5cf6" },
  { id: "personalizationengineia", name: "Motor de Personalización", cat: "segmentation", color: "#8b5cf6" },
  { id: "retentionpredictoria", name: "Predictor de Retención", cat: "retention", color: "#10b981" },
  { id: "retentionpredictorea", name: "Analizador de Retención", cat: "retention", color: "#10b981" },
  { id: "emailautomationia", name: "Automatizador de Email", cat: "email", color: "#f97316" },
  { id: "journeyoptimizeria", name: "Optimizador de Journey", cat: "retention", color: "#10b981" },
  { id: "pricingoptimizeria", name: "Optimizador de Precios", cat: "pricing", color: "#eab308" },
  { id: "influencermatcheria", name: "Buscador de Influencers", cat: "social", color: "#3b82f6" },
  { id: "influencermatchingia", name: "Emparejador de Influencers", cat: "social", color: "#3b82f6" },
  { id: "creativeanalyzeria", name: "Analizador de Creatividades", cat: "content", color: "#a855f7" },
  { id: "contactqualityia", name: "Evaluador de Contactos", cat: "leads", color: "#22c55e" },
  { id: "minimalformia", name: "Optimizador de Formularios", cat: "conversion", color: "#14b8a6" },
  { id: "conversioncohortia", name: "Analizador de Cohortes", cat: "analytics", color: "#06b6d4" },
  { id: "productaffinityia", name: "Analizador de Afinidad", cat: "segmentation", color: "#8b5cf6" },
  { id: "cashofferfilteria", name: "Filtrador de Ofertas", cat: "pricing", color: "#eab308" },
  { id: "marketingorchestratorea", name: "Orquestador de Marketing", cat: "campaigns", color: "#ef4444" },
];

const CATEGORIES = ["all", "leads", "content", "social", "analytics", "campaigns", "segmentation", "retention", "testing", "competitive", "email", "pricing", "conversion"];

export default function AllAgentsPage() {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? ALL_AGENTS : ALL_AGENTS.filter(a => a.cat === filter);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🤖 Marketing Agents Hub</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Los 35 agentes de IA de marketing</p>
        </div>
        <span style={{ backgroundColor: "rgba(236,72,153,0.2)", color: "#ec4899", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
          {filtered.length} / {ALL_AGENTS.length} agentes
        </span>
      </div>
      <MarketingNav />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 24 }}>
        {CATEGORIES.map(cat => (
          <button key={cat} onClick={() => setFilter(cat)} style={{
            padding: "6px 14px", backgroundColor: filter === cat ? "#8b5cf6" : "rgba(30,41,59,0.5)",
            border: "1px solid rgba(51,65,85,0.5)", borderRadius: 20,
            color: filter === cat ? "white" : "#94a3b8", cursor: "pointer", fontSize: 12, fontWeight: 600, textTransform: "capitalize"
          }}>{cat}</button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 16 }}>
        {filtered.map((agent) => (
          <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, margin: 0 }}>{agent.name}</h3>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                  <code style={{ color: "#64748b", fontSize: 10 }}>{agent.id}</code>
                  <span style={{ backgroundColor: `${agent.color}20`, color: agent.color, padding: "2px 8px", borderRadius: 10, fontSize: 10 }}>{agent.cat}</span>
                </div>
              </div>
              <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#22c55e" }} />
            </div>
            <AgentExecutor agentId={agent.id} agentName={agent.name} color={agent.color} />
          </div>
        ))}
      </div>
    </div>
  );
}
