"use client";
import { useState } from "react";
import MarketingNav from "@/components/marketing/MarketingNav";
import AgentExecutor from "@/components/marketing/AgentExecutor";

// Estado REAL: ninguna red está conectada aún
const NETWORKS = [
  { 
    id: "facebook", 
    name: "Facebook", 
    logo: "📘", 
    color: "#1877f2", 
    connected: false, 
    apiRequired: "Meta Business API",
    setupUrl: "https://developers.facebook.com/apps/",
    description: "Requiere crear una app en Meta for Developers"
  },
  { 
    id: "instagram", 
    name: "Instagram", 
    logo: "📸", 
    color: "#e4405f", 
    connected: false,
    apiRequired: "Instagram Graph API",
    setupUrl: "https://developers.facebook.com/docs/instagram-api/",
    description: "Requiere cuenta Business conectada a Facebook"
  },
  { 
    id: "twitter", 
    name: "X (Twitter)", 
    logo: "🐦", 
    color: "#1da1f2", 
    connected: false,
    apiRequired: "Twitter API v2",
    setupUrl: "https://developer.twitter.com/",
    description: "Requiere cuenta de desarrollador de Twitter"
  },
  { 
    id: "linkedin", 
    name: "LinkedIn", 
    logo: "💼", 
    color: "#0a66c2", 
    connected: false,
    apiRequired: "LinkedIn Marketing API",
    setupUrl: "https://developer.linkedin.com/",
    description: "Requiere app en LinkedIn Developer Portal"
  },
  { 
    id: "tiktok", 
    name: "TikTok", 
    logo: "🎵", 
    color: "#010101", 
    connected: false,
    apiRequired: "TikTok for Business API",
    setupUrl: "https://developers.tiktok.com/",
    description: "Requiere cuenta TikTok for Business"
  },
  { 
    id: "youtube", 
    name: "YouTube", 
    logo: "📺", 
    color: "#ff0000", 
    connected: false,
    apiRequired: "YouTube Data API v3",
    setupUrl: "https://console.cloud.google.com/",
    description: "Requiere proyecto en Google Cloud Console"
  },
];

const AGENTS = [
  { id: "sociallisteningia", name: "Monitor de Redes Sociales", desc: "Monitorea menciones y conversaciones (requiere datos de entrada)", color: "#3b82f6", input: { keywords: ["nadakki", "fintech"], platform: "twitter" } },
  { id: "sentimentanalyzeria", name: "Analizador de Sentimiento", desc: "Analiza el sentimiento de textos que le proporciones", color: "#06b6d4", input: { text: "Me encanta este producto, es increíble!", source: "manual" } },
  { id: "influencermatcheria", name: "Buscador de Influencers", desc: "Encuentra influencers por nicho y criterios", color: "#0ea5e9", input: { niche: "fintech", min_followers: 10000, region: "latam" } },
  { id: "influencermatchingia", name: "Emparejador de Influencers", desc: "Match avanzado con scoring de afinidad de marca", color: "#8b5cf6", input: { brand_values: ["innovation", "trust"], campaign_type: "awareness" } },
];

