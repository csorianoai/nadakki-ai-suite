"use client";
import { useState, useEffect } from "react";
interface Agent { id: string; name: string; category: string; }
export default function ventascrmPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  useEffect(() => {
    fetch("https://nadakki-ai-suite.onrender.com/api/catalog/ventascrm/agents")
      .then((res) => res.json())
      .then((data) => { setAgents(data.agents || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);
  const executeAgent = async (agentId: string) => {
    setExecuting(agentId);
    setResult(null);
    setShowModal(true);
    try {
      const response = await fetch("https://nadakki-ai-suite.onrender.com/agents/ventascrm/" + agentId + "/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_data: { test: true }, tenant_id: "credicefi" })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: "Error executing agent" });
    }
    setExecuting(null);
  };
  if (loading) return <div className="p-8 text-center">Loading...</div>;
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6 capitalize">Ventascrm Agents</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <div key={agent.id} className="border rounded-lg p-4 hover:shadow-lg transition">
            <h3 className="font-semibold text-lg">{agent.name}</h3>
            <p className="text-gray-500 text-sm mb-3">{agent.category}</p>
            <button
              onClick={() => executeAgent(agent.id)}
              disabled={executing === agent.id}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {executing === agent.id ? "Executing..." : "Execute"}
            </button>
          </div>
        ))}
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-auto">
            <h2 className="text-xl font-bold mb-4">Execution Result</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
            <button onClick={() => setShowModal(false)} className="mt-4 bg-gray-600 text-white px-4 py-2 rounded">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
