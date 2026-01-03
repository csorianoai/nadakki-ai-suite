"use client";
import { useState, useEffect } from "react";

export default function MarketingPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("https://nadakki-ai-suite.onrender.com/api/catalog/marketing/agents")
      .then((res) => res.json())
      .then((data) => {
        setAgents(data.agents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <div style={{ color: "#94a3b8", fontSize: 18 }}>Cargando 35 agentes de marketing...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎯 Marketing Core</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>{agents.length} agentes disponibles</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {agents.map((agent) => (
          <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{agent.name}</h3>
            <p style={{ color: "#64748b", fontSize: 12, marginBottom: 4 }}>ID: {agent.id}</p>
            <p style={{ color: "#94a3b8", fontSize: 13 }}>{agent.category || "General"}</p>
            <button style={{ marginTop: 16, width: "100%", padding: 10, backgroundColor: "#F97316", border: "none", borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer" }}>
              Ejecutar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
