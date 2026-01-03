"use client";
import { useState } from "react";

export default function WorkflowcampaignoptimizationPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const executeWorkflow = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("https://nadakki-ai-suite.onrender.com/workflows/campaign-optimization", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_brief: { name: "Test Campaign", objective: "lead_generation", channel: "email" },
          budget: 10000,
          tenant_id: "credicefi"
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📢 Campaign Optimization</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>5 pasos en este workflow</p>
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24, marginBottom: 24 }}>
        <button onClick={executeWorkflow} disabled={loading} style={{
          padding: "14px 28px",
          backgroundColor: loading ? "#475569" : "#8B5CF6",
          border: "none",
          borderRadius: 10,
          color: "white",
          fontWeight: 700,
          fontSize: 16,
          cursor: loading ? "not-allowed" : "pointer"
        }}>
          {loading ? "⏳ Ejecutando..." : "🚀 Ejecutar Workflow"}
        </button>
      </div>

      {result && (
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: result.error ? "1px solid rgba(239,68,68,0.3)" : "1px solid rgba(34,197,94,0.3)", borderRadius: 16, padding: 24 }}>
          <h2 style={{ color: result.error ? "#ef4444" : "#22c55e", fontSize: 18, marginBottom: 16 }}>
            {result.error ? "❌ Error" : "✅ Resultado"}
          </h2>
          {result.steps && (
            <div style={{ marginBottom: 16 }}>
              {result.steps.map((step: any, i: number) => (
                <div key={i} style={{ padding: 12, backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 8, marginBottom: 8, display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ color: step.status === "success" ? "#22c55e" : "#ef4444" }}>{step.status === "success" ? "✓" : "✗"}</span>
                  <span style={{ color: "#f8fafc" }}>Step {i+1}: {step.agent_id || "Processing"}</span>
                  <span style={{ color: "#64748b", marginLeft: "auto" }}>{step.duration_ms}ms</span>
                </div>
              ))}
            </div>
          )}
          <div style={{ backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 8, padding: 16, overflow: "auto" }}>
            <pre style={{ color: "#94a3b8", fontSize: 12, margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
