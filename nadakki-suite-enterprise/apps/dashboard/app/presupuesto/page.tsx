"use client";
import { useState, useEffect } from "react";

interface Agent { id: string; name: string; category: string; }

export default function presupuestoPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetch("https://nadakki-ai-suite.onrender.com/api/catalog/presupuesto/agents")
      .then((res) => res.json())
      .then((data) => { setAgents(data.agents || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const executeAgent = async (agentId: string) => {
    setExecuting(agentId);
    setResult(null);
    setShowModal(true);
    try {
      const response = await fetch(+""+https://nadakki-ai-suite.onrender.com/agents/presupuesto/+""+{agentId}/execute, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_data: { test: true }, tenant_id: "credicefi" })
      });
      const data = await response.json();
      setResult({ status: "success", data });
    } catch (err: any) {
      setResult({ status: "error", error: err.message });
    } finally {
      setExecuting(null);
    }
  };

  if (loading) return <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}><div style={{ color: "#94a3b8" }}>Cargando agentes...</div></div>;

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 8 }}>💰 Presupuesto Core</h1>
      <p style={{ color: "#94a3b8", marginBottom: 32 }}>{agents.length} agentes disponibles</p>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {agents.map((agent) => (
          <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{agent.name}</h3>
            <p style={{ color: "#64748b", fontSize: 12, marginBottom: 4 }}>ID: {agent.id}</p>
            <p style={{ color: "#94a3b8", fontSize: 13 }}>{agent.category}</p>
            <button onClick={() => executeAgent(agent.id)} disabled={executing === agent.id} style={{
              marginTop: 16, width: "100%", padding: 10,
              backgroundColor: executing === agent.id ? "#6b7280" : "#EAB308",
              border: "none", borderRadius: 8, color: "white", fontWeight: 600,
              cursor: executing === agent.id ? "not-allowed" : "pointer"
            }}>
              {executing === agent.id ? "⏳ Ejecutando..." : "🚀 Ejecutar"}
            </button>
          </div>
        ))}
      </div>

      {showModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.8)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000 }} onClick={() => setShowModal(false)}>
          <div style={{ backgroundColor: "#1e293b", borderRadius: 16, padding: 32, maxWidth: 600, width: "90%", maxHeight: "80vh", overflow: "auto" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 24 }}>
              <h2 style={{ color: "#f8fafc", fontSize: 20, margin: 0 }}>{executing ? "⏳ Ejecutando..." : result?.status === "error" ? "❌ Error" : "✅ Resultado"}</h2>
              <button onClick={() => setShowModal(false)} style={{ background: "none", border: "none", color: "#94a3b8", fontSize: 24, cursor: "pointer" }}>×</button>
            </div>
            {executing && <div style={{ textAlign: "center", padding: 40 }}><div style={{ fontSize: 48 }}>🔄</div><p style={{ color: "#94a3b8" }}>Procesando...</p></div>}
            {result && !executing && (
              <div style={{ backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 8, padding: 16 }}>
                <pre style={{ color: "#94a3b8", fontSize: 12, margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
