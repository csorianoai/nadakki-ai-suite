"use client";
import { useState } from "react";

const scheduledPosts = [
  { id: 1, content: "🚀 Nuevo lanzamiento! Descubre...", platforms: ["meta", "linkedin"], scheduledFor: "2026-01-02 10:00", status: "scheduled" },
  { id: 2, content: "Tips para mejorar tu productividad...", platforms: ["x", "tiktok"], scheduledFor: "2026-01-02 14:00", status: "scheduled" },
  { id: 3, content: "Behind the scenes de nuestro equipo...", platforms: ["meta"], scheduledFor: "2026-01-03 09:00", status: "draft" },
];

export default function PostSchedulerPage() {
  const [posts, setPosts] = useState(scheduledPosts);
  const [newPost, setNewPost] = useState({ content: "", platforms: [] as string[], scheduledFor: "" });
  const [showForm, setShowForm] = useState(false);

  const platformIcons: Record<string, string> = {
    meta: "📘", x: "🐦", tiktok: "🎵", linkedin: "💼", youtube: "▶️"
  };

  const togglePlatform = (platform: string) => {
    setNewPost(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform) 
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  const schedulePost = () => {
    if (newPost.content && newPost.platforms.length > 0 && newPost.scheduledFor) {
      setPosts(prev => [...prev, {
        id: Date.now(),
        content: newPost.content,
        platforms: newPost.platforms,
        scheduledFor: newPost.scheduledFor,
        status: "scheduled"
      }]);
      setNewPost({ content: "", platforms: [], scheduledFor: "" });
      setShowForm(false);
    }
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📅 Programador de Posts</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>{posts.filter(p => p.status === "scheduled").length} posts programados</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} style={{
          padding: "12px 24px", backgroundColor: "#22c55e", border: "none",
          borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer"
        }}>
          + Programar Post
        </button>
      </div>

      {showForm && (
        <div style={{ backgroundColor: "rgba(30,41,59,0.8)", border: "2px solid #22c55e", borderRadius: 16, padding: 24, marginBottom: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 16 }}>Nuevo Post</h3>
          
          <textarea
            value={newPost.content}
            onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
            placeholder="Escribe tu post aquí..."
            style={{
              width: "100%", minHeight: 100, padding: 16,
              backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)",
              borderRadius: 8, color: "#f8fafc", fontSize: 14, resize: "vertical"
            }}
          />

          <div style={{ marginTop: 16 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Plataformas:</p>
            <div style={{ display: "flex", gap: 12 }}>
              {Object.entries(platformIcons).map(([platform, icon]) => (
                <button key={platform} onClick={() => togglePlatform(platform)} style={{
                  padding: "10px 16px",
                  backgroundColor: newPost.platforms.includes(platform) ? "#22c55e" : "rgba(0,0,0,0.3)",
                  border: "none", borderRadius: 8, fontSize: 20, cursor: "pointer"
                }}>
                  {icon}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Fecha y hora:</p>
            <input
              type="datetime-local"
              value={newPost.scheduledFor}
              onChange={(e) => setNewPost(prev => ({ ...prev, scheduledFor: e.target.value }))}
              style={{
                padding: 12, backgroundColor: "rgba(0,0,0,0.3)",
                border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8,
                color: "#f8fafc", fontSize: 14
              }}
            />
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button onClick={schedulePost} style={{
              padding: "12px 24px", backgroundColor: "#22c55e", border: "none",
              borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer"
            }}>
              ✓ Programar
            </button>
            <button onClick={() => setShowForm(false)} style={{
              padding: "12px 24px", backgroundColor: "rgba(255,255,255,0.1)", border: "none",
              borderRadius: 8, color: "white", cursor: "pointer"
            }}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {posts.map((post) => (
          <div key={post.id} style={{
            backgroundColor: "rgba(30,41,59,0.5)",
            border: "1px solid rgba(51,65,85,0.5)",
            borderRadius: 16,
            padding: 20
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <p style={{ color: "#f8fafc", fontSize: 15, margin: 0, lineHeight: 1.5 }}>{post.content}</p>
                <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                  {post.platforms.map(p => (
                    <span key={p} style={{ fontSize: 18 }}>{platformIcons[p]}</span>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: "right", marginLeft: 20 }}>
                <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Programado para</p>
                <p style={{ color: "#f8fafc", fontSize: 14, fontWeight: 600, margin: "4px 0 0 0" }}>{post.scheduledFor}</p>
                <span style={{
                  display: "inline-block", marginTop: 8,
                  backgroundColor: post.status === "scheduled" ? "rgba(34,197,94,0.1)" : "rgba(245,158,11,0.1)",
                  color: post.status === "scheduled" ? "#22c55e" : "#f59e0b",
                  padding: "4px 12px", borderRadius: 20, fontSize: 11
                }}>
                  {post.status === "scheduled" ? "✓ Programado" : "📝 Borrador"}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
