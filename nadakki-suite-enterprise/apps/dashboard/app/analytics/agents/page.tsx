"use client";
export default function AnalyticsAgentsPage() {
  const agents = [
    { name: "LeadScoringIA", executions: 1234, avgTime: "1.2s", successRate: 98.5, leadsImpacted: 4500 },
    { name: "ContentGeneratorIA", executions: 567, avgTime: "3.4s", successRate: 96.2, postsCreated: 890 },
    { name: "CampaignOptimizerIA", executions: 234, avgTime: "2.1s", successRate: 99.1, budgetOptimized: 45000 },
    { name: "SentimentAnalyzerIA", executions: 890, avgTime: "0.8s", successRate: 97.8, mentionsAnalyzed: 12000 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🤖 Performance de Agentes IA</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20 }}>
        {agents.map((a, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <h3 style={{ color: "#f8fafc", fontSize: 18, margin: 0 }}>{a.name}</h3>
                <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{a.executions} ejecuciones</p>
              </div>
              <span style={{ backgroundColor: "rgba(34,197,94,0.1)", color: "#22c55e", padding: "4px 10px", borderRadius: 20, fontSize: 12 }}>
                {a.successRate}% éxito
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Tiempo Promedio</p>
                <p style={{ color: "#f8fafc", fontSize: 16, fontWeight: 600, margin: "4px 0 0 0" }}>{a.avgTime}</p>
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 8 }}>
                <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Impacto</p>
                <p style={{ color: "#8b5cf6", fontSize: 16, fontWeight: 600, margin: "4px 0 0 0" }}>
                  {a.leadsImpacted?.toLocaleString() || a.postsCreated || `$${a.budgetOptimized?.toLocaleString()}` || a.mentionsAnalyzed?.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
