"use client";
import { useState } from "react";

export default function SocialEditorPage() {
  const [content, setContent] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["instagram"]);
  const [mediaType, setMediaType] = useState("image");

  const platforms = [
    { id: "instagram", name: "Instagram", formats: ["Post", "Story", "Reel", "Carousel"] },
    { id: "facebook", name: "Facebook", formats: ["Post", "Story", "Reel"] },
    { id: "linkedin", name: "LinkedIn", formats: ["Post", "Article", "Document"] },
    { id: "x", name: "X", formats: ["Tweet", "Thread"] },
    { id: "tiktok", name: "TikTok", formats: ["Video"] },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🎨 Editor Multiplataforma</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 400px", gap: 24 }}>
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <div style={{ marginBottom: 20 }}>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Plataformas</label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {platforms.map(p => (
                <button key={p.id} onClick={() => setSelectedPlatforms(prev => prev.includes(p.id) ? prev.filter(x => x !== p.id) : [...prev, p.id])}
                  style={{ padding: "8px 16px", backgroundColor: selectedPlatforms.includes(p.id) ? "#8b5cf6" : "rgba(0,0,0,0.3)",
                    border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Tipo de Media</label>
            <div style={{ display: "flex", gap: 8 }}>
              {["image", "video", "carousel", "text"].map(t => (
                <button key={t} onClick={() => setMediaType(t)}
                  style={{ padding: "8px 16px", backgroundColor: mediaType === t ? "#22c55e" : "rgba(0,0,0,0.3)",
                    border: "none", borderRadius: 8, color: "white", cursor: "pointer", textTransform: "capitalize" }}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Contenido</label>
            <textarea value={content} onChange={e => setContent(e.target.value)}
              placeholder="Escribe tu contenido aquí..."
              style={{ width: "100%", minHeight: 150, padding: 16, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", resize: "vertical" }} />
            <p style={{ color: "#64748b", fontSize: 12, marginTop: 8 }}>{content.length} / 2200 caracteres</p>
          </div>

          <div style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 20, marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", fontSize: 13, margin: "0 0 12px 0" }}>📎 Subir Media</p>
            <div style={{ border: "2px dashed rgba(139,92,246,0.5)", borderRadius: 8, padding: 40, textAlign: "center" }}>
              <p style={{ color: "#64748b", margin: 0 }}>Arrastra archivos aquí o haz clic para subir</p>
            </div>
          </div>

          <div style={{ display: "flex", gap: 12 }}>
            <button style={{ flex: 1, padding: 14, backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
              📅 Programar
            </button>
            <button style={{ flex: 1, padding: 14, backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
              🚀 Publicar Ahora
            </button>
          </div>
        </div>

        {/* Preview */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 16 }}>Vista Previa</h3>
          <div style={{ backgroundColor: "#000", borderRadius: 12, padding: 16, minHeight: 400 }}>
            <div style={{ backgroundColor: "#1a1a1a", borderRadius: 8, padding: 12, marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", backgroundColor: "#8b5cf6" }} />
                <span style={{ color: "#f8fafc", fontWeight: 600, fontSize: 14 }}>@tu_marca</span>
              </div>
              <div style={{ backgroundColor: "#333", borderRadius: 8, height: 200, marginBottom: 12, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ color: "#64748b" }}>📷 Preview</span>
              </div>
              <p style={{ color: "#f8fafc", fontSize: 14, lineHeight: 1.5, margin: 0 }}>{content || "Tu contenido aparecerá aquí..."}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
