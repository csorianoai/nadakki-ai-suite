"use client";
import { useState } from "react";
import Link from "next/link";

const CATEGORY_COLORS: Record<string, string> = {
  leads: "#22c55e",
  content: "#a855f7",
  social: "#3b82f6",
  analytics: "#06b6d4",
  campaigns: "#ef4444",
  segmentation: "#8b5cf6",
  retention: "#10b981",
  testing: "#f59e0b",
  competitive: "#ec4899",
  email: "#f97316",
  pricing: "#eab308",
  conversion: "#14b8a6",
  "google-ads": "#4285f4",
};

const MARKETING_AGENTS = [
  { id: "leadscoria", name: "Puntuador de Leads", cat: "leads" },
  { id: "leadscoringia", name: "Calificador de Leads", cat: "leads" },
  { id: "predictiveleadia", name: "Predictor de Leads", cat: "leads" },
  { id: "contactqualityia", name: "Evaluador de Contactos", cat: "leads" },
  { id: "abtestingia", name: "Analizador de Pruebas A/B", cat: "testing" },
  { id: "abtestingimpactia", name: "Medidor de Impacto A/B", cat: "testing" },
  { id: "campaignoptimizeria", name: "Optimizador de Campanas", cat: "campaigns" },
  { id: "marketingorchestratorea", name: "Orquestador de Marketing", cat: "campaigns" },
  { id: "contentgeneratoria", name: "Generador de Contenido", cat: "content" },
  { id: "contentperformanceia", name: "Analizador de Contenido", cat: "content" },
  { id: "socialpostgeneratoria", name: "Generador de Posts Sociales", cat: "content" },
  { id: "creativeanalyzeria", name: "Analizador de Creatividades", cat: "content" },
  { id: "sentimentanalyzeria", name: "Analizador de Sentimiento", cat: "social" },
  { id: "sociallisteningia", name: "Monitor de Redes Sociales", cat: "social" },
  { id: "influencermatcheria", name: "Buscador de Influencers", cat: "social" },
  { id: "influencermatchingia", name: "Emparejador de Influencers", cat: "social" },
  { id: "social_bridge__socialbridgeconnector", name: "Social Bridge", cat: "social" },
  { id: "competitoranalyzeria", name: "Analizador de Competencia", cat: "competitive" },
  { id: "competitorintelligenceia", name: "Inteligencia Competitiva", cat: "competitive" },
  { id: "channelattributia", name: "Atribuidor de Canales", cat: "analytics" },
  { id: "attributionmodelia", name: "Modelador de Atribucion", cat: "analytics" },
  { id: "budgetforecastia", name: "Pronosticador de Presupuesto", cat: "analytics" },
  { id: "marketingmixmodelia", name: "Modelador de Mix Marketing", cat: "analytics" },
  { id: "conversioncohortia", name: "Analizador de Cohortes", cat: "analytics" },
  { id: "audiencesegmenteria", name: "Segmentador de Audiencias", cat: "segmentation" },
  { id: "customersegmentatonia", name: "Segmentador de Clientes", cat: "segmentation" },
  { id: "geosegmentationia", name: "Segmentador Geografico", cat: "segmentation" },
  { id: "personalizationengineia", name: "Motor de Personalizacion", cat: "segmentation" },
  { id: "productaffinityia", name: "Analizador de Afinidad", cat: "segmentation" },
  { id: "retentionpredictoria", name: "Predictor de Retencion", cat: "retention" },
  { id: "retentionpredictorea", name: "Analizador de Retencion", cat: "retention" },
  { id: "journeyoptimizeria", name: "Optimizador de Journey", cat: "retention" },
  { id: "emailautomationia", name: "Automatizador de Email", cat: "email" },
  { id: "email_bridge__emailoperationalwrapper", name: "Email Bridge", cat: "email" },
  { id: "pricingoptimizeria", name: "Optimizador de Precios", cat: "pricing" },
  { id: "cashofferfilteria", name: "Filtrador de Ofertas", cat: "pricing" },
  { id: "minimalformia", name: "Optimizador de Formularios", cat: "conversion" },
  { id: "action_plan_executor__actionplanexecutor", name: "Action Plan Executor", cat: "google-ads" },
  { id: "connector__googleadsconnector", name: "Google Ads Connector", cat: "google-ads" },
  { id: "registry__operationregistry", name: "Operation Registry", cat: "google-ads" },
];

