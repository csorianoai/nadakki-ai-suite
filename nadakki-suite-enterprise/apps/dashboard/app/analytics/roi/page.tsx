"use client";
import { useState } from "react";

export default function ROICalculatorPage() {
  const [inputs, setInputs] = useState({ adSpend: 10000, revenue: 45000, leads: 150, customers: 25 });

  const roi = ((inputs.revenue - inputs.adSpend) / inputs.adSpend * 100).toFixed(1);
  const cpl = (inputs.adSpend / inputs.leads).toFixed(2);
  const cac = (inputs.adSpend / inputs.customers).toFixed(2);
  const ltv = (inputs.revenue / inputs.customers).toFixed(2);
  const ltvCacRatio = (parseFloat(ltv) / parseFloat(cac)).toFixed(2);

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📊 ROI Calculator</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>Calcula el retorno de inversión de tus campañas</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Inputs */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 24 }}>Datos de Entrada</h3>
          
          {[
            { key: "adSpend", label: "Inversión Publicitaria ($)", icon: "💰" },
            { key: "revenue", label: "Revenue Generado ($)", icon: "💵" },
            { key: "leads", label: "Leads Generados", icon: "👥" },
            { key: "customers", label: "Clientes Convertidos", icon: "🎯" },
          ].map(field => (
            <div key={field.key} style={{ marginBottom: 20 }}>
              <label style={{ color: "#94a3b8", fontSize: 14, display: "block", marginBottom: 8 }}>{field.icon} {field.label}</label>
              <input
                type="number"
                value={inputs[field.key as keyof typeof inputs]}
                onChange={(e) => setInputs(prev => ({ ...prev, [field.key]: Number(e.target.value) }))}
                style={{
                  width: "100%", padding: 14, backgroundColor: "rgba(0,0,0,0.3)",
                  border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", fontSize: 16
                }}
              />
            </div>
          ))}
        </div>

        {/* Results */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 16, padding: 24 }}>
          <h3 style={{ color: "#f8fafc", marginBottom: 24 }}>Resultados</h3>
          
          <div style={{ backgroundColor: parseFloat(roi) > 0 ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)", border: `2px solid ${parseFloat(roi) > 0 ? "#22c55e" : "#ef4444"}`, borderRadius: 12, padding: 20, marginBottom: 20, textAlign: "center" }}>
            <p style={{ color: "#64748b", fontSize: 14, margin: 0 }}>ROI Total</p>
            <p style={{ color: parseFloat(roi) > 0 ? "#22c55e" : "#ef4444", fontSize: 48, fontWeight: 800, margin: "8px 0 0 0" }}>{roi}%</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Costo por Lead (CPL)</p>
              <p style={{ color: "#f8fafc", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>${cpl}</p>
            </div>
            <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Costo Adq. Cliente (CAC)</p>
              <p style={{ color: "#f8fafc", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>${cac}</p>
            </div>
            <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Valor por Cliente (LTV)</p>
              <p style={{ color: "#22c55e", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>${ltv}</p>
            </div>
            <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
              <p style={{ color: "#64748b", fontSize: 12, margin: 0 }}>Ratio LTV:CAC</p>
              <p style={{ color: parseFloat(ltvCacRatio) >= 3 ? "#22c55e" : "#f59e0b", fontSize: 24, fontWeight: 700, margin: "8px 0 0 0" }}>{ltvCacRatio}x</p>
            </div>
          </div>

          <div style={{ marginTop: 20, padding: 16, backgroundColor: "rgba(139,92,246,0.1)", borderRadius: 12 }}>
            <p style={{ color: "#8b5cf6", fontSize: 14, margin: 0 }}>
              💡 {parseFloat(ltvCacRatio) >= 3 ? "Excelente ratio LTV:CAC. Tu negocio es saludable." : "Ratio LTV:CAC bajo. Considera optimizar tu CAC o aumentar retención."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
