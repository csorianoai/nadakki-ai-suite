"use client";
import { useState } from "react";

export default function SocialAnalyticsPage() {
  const [period, setPeriod] = useState("7d");

  const platformStats = [
    { platform: "Instagram", icon: "📸", followers: "45.2K", growth: "+2.3%", engagement: "4.8%", posts: 24, reach: "125K" },
    { platform: "Facebook", icon: "📘", followers: "32.1K", growth: "+1.1%", engagement: "2.1%", posts: 18, reach: "89K" },
    { platform: "LinkedIn", icon: "💼", followers: "28.5K", growth: "+3.5%", engagement: "5.2%", posts: 12, reach: "67K" },
    { platform: "X", icon: "🐦", followers: "18.9K", growth: "+0.8%", engagement: "3.4%", posts: 45, reach: "234K" },
    { platform: "TikTok", icon: "🎵", followers: "12.3K", growth: "+8.2%", engagement: "12.5%", posts: 8, reach: "456K" },
  ];

  const topPosts = [
    { platform: "TikTok", title: "Behind the scenes video", likes: "12.4K", comments: 892, shares: 2340 },
    { platform: "Instagram", title: "Product carousel", likes: "8.2K", comments: 456, shares: 234 },
    { platform: "LinkedIn", title: "Industry insights", likes: "2.1K", comments: 189, shares: 567 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📊 Social Analytics</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Métricas unificadas de todas las plataformas</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {["24h", "7d", "30d", "90d"].map(p => (
            <button key={p} onClick={() => setPeriod(p)} style={{
              padding: "8px 16px", backgroundColor: period === p ? "#8b5cf6" : "rgba(255,255,255,0.1)",
              border: "none", borderRadius: 8, color: "white", cursor: "pointer"
            }}>{p}</button>
          ))}
        </div>
      </div>

      {/* Platform Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16, marginBottom: 32 }}>
        {platformStats.map((stat, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
              <span style={{ fontSize: 28 }}>{stat.icon}</span>
              <span style={{ color: "#f8fafc", fontWeight: 600 }}>{stat.platform}</span>
            </div>
            <p style={{ color: "#f8fafc", fontSize: 28, fontWeight: 700, margin: 0 }}>{stat.followers}</p>
            <p style={{ color: "#22c55e", fontSize: 13, margin: "4px 0 0 0" }}>{stat.growth} seguidores</p>
            <div style={{ borderTop: "1px solid rgba(51,65,85,0.5)", marginTop: 16, paddingTop: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ color: "#64748b", fontSize: 12 }}>Engagement</span>
                <span style={{ color: "#f8fafc", fontSize: 12, fontWeight: 600 }}>{stat.engagement}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ color: "#64748b", fontSize: 12 }}>Posts</span>
                <span style={{ color: "#f8fafc", fontSize: 12, fontWeight: 600 }}>{stat.posts}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#64748b", fontSize: 12 }}>Alcance</span>
                <span style={{ color: "#f8fafc", fontSize: 12, fontWeight: 600 }}>{stat.reach}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24 }}>
        {/* Engagement Chart */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h2 style={{ color: "#f8fafc", fontSize: 18, marginBottom: 20 }}>📈 Engagement por Día</h2>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 200 }}>
            {[45, 62, 58, 75, 82, 68, 95].map((value, i) => (
              <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{ width: "100%", height: `${value * 2}px`, background: "linear-gradient(180deg, #8b5cf6, #6366f1)", borderRadius: "8px 8px 0 0" }} />
                <p style={{ color: "#64748b", fontSize: 11, marginTop: 8 }}>{["L", "M", "X", "J", "V", "S", "D"][i]}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Top Posts */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h2 style={{ color: "#f8fafc", fontSize: 18, marginBottom: 20 }}>🏆 Top Posts</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {topPosts.map((post, i) => (
              <div key={i} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <span style={{ color: "#f8fafc", fontWeight: 600 }}>{post.title}</span>
                  <span style={{ color: "#64748b", fontSize: 12 }}>{post.platform}</span>
                </div>
                <div style={{ display: "flex", gap: 16 }}>
                  <span style={{ color: "#ef4444", fontSize: 13 }}>❤️ {post.likes}</span>
                  <span style={{ color: "#3b82f6", fontSize: 13 }}>💬 {post.comments}</span>
                  <span style={{ color: "#22c55e", fontSize: 13 }}>🔄 {post.shares}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
