"use client";
import { useState } from "react";

export default function ContentCalendarPage() {
  const [currentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<number | null>(null);

  const scheduledContent = {
    2: [{ platform: "instagram", title: "Producto launch", time: "10:00" }],
    5: [{ platform: "linkedin", title: "Blog post share", time: "09:00" }, { platform: "x", title: "Thread", time: "14:00" }],
    8: [{ platform: "facebook", title: "Video promo", time: "18:00" }],
    12: [{ platform: "tiktok", title: "Behind scenes", time: "12:00" }],
    15: [{ platform: "instagram", title: "Story campaign", time: "11:00" }],
    18: [{ platform: "linkedin", title: "Case study", time: "10:00" }],
    22: [{ platform: "x", title: "Engagement post", time: "15:00" }],
    25: [{ platform: "instagram", title: "Carousel", time: "09:00" }, { platform: "facebook", title: "Ad campaign", time: "14:00" }],
  };

  const platformColors: Record<string, string> = {
    instagram: "#E4405F", facebook: "#1877F2", linkedin: "#0A66C2", x: "#000", tiktok: "#000", youtube: "#FF0000"
  };

  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📅 Content Calendar</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Enero 2026 • 12 posts programados</p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <button style={{ padding: "10px 20px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>← Anterior</button>
          <button style={{ padding: "10px 20px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>Siguiente →</button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
        {/* Days Header */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8, marginBottom: 16 }}>
          {["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"].map(day => (
            <div key={day} style={{ textAlign: "center", color: "#64748b", fontSize: 13, fontWeight: 600, padding: 8 }}>{day}</div>
          ))}
        </div>

        {/* Calendar Days */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8 }}>
          {/* Empty cells for days before month starts */}
          {Array(firstDayOfMonth).fill(null).map((_, i) => (
            <div key={`empty-${i}`} style={{ minHeight: 100 }} />
          ))}
          
          {/* Days of month */}
          {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
            const content = scheduledContent[day as keyof typeof scheduledContent];
            const isToday = day === new Date().getDate();
            
            return (
              <div key={day} onClick={() => setSelectedDate(day)} style={{
                minHeight: 100, padding: 8, borderRadius: 8, cursor: "pointer",
                backgroundColor: selectedDate === day ? "rgba(139,92,246,0.2)" : "rgba(0,0,0,0.2)",
                border: isToday ? "2px solid #8b5cf6" : "1px solid rgba(51,65,85,0.3)"
              }}>
                <p style={{ color: isToday ? "#8b5cf6" : "#f8fafc", fontSize: 14, fontWeight: 600, margin: 0 }}>{day}</p>
                {content && (
                  <div style={{ marginTop: 8 }}>
                    {content.map((item, idx) => (
                      <div key={idx} style={{
                        backgroundColor: platformColors[item.platform] + "30",
                        borderLeft: `3px solid ${platformColors[item.platform]}`,
                        padding: "4px 8px", borderRadius: 4, marginBottom: 4, fontSize: 11
                      }}>
                        <p style={{ color: "#f8fafc", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.title}</p>
                        <p style={{ color: "#64748b", margin: 0 }}>{item.time}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: "flex", gap: 16, marginTop: 24, justifyContent: "center" }}>
        {Object.entries(platformColors).map(([platform, color]) => (
          <div key={platform} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 12, height: 12, backgroundColor: color, borderRadius: 4 }} />
            <span style={{ color: "#94a3b8", fontSize: 12, textTransform: "capitalize" }}>{platform}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
