"use client";
import { useState } from "react";

interface AgentExecutorProps {
  agentId: string;
  agentName: string;
  color: string;
  defaultInput?: Record<string, any>;
}

const API_BASE = "https://nadakki-ai-suite.onrender.com";

export default function AgentExecutor({ agentId, agentName, color, defaultInput = {} }: AgentExecutorProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const executeAgent = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // RUTA CORRECTA CONFIRMADA: /agents/marketing/{agent_id}/execute
      const response = await fetch(`${API_BASE}/agents/marketing/${agentId}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_data: { ...defaultInput, tenant_id: "credicefi", timestamp: new Date().toISOString() }
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Error ${response.status}`);
      setResult(data);
    } catch (err: any) {
      if (err.message?.includes("Failed to fetch")) {
        setError("Backend dormido. Haz clic en ⚡ para despertar y espera 30 seg.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      setShowModal(true);
    }
  };

  const wakeBackend = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/health`);
      setResult({ message: "✅ Backend despertado. Ahora ejecuta el agente." });
    } catch {
      setError("Iniciando backend... espera 30 segundos.");
    } finally {
      setLoading(false);
      setShowModal(true);
    }
  };

  return (
    <>
      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={executeAgent} disabled={loading} style={{
          flex: 1, padding: 12, backgroundColor: loading ? "#64748b" : color,
          border: "none", borderRadius: 8, color: "white", fontWeight: 600,
          cursor: loading ? "wait" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
        }}>
          {loading ? "⏳ Ejecutando..." : "🚀 Ejecutar"}
        </button>
        <button onClick={wakeBackend} disabled={loading} title="Despertar backend" style={{
          padding: "12px 14px", backgroundColor: "rgba(245,158,11,0.2)", border: "1px solid rgba(245,158,11,0.3)",
          borderRadius: 8, color: "#f59e0b", cursor: "pointer", fontSize: 16,
        }}>⚡</button>
      </div>

      {showModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.8)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000
        }} onClick={() => setShowModal(false)}>
          <div style={{
            backgroundColor: "#1e293b", borderRadius: 16, padding: 24,
            maxWidth: 700, width: "90%", maxHeight: "80vh", overflow: "auto"
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
              <h3 style={{ color: "#f8fafc", margin: 0 }}>
                {error ? "❌ Error" : "✅ Resultado"} - {agentName}
              </h3>
              <button onClick={() => setShowModal(false)} style={{
                backgroundColor: "transparent", border: "none", color: "#94a3b8", fontSize: 24, cursor: "pointer"
              }}>×</button>
            </div>
            
            {error ? (
              <div style={{ backgroundColor: "rgba(239,68,68,0.1)", border: "1px solid #ef4444", borderRadius: 8, padding: 16 }}>
                <p style={{ color: "#ef4444", margin: 0 }}>{error}</p>
              </div>
            ) : (
              <div style={{ backgroundColor: "rgba(34,197,94,0.1)", border: "1px solid #22c55e", borderRadius: 8, padding: 16 }}>
                <pre style={{ color: "#f8fafc", margin: 0, whiteSpace: "pre-wrap", fontSize: 12, maxHeight: 400, overflow: "auto" }}>
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}

            <div style={{ marginTop: 16, display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button onClick={() => setShowModal(false)} style={{
                padding: "8px 16px", backgroundColor: "#64748b", border: "none", borderRadius: 6, color: "white", cursor: "pointer"
              }}>Cerrar</button>
              {result && !error && (
                <button onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))} style={{
                  padding: "8px 16px", backgroundColor: color, border: "none", borderRadius: 6, color: "white", cursor: "pointer"
                }}>📋 Copiar</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
