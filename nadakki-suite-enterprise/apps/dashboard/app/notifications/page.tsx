"use client";
export default function NotificationsPage() {
  const notifications = [
    { type: "success", title: "Campaña completada", message: "Black Friday 2026 finalizó con ROI de 420%", time: "Hace 2 horas", read: false },
    { type: "warning", title: "Presupuesto bajo", message: "Campaña Q1 tiene solo 15% de presupuesto restante", time: "Hace 5 horas", read: false },
    { type: "info", title: "Nuevo lead", message: "María García se registró desde LinkedIn", time: "Hace 1 día", read: true },
    { type: "error", title: "Error de conexión", message: "No se pudo conectar con Instagram API", time: "Hace 2 días", read: true },
  ];

  const typeColors: Record<string, string> = { success: "#22c55e", warning: "#f59e0b", info: "#3b82f6", error: "#ef4444" };
  const typeIcons: Record<string, string> = { success: "✓", warning: "⚠", info: "ℹ", error: "✕" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🔔 Notificaciones</h1>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {notifications.map((n, i) => (
          <div key={i} style={{ backgroundColor: n.read ? "rgba(30,41,59,0.3)" : "rgba(30,41,59,0.5)", borderLeft: `4px solid ${typeColors[n.type]}`, borderRadius: "0 12px 12px 0", padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ display: "flex", gap: 12 }}>
                <span style={{ color: typeColors[n.type], fontSize: 20 }}>{typeIcons[n.type]}</span>
                <div>
                  <p style={{ color: "#f8fafc", fontWeight: 600, margin: 0 }}>{n.title}</p>
                  <p style={{ color: "#94a3b8", fontSize: 14, margin: "4px 0 0 0" }}>{n.message}</p>
                </div>
              </div>
              <span style={{ color: "#64748b", fontSize: 12 }}>{n.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
