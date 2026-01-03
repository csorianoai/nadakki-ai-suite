"use client";
export default function AIHistoryPage() {
  const history = [
    { date: "Hoy 14:32", type: "Social Post", platform: "Instagram", status: "published" },
    { date: "Hoy 10:15", type: "Email", platform: "Mailchimp", status: "scheduled" },
    { date: "Ayer 16:45", type: "Ad Copy", platform: "Facebook Ads", status: "published" },
    { date: "Ayer 09:20", type: "Blog Post", platform: "WordPress", status: "draft" },
  ];
  const statusColors: Record<string, string> = { published: "#22c55e", scheduled: "#3b82f6", draft: "#f59e0b" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📜 Historial de Generación</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {history.map((h, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>{h.date}</p>
              <p style={{ color: "#f8fafc", fontWeight: 600, margin: "4px 0 0 0" }}>{h.type}</p>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ color: "#64748b", fontSize: 13 }}>{h.platform}</span>
              <span style={{ backgroundColor: `${statusColors[h.status]}20`, color: statusColors[h.status], padding: "4px 12px", borderRadius: 20, fontSize: 12 }}>{h.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
