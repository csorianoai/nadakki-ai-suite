"use client";
export default function SocialFeedsPage() {
  const feeds = {
    instagram: [
      { content: "🚀 Nuevo producto lanzado!", likes: 234, comments: 45, time: "2h" },
      { content: "Behind the scenes de nuestro equipo", likes: 189, comments: 23, time: "1d" },
    ],
    linkedin: [
      { content: "Artículo: 10 tendencias de marketing 2026", likes: 567, comments: 89, time: "3h" },
      { content: "Estamos contratando! Únete al equipo", likes: 234, comments: 45, time: "2d" },
    ],
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>📰 Social Feeds</h1>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {Object.entries(feeds).map(([platform, posts]) => (
          <div key={platform} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
            <h2 style={{ color: "#f8fafc", fontSize: 18, marginBottom: 16, textTransform: "capitalize" }}>📱 {platform}</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {posts.map((p, i) => (
                <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 16 }}>
                  <p style={{ color: "#f8fafc", fontSize: 14, margin: "0 0 12px 0" }}>{p.content}</p>
                  <div style={{ display: "flex", gap: 16 }}>
                    <span style={{ color: "#ef4444", fontSize: 13 }}>❤️ {p.likes}</span>
                    <span style={{ color: "#3b82f6", fontSize: 13 }}>💬 {p.comments}</span>
                    <span style={{ color: "#64748b", fontSize: 13 }}>• {p.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
