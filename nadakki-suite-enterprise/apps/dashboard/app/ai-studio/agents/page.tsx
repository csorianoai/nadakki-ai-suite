"use client";
import { useState } from "react";

const CONTENT_AGENTS = [
  { id: "contentgeneratoria", name: "ContentGeneratorIA", status: "active", category: "Content" },
  { id: "copywriteria", name: "CopywriterIA", status: "active", category: "Content" },
  { id: "blogwriteria", name: "BlogWriterIA", status: "active", category: "Content" },
  { id: "emailwriteria", name: "EmailWriterIA", status: "active", category: "Email" },
  { id: "adcopyia", name: "AdCopyIA", status: "active", category: "Ads" },
  { id: "seowriteria", name: "SEOWriterIA", status: "active", category: "SEO" },
  { id: "socialcaptions", name: "SocialCaptionsIA", status: "active", category: "Social" },
  { id: "videoscriptia", name: "VideoScriptIA", status: "active", category: "Video" },
];

export default function AIAgentsPage() {
  const [agents] = useState(CONTENT_AGENTS);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🤖 Agentes de Contenido</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {agents.map((a, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#22c55e" }} />
              <span style={{ color: "#22c55e", fontSize: 11 }}>Activo</span>
            </div>
            <h4 style={{ color: "#f8fafc", fontSize: 14, margin: "0 0 4px 0" }}>{a.name}</h4>
            <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>{a.category}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