const CATEGORIES = ["all", ...Object.keys(CATEGORY_COLORS)];

export default function AgentExecutePage() {
  const [filter, setFilter] = useState("all");
  const [executing, setExecuting] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, string>>({});

  const filtered = filter === "all" ? MARKETING_AGENTS : MARKETING_AGENTS.filter(a => a.cat === filter);

  const handleExecute = async (agentId: string) => {
    setExecuting(agentId);
    setResults(prev => ({ ...prev, [agentId]: "" }));
    try {
      const res = await fetch(`https://nadakki-ai-suite.onrender.com/api/v1/agents/${agentId}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: "test execution" }),
      });
      const data = await res.json();
      setResults(prev => ({ ...prev, [agentId]: data.status || "completed" }));
    } catch {
      setResults(prev => ({ ...prev, [agentId]: "error" }));
    } finally {
      setExecuting(null);
    }
  };

  const stats = {
    total: MARKETING_AGENTS.length,
    categories: Object.keys(CATEGORY_COLORS).length,
    googleAds: MARKETING_AGENTS.filter(a => a.cat === "google-ads").length,
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>Agent Execute Console</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>
            Los {stats.total} agentes de IA de marketing &middot;{" "}
            <Link href="/marketing/agents" style={{ color: "#8b5cf6", textDecoration: "none" }}>
              Marketing Agents Hub
            </Link>
          </p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <span style={{ backgroundColor: "rgba(66,133,244,0.2)", color: "#4285f4", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
            {stats.googleAds} Google Ads
          </span>
          <span style={{ backgroundColor: "rgba(236,72,153,0.2)", color: "#ec4899", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
            {filtered.length} / {stats.total} agentes
          </span>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#f8fafc" }}>{stats.total}</div>
          <div style={{ color: "#94a3b8", fontSize: 12 }}>Total Agentes</div>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#22c55e" }}>{stats.total}</div>
          <div style={{ color: "#94a3b8", fontSize: 12 }}>Activos</div>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#8b5cf6" }}>{stats.categories}</div>
          <div style={{ color: "#94a3b8", fontSize: 12 }}>Categorias</div>
        </div>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16, textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#4285f4" }}>{stats.googleAds}</div>
          <div style={{ color: "#94a3b8", fontSize: 12 }}>Google Ads</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 24 }}>
        {CATEGORIES.map(cat => (
          <button key={cat} onClick={() => setFilter(cat)} style={{
            padding: "6px 14px", backgroundColor: filter === cat ? (CATEGORY_COLORS[cat] || "#8b5cf6") : "rgba(30,41,59,0.5)",
            border: "1px solid rgba(51,65,85,0.5)", borderRadius: 20,
            color: filter === cat ? "white" : "#94a3b8", cursor: "pointer", fontSize: 12, fontWeight: 600, textTransform: "capitalize",
          }}>{cat}</button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 16 }}>
        {filtered.map((agent) => {
          const color = CATEGORY_COLORS[agent.cat] || "#94a3b8";
          return (
            <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div>
                  <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, margin: 0 }}>{agent.name}</h3>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                    <code style={{ color: "#64748b", fontSize: 10 }}>{agent.id}</code>
                    <span style={{ backgroundColor: `${color}20`, color, padding: "2px 8px", borderRadius: 10, fontSize: 10 }}>{agent.cat}</span>
                  </div>
                </div>
                <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#22c55e" }} />
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <button
                  onClick={() => handleExecute(agent.id)}
                  disabled={executing === agent.id}
                  style={{
                    padding: "6px 16px", backgroundColor: executing === agent.id ? "rgba(100,116,139,0.3)" : `${color}20`,
                    border: `1px solid ${color}40`, borderRadius: 8, color, cursor: executing === agent.id ? "wait" : "pointer",
                    fontSize: 12, fontWeight: 600,
                  }}
                >
                  {executing === agent.id ? "Ejecutando..." : "Ejecutar"}
                </button>
                {results[agent.id] && (
                  <span style={{ fontSize: 11, color: results[agent.id] === "error" ? "#ef4444" : "#22c55e" }}>
                    {results[agent.id] === "error" ? "Error" : results[agent.id]}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
