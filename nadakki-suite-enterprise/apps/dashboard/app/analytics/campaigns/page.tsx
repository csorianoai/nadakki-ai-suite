"use client";
export default function AnalyticsCampaignsPage() {
  const campaigns = [
    { name: "Black Friday 2026", impressions: "2.4M", clicks: "89K", conversions: 2340, ctr: "3.7%", cost: 15000, revenue: 78000 },
    { name: "Lanzamiento Q1", impressions: "890K", clicks: "32K", conversions: 890, ctr: "3.6%", cost: 8000, revenue: 34000 },
    { name: "Brand Awareness", impressions: "5.2M", clicks: "145K", conversions: 567, ctr: "2.8%", cost: 20000, revenue: 45000 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📢 Analytics por Campaña</h1>
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "rgba(0,0,0,0.2)" }}>
              {["Campaña", "Impresiones", "Clicks", "Conv.", "CTR", "Costo", "Revenue", "ROI"].map(h => (
                <th key={h} style={{ padding: 16, textAlign: "left", color: "#94a3b8", fontSize: 13 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {campaigns.map((c, i) => {
              const roi = Math.round(((c.revenue - c.cost) / c.cost) * 100);
              return (
                <tr key={i} style={{ borderTop: "1px solid rgba(51,65,85,0.3)" }}>
                  <td style={{ padding: 16, color: "#f8fafc", fontWeight: 600 }}>{c.name}</td>
                  <td style={{ padding: 16, color: "#f8fafc" }}>{c.impressions}</td>
                  <td style={{ padding: 16, color: "#f8fafc" }}>{c.clicks}</td>
                  <td style={{ padding: 16, color: "#22c55e", fontWeight: 600 }}>{c.conversions}</td>
                  <td style={{ padding: 16, color: "#f8fafc" }}>{c.ctr}</td>
                  <td style={{ padding: 16, color: "#f8fafc" }}>${c.cost.toLocaleString()}</td>
                  <td style={{ padding: 16, color: "#22c55e" }}>${c.revenue.toLocaleString()}</td>
                  <td style={{ padding: 16, color: roi > 200 ? "#22c55e" : "#f59e0b", fontWeight: 700 }}>{roi}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
