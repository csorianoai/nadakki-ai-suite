"use client";
import { useState, useEffect } from "react";

const MOCK_AGENTS = [
  { id: "leadscoringia", name: "LeadScoringIA", category: "Marketing", status: "active" },
  { id: "contentgeneratoria", name: "ContentGeneratorIA", category: "Marketing", status: "active" },
  { id: "compliancecheckingia", name: "ComplianceCheckingIA", category: "Compliance", status: "active" },
  { id: "legalreviewia", name: "LegalReviewIA", category: "Legal", status: "active" },
  { id: "frauddetectoria", name: "FraudDetectorIA", category: "Finanzas", status: "active" },
];

export default function AdminAgentsPage() {
  const [agents, setAgents] = useState(MOCK_AGENTS);
  const [apiStatus, setApiStatus] = useState<"mock" | "live">("mock");

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    fetch("https://nadakki-ai-suite.onrender.com/api/catalog/marketing/agents", { signal: controller.signal })
      .then(r => r.json())
      .then(data => {
        clearTimeout(timeoutId);
        if (data.agents && data.agents.length > 0) {
          setAgents(data.agents.slice(0, 20));
          setApiStatus("live");
        }
      })
      .catch(() => clearTimeout(timeoutId));

    return () => clearTimeout(timeoutId);
  }, []);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🤖 Admin: Agentes IA</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>{agents.length} agentes registrados</p>
        </div>
        <span style={{ backgroundColor: apiStatus === "live" ? "rgba(34,197,94,0.2)" : "rgba(245,158,11,0.2)", color: apiStatus === "live" ? "#22c55e" : "#f59e0b", padding: "6px 14px", borderRadius: 20, fontSize: 12, height: "fit-content" }}>
          {apiStatus === "live" ? "🟢 API Live" : "🟡 Demo Mode"}
        </span>
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Estado", "Nombre", "ID", "Categoría", "Acciones"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {agents.map((a, i) => (
              <tr key={i} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                <td style={{ padding: 16 }}><div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#22c55e" }} /></td>
                <td style={{ padding: 16, color: "#f8fafc", fontWeight: 600 }}>{a.name}</td>
                <td style={{ padding: 16, color: "#64748b", fontSize: 12 }}>{a.id}</td>
                <td style={{ padding: 16, color: "#94a3b8" }}>{a.category || "Marketing"}</td>
                <td style={{ padding: 16 }}>
                  <button style={{ padding: "4px 10px", backgroundColor: "rgba(239,68,68,0.1)", border: "none", borderRadius: 4, color: "#ef4444", cursor: "pointer", fontSize: 12 }}>Desactivar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