export default function SocialPage() {
  const [tab, setTab] = useState<"networks" | "agents">("networks");
  const [showSetupModal, setShowSetupModal] = useState<string | null>(null);

  const selectedNetwork = NETWORKS.find(n => n.id === showSetupModal);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📱 Social Media</h1>
          <p style={{ color: "#94a3b8", marginTop: 8 }}>Monitoreo y análisis de redes sociales</p>
        </div>
        <span style={{ backgroundColor: "rgba(245,158,11,0.2)", color: "#f59e0b", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600 }}>
          ⚠️ {NETWORKS.filter(n => n.connected).length} conectadas
        </span>
      </div>
      <MarketingNav />

      {/* Info banner */}
      <div style={{ 
        backgroundColor: "rgba(59,130,246,0.1)", 
        border: "1px solid rgba(59,130,246,0.3)", 
        borderRadius: 12, 
        padding: 16, 
        marginBottom: 24,
        display: "flex",
        alignItems: "center",
        gap: 12
      }}>
        <span style={{ fontSize: 24 }}>ℹ️</span>
        <div>
          <p style={{ color: "#3b82f6", margin: 0, fontWeight: 600 }}>Conexión de Redes Sociales</p>
          <p style={{ color: "#94a3b8", margin: "4px 0 0 0", fontSize: 13 }}>
            Para conectar tus redes sociales reales, necesitas configurar las APIs correspondientes. 
            Los agentes de análisis funcionan con datos que les proporciones manualmente.
          </p>
        </div>
      </div>

      <div style={{ display: "flex", gap: 4, marginBottom: 24, backgroundColor: "rgba(30,41,59,0.5)", padding: 4, borderRadius: 12, width: "fit-content" }}>
        {[{ id: "networks", label: "🔗 Redes Sociales" }, { id: "agents", label: "🤖 Agentes de Análisis" }].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id as any)} style={{
            padding: "10px 20px", backgroundColor: tab === t.id ? "#3b82f6" : "transparent",
            border: "none", borderRadius: 8, color: tab === t.id ? "white" : "#94a3b8", cursor: "pointer", fontWeight: 600
          }}>{t.label}</button>
        ))}
      </div>

      {tab === "networks" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
          {NETWORKS.map((net) => (
            <div key={net.id} style={{
              backgroundColor: "rgba(30,41,59,0.5)", 
              border: "1px solid rgba(51,65,85,0.5)",
              borderRadius: 16, 
              padding: 24,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                <span style={{ fontSize: 40 }}>{net.logo}</span>
                <div>
                  <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: 0 }}>{net.name}</h3>
                  <span style={{
                    fontSize: 11, padding: "3px 10px", borderRadius: 10,
                    backgroundColor: "rgba(239,68,68,0.2)",
                    color: "#ef4444"
                  }}>⚠️ No conectado</span>
                </div>
              </div>
              
              <p style={{ color: "#64748b", fontSize: 13, margin: "0 0 16px 0" }}>
                {net.description}
              </p>

              <div style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 8, padding: 12, marginBottom: 16 }}>
                <p style={{ color: "#94a3b8", fontSize: 11, margin: 0 }}>API Requerida:</p>
                <p style={{ color: "#f8fafc", fontSize: 13, margin: "4px 0 0 0", fontWeight: 600 }}>{net.apiRequired}</p>
              </div>

              <div style={{ display: "flex", gap: 8 }}>
                <button 
                  onClick={() => setShowSetupModal(net.id)}
                  style={{
                    flex: 1,
                    padding: 12,
                    backgroundColor: net.color,
                    border: "none",
                    borderRadius: 8,
                    color: "white",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: 13
                  }}
                >
                  🔗 Conectar
                </button>
                <a href={net.setupUrl} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
                  <button style={{
                    padding: "12px 16px",
                    backgroundColor: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(51,65,85,0.5)",
                    borderRadius: 8,
                    color: "#94a3b8",
                    cursor: "pointer",
                    fontSize: 13
                  }}>
                    📖 Docs
                  </button>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "agents" && (
        <>
          <div style={{ 
            backgroundColor: "rgba(34,197,94,0.1)", 
            border: "1px solid rgba(34,197,94,0.3)", 
            borderRadius: 12, 
            padding: 16, 
            marginBottom: 24 
          }}>
            <p style={{ color: "#22c55e", margin: 0, fontSize: 14 }}>
              ✅ <strong>Estos agentes SÍ funcionan</strong> - Analizan datos que les proporciones como input. 
              No requieren conexión a redes sociales.
            </p>
          </div>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 20 }}>
            {AGENTS.map((agent) => (
              <div key={agent.id} style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 16, padding: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                  <div>
                    <h3 style={{ color: "#f8fafc", fontSize: 18, fontWeight: 600, margin: 0 }}>{agent.name}</h3>
                    <code style={{ color: "#64748b", fontSize: 11 }}>{agent.id}</code>
                  </div>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#22c55e" }} />
                </div>
                <p style={{ color: "#94a3b8", fontSize: 14, margin: "0 0 16px 0" }}>{agent.desc}</p>
                <AgentExecutor agentId={agent.id} agentName={agent.name} color={agent.color} defaultInput={agent.input} />
              </div>
            ))}
          </div>
        </>
      )}

      {/* Modal de configuración */}
      {showSetupModal && selectedNetwork && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.8)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000
        }} onClick={() => setShowSetupModal(null)}>
          <div style={{
            backgroundColor: "#1e293b", borderRadius: 16, padding: 32,
            maxWidth: 500, width: "90%"
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
              <span style={{ fontSize: 48 }}>{selectedNetwork.logo}</span>
              <div>
                <h2 style={{ color: "#f8fafc", margin: 0 }}>Conectar {selectedNetwork.name}</h2>
                <p style={{ color: "#64748b", margin: "4px 0 0 0" }}>{selectedNetwork.apiRequired}</p>
              </div>
            </div>

            <div style={{ backgroundColor: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 8, padding: 16, marginBottom: 24 }}>
              <p style={{ color: "#f59e0b", margin: 0, fontWeight: 600 }}>⚠️ Requiere configuración del backend</p>
              <p style={{ color: "#94a3b8", margin: "8px 0 0 0", fontSize: 13 }}>
                Para conectar {selectedNetwork.name}, necesitas:
              </p>
              <ol style={{ color: "#94a3b8", margin: "8px 0 0 0", paddingLeft: 20, fontSize: 13 }}>
                <li>Crear una app en el portal de desarrolladores</li>
                <li>Obtener las credenciales (Client ID, Secret)</li>
                <li>Configurar OAuth en el backend de Nadakki</li>
                <li>Implementar el flujo de autorización</li>
              </ol>
            </div>

            <div style={{ display: "flex", gap: 12 }}>
              <a href={selectedNetwork.setupUrl} target="_blank" rel="noopener noreferrer" style={{ flex: 1, textDecoration: "none" }}>
                <button style={{
                  width: "100%", padding: 14, backgroundColor: selectedNetwork.color,
                  border: "none", borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer"
                }}>
                  📖 Ir a Developer Portal
                </button>
              </a>
              <button onClick={() => setShowSetupModal(null)} style={{
                padding: "14px 24px", backgroundColor: "#64748b",
                border: "none", borderRadius: 8, color: "white", cursor: "pointer"
              }}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
