"use client";
import { useState, useEffect } from "react";
export default function LegalPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("https://nadakki-ai-suite.onrender.com/api/catalog/legal/agents")
      .then((res) => res.json())
      .then((data) => { setAgents(data.agents || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);
  if (loading) return <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}><div style={{ color: "#94a3b8" }}>Cargando...</div></div>;
  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc" }}>⚖️ Legal Core</h1>
      <p style={{ color: "#94a3b8", marginBottom: 32 }}>{agents.length} agentes</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {agents.map((a) => (<div key={a.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 12, padding: 20 }}><h3 style={{ color: "#f8fafc", fontSize: 16 }}>{a.name}</h3><p style={{ color: "#64748b", fontSize: 12 }}>{a.id}</p></div>))}
      </div>
    </div>
  );
}
