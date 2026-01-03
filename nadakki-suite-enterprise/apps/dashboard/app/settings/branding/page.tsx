"use client";
import { useState } from "react";

export default function BrandingSettingsPage() {
  const [brand, setBrand] = useState({ name: "Nadakki", primaryColor: "#8b5cf6", secondaryColor: "#22c55e" });

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", marginBottom: 32 }}>🎨 Branding</h1>
      
      <div style={{ maxWidth: 600, backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, padding: 32 }}>
        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Nombre de Marca</label>
          <input value={brand.name} onChange={e => setBrand({...brand, name: e.target.value})}
            style={{ width: "100%", padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc" }} />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Logo</label>
          <div style={{ border: "2px dashed rgba(139,92,246,0.5)", borderRadius: 12, padding: 40, textAlign: "center" }}>
            <p style={{ color: "#64748b", margin: 0 }}>Arrastra tu logo aquí</p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
          <div>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Color Primario</label>
            <input type="color" value={brand.primaryColor} onChange={e => setBrand({...brand, primaryColor: e.target.value})}
              style={{ width: "100%", height: 50, backgroundColor: "transparent", border: "none", cursor: "pointer" }} />
          </div>
          <div>
            <label style={{ color: "#94a3b8", display: "block", marginBottom: 8 }}>Color Secundario</label>
            <input type="color" value={brand.secondaryColor} onChange={e => setBrand({...brand, secondaryColor: e.target.value})}
              style={{ width: "100%", height: 50, backgroundColor: "transparent", border: "none", cursor: "pointer" }} />
          </div>
        </div>

        <button style={{ width: "100%", padding: 14, backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          💾 Guardar Cambios
        </button>
      </div>
    </div>
  );
}
