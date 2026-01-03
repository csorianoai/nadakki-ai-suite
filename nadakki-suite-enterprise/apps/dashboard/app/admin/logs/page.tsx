"use client";
export default function AdminLogsPage() {
  const logs = [
    { time: "14:32:45", level: "info", agent: "LeadScoringIA", message: "Processed 15 leads successfully", duration: "1.2s" },
    { time: "14:30:12", level: "info", agent: "ContentGeneratorIA", message: "Generated 3 social posts", duration: "3.4s" },
    { time: "14:28:56", level: "warning", agent: "SentimentAnalyzerIA", message: "API rate limit approaching", duration: "0.8s" },
    { time: "14:25:33", level: "error", agent: "EmailSequenceMaster", message: "SMTP connection timeout", duration: "5.0s" },
    { time: "14:22:11", level: "info", agent: "CampaignOptimizerIA", message: "Budget reallocated successfully", duration: "2.1s" },
  ];

  const levelColors: Record<string, string> = { info: "#22c55e", warning: "#f59e0b", error: "#ef4444" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📜 Logs del Sistema</h1>
      
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, fontFamily: "monospace" }}>
          {logs.map((l, i) => (
            <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 8, padding: 12, display: "flex", gap: 16 }}>
              <span style={{ color: "#64748b" }}>{l.time}</span>
              <span style={{ color: levelColors[l.level], fontWeight: 600, minWidth: 60 }}>[{l.level.toUpperCase()}]</span>
              <span style={{ color: "#8b5cf6", minWidth: 180 }}>{l.agent}</span>
              <span style={{ color: "#f8fafc", flex: 1 }}>{l.message}</span>
              <span style={{ color: "#64748b" }}>{l.duration}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
