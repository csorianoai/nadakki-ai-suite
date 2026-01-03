"use client";
export default function SchedulerJobsPage() {
  const jobs = [
    { name: "Daily Social Post", schedule: "Diario 10:00 AM", nextRun: "Mañana", status: "active", runs: 45 },
    { name: "Weekly Newsletter", schedule: "Lunes 9:00 AM", nextRun: "En 3 días", status: "active", runs: 12 },
    { name: "Lead Scoring Update", schedule: "Cada 6 horas", nextRun: "En 2 horas", status: "active", runs: 234 },
    { name: "Competitor Analysis", schedule: "Diario 6:00 AM", nextRun: "Mañana", status: "paused", runs: 30 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📋 Trabajos Programados</h1>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {jobs.map((j, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: j.status === "active" ? "#22c55e" : "#64748b" }} />
              <div>
                <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{j.name}</p>
                <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{j.schedule} • Próximo: {j.nextRun}</p>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ color: "#94a3b8", fontSize: 13 }}>{j.runs} ejecuciones</span>
              <button style={{ padding: "8px 16px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 6, color: "white", cursor: "pointer" }}>
                {j.status === "active" ? "⏸️" : "▶️"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
