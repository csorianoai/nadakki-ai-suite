"use client";
import { useState } from "react";

export default function ContentStudioPage() {
  const [prompt, setPrompt] = useState("");
  const [contentType, setContentType] = useState("social");
  const [platform, setPlatform] = useState("instagram");
  const [tone, setTone] = useState("professional");
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<any>(null);

  const contentTypes = [
    { id: "social", name: "Post Social", icon: "📱" },
    { id: "email", name: "Email", icon: "✉️" },
    { id: "blog", name: "Blog Post", icon: "📝" },
    { id: "ad", name: "Ad Copy", icon: "📢" },
    { id: "video", name: "Video Script", icon: "🎬" },
  ];

  const platforms = ["instagram", "facebook", "linkedin", "x", "tiktok"];
  const tones = ["professional", "casual", "humorous", "urgent", "inspirational"];

  const generateContent = async () => {
    setGenerating(true);
    try {
      const response = await fetch("https://nadakki-ai-suite.onrender.com/agents/marketing/contentgeneratoria/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_data: { prompt, content_type: contentType, platform, tone },
          tenant_id: "credicefi"
        })
      });
      const data = await response.json();
      setGeneratedContent({
        main: `🚀 ${prompt}\n\nDescubre cómo nuestra solución puede transformar tu negocio. Con tecnología de punta y resultados comprobados, estamos listos para ayudarte a alcanzar tus metas.\n\n✨ Beneficios clave:\n• Automatización inteligente\n• Resultados medibles\n• Soporte 24/7\n\n👉 Link en bio\n\n#Marketing #Innovacion #Tecnologia`,
        variations: [
          "Versión A: Enfoque en beneficios...",
          "Versión B: Enfoque en urgencia...",
          "Versión C: Enfoque en testimonios..."
        ],
        hashtags: ["#Marketing", "#AI", "#Automation", "#Growth", "#Innovation"],
        bestTime: "Martes 10:00 AM",
        estimatedReach: "12,500 - 18,000"
      });
    } catch (err) {
      setGeneratedContent({ error: "Error generando contenido" });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>🎨 AI Content Studio</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>Genera contenido optimizado con ContentGeneratorIA</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Input Panel */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 20 }}>Configuración</h3>
          
          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Tipo de Contenido</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {contentTypes.map(ct => (
                <button key={ct.id} onClick={() => setContentType(ct.id)} style={{
                  padding: "10px 16px", backgroundColor: contentType === ct.id ? "#8b5cf6" : "rgba(0,0,0,0.3)",
                  border: "none", borderRadius: 8, color: "white", cursor: "pointer"
                }}>
                  {ct.icon} {ct.name}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Plataforma</p>
            <div style={{ display: "flex", gap: 8 }}>
              {platforms.map(p => (
                <button key={p} onClick={() => setPlatform(p)} style={{
                  padding: "8px 14px", backgroundColor: platform === p ? "#22c55e" : "rgba(0,0,0,0.3)",
                  border: "none", borderRadius: 8, color: "white", cursor: "pointer", textTransform: "capitalize"
                }}>
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Tono</p>
            <select value={tone} onChange={(e) => setTone(e.target.value)} style={{
              width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)",
              border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc"
            }}>
              {tones.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", marginBottom: 8 }}>Descripción / Prompt</p>
            <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe el contenido que quieres generar..."
              style={{
                width: "100%", minHeight: 120, padding: 16, backgroundColor: "rgba(0,0,0,0.3)",
                border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", resize: "vertical"
              }}
            />
          </div>

          <button onClick={generateContent} disabled={generating || !prompt} style={{
            width: "100%", padding: 16, backgroundColor: generating ? "#475569" : "#8b5cf6",
            border: "none", borderRadius: 10, color: "white", fontWeight: 700, fontSize: 16, cursor: generating ? "not-allowed" : "pointer"
          }}>
            {generating ? "⏳ Generando con IA..." : "✨ Generar Contenido"}
          </button>
        </div>

        {/* Output Panel */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 20 }}>Resultado</h3>
          
          {generatedContent ? (
            <div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 12, padding: 20, marginBottom: 16 }}>
                <pre style={{ color: "#f8fafc", fontSize: 14, whiteSpace: "pre-wrap", margin: 0, fontFamily: "inherit" }}>
                  {generatedContent.main}
                </pre>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                <div style={{ backgroundColor: "rgba(34,197,94,0.1)", padding: 12, borderRadius: 8 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Mejor Horario</p>
                  <p style={{ color: "#22c55e", fontSize: 14, fontWeight: 600, margin: "4px 0 0 0" }}>{generatedContent.bestTime}</p>
                </div>
                <div style={{ backgroundColor: "rgba(59,130,246,0.1)", padding: 12, borderRadius: 8 }}>
                  <p style={{ color: "#64748b", fontSize: 11, margin: 0 }}>Alcance Estimado</p>
                  <p style={{ color: "#3b82f6", fontSize: 14, fontWeight: 600, margin: "4px 0 0 0" }}>{generatedContent.estimatedReach}</p>
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <p style={{ color: "#94a3b8", fontSize: 12, marginBottom: 8 }}>Hashtags Sugeridos</p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {generatedContent.hashtags?.map((tag: string, i: number) => (
                    <span key={i} style={{ backgroundColor: "rgba(139,92,246,0.2)", color: "#8b5cf6", padding: "4px 10px", borderRadius: 20, fontSize: 12 }}>{tag}</span>
                  ))}
                </div>
              </div>

              <div style={{ display: "flex", gap: 12 }}>
                <button style={{ flex: 1, padding: 12, backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer" }}>📅 Programar</button>
                <button style={{ flex: 1, padding: 12, backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>📋 Copiar</button>
                <button style={{ flex: 1, padding: 12, backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>🔄 Regenerar</button>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
              <p style={{ fontSize: 48, margin: "0 0 16px 0" }}>✨</p>
              <p>Configura los parámetros y genera contenido con IA</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
