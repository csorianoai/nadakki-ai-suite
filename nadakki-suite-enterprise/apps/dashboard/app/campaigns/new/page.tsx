"use client";
import { useState } from "react";

export default function NewCampaignPage() {
  const [step, setStep] = useState(1);
  const [campaign, setCampaign] = useState({ name: "", objective: "", budget: 5000, startDate: "", endDate: "", platforms: [] as string[] });

  const objectives = [
    { id: "awareness", name: "Brand Awareness", icon: "👁️", desc: "Aumentar visibilidad" },
    { id: "leads", name: "Generación de Leads", icon: "👥", desc: "Captar prospectos" },
    { id: "sales", name: "Ventas Directas", icon: "💰", desc: "Conversión inmediata" },
    { id: "engagement", name: "Engagement", icon: "❤️", desc: "Interacción" },
  ];

  const platforms = ["facebook", "instagram", "linkedin", "x", "tiktok", "youtube", "email"];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 8 }}>🚀 Nueva Campaña</h1>
      <p style={{ color: "#94a3b8", marginBottom: 32 }}>Paso {step} de 4</p>

      <div style={{ display: "flex", gap: 8, marginBottom: 32 }}>
        {[1,2,3,4].map(s => (
          <div key={s} style={{ flex: 1, height: 4, backgroundColor: s <= step ? "#8b5cf6" : "rgba(255,255,255,0.1)", borderRadius: 2 }} />
        ))}
      </div>

      <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32, maxWidth: 700 }}>
        {step === 1 && (
          <div>
            <h2 style={{ color: "#f8fafc", marginBottom: 24 }}>1. Información Básica</h2>
            <div style={{ marginBottom: 20 }}>
              <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Nombre de la Campaña</label>
              <input value={campaign.name} onChange={e => setCampaign({...campaign, name: e.target.value})}
                style={{ width: "100%", padding: 14, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }}
                placeholder="Ej: Black Friday 2026" />
            </div>
            <div style={{ marginBottom: 20 }}>
              <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Objetivo</label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
                {objectives.map(o => (
                  <div key={o.id} onClick={() => setCampaign({...campaign, objective: o.id})}
                    style={{ padding: 20, backgroundColor: campaign.objective === o.id ? "rgba(139,92,246,0.2)" : "rgba(0,0,0,0.2)",
                      border: campaign.objective === o.id ? "2px solid #8b5cf6" : "1px solid rgba(51,65,85,0.5)",
                      borderRadius: 12, cursor: "pointer" }}>
                    <span style={{ fontSize: 28 }}>{o.icon}</span>
                    <p style={{ color: "#f8fafc", fontWeight: 600, margin: "8px 0 4px 0" }}>{o.name}</p>
                    <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>{o.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 style={{ color: "#f8fafc", marginBottom: 24 }}>2. Presupuesto y Fechas</h2>
            <div style={{ marginBottom: 20 }}>
              <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Presupuesto Total ($)</label>
              <input type="number" value={campaign.budget} onChange={e => setCampaign({...campaign, budget: Number(e.target.value)})}
                style={{ width: "100%", padding: 14, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Fecha Inicio</label>
                <input type="date" value={campaign.startDate} onChange={e => setCampaign({...campaign, startDate: e.target.value})}
                  style={{ width: "100%", padding: 14, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
              </div>
              <div>
                <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Fecha Fin</label>
                <input type="date" value={campaign.endDate} onChange={e => setCampaign({...campaign, endDate: e.target.value})}
                  style={{ width: "100%", padding: 14, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 style={{ color: "#f8fafc", marginBottom: 24 }}>3. Plataformas</h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
              {platforms.map(p => (
                <button key={p} onClick={() => setCampaign({...campaign, platforms: campaign.platforms.includes(p) ? campaign.platforms.filter(x => x !== p) : [...campaign.platforms, p]})}
                  style={{ padding: 16, backgroundColor: campaign.platforms.includes(p) ? "#8b5cf6" : "rgba(0,0,0,0.2)",
                    border: "none", borderRadius: 12, color: "white", cursor: "pointer", textTransform: "capitalize" }}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 style={{ color: "#f8fafc", marginBottom: 24 }}>4. Resumen</h2>
            <div style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: 12, padding: 20 }}>
              <p style={{ color: "#94a3b8", margin: "0 0 8px 0" }}>Campaña: <span style={{ color: "#f8fafc", fontWeight: 600 }}>{campaign.name || "Sin nombre"}</span></p>
              <p style={{ color: "#94a3b8", margin: "0 0 8px 0" }}>Objetivo: <span style={{ color: "#f8fafc" }}>{campaign.objective || "No seleccionado"}</span></p>
              <p style={{ color: "#94a3b8", margin: "0 0 8px 0" }}>Presupuesto: <span style={{ color: "#22c55e", fontWeight: 600 }}>${campaign.budget.toLocaleString()}</span></p>
              <p style={{ color: "#94a3b8", margin: 0 }}>Plataformas: <span style={{ color: "#f8fafc" }}>{campaign.platforms.join(", ") || "Ninguna"}</span></p>
            </div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 32 }}>
          <button onClick={() => setStep(Math.max(1, step - 1))} disabled={step === 1}
            style={{ padding: "12px 24px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: step === 1 ? "not-allowed" : "pointer" }}>
            ← Anterior
          </button>
          {step < 4 ? (
            <button onClick={() => setStep(step + 1)}
              style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>
              Siguiente →
            </button>
          ) : (
            <button style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", cursor: "pointer", fontWeight: 600 }}>
              🚀 Lanzar Campaña
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
