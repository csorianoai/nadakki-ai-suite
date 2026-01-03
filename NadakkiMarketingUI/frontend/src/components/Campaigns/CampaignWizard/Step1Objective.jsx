import React from "react";

const objectives = [
  { id: "awareness", icon: "📢", name: "Awareness", description: "Aumentar alcance" },
  { id: "engagement", icon: "💬", name: "Engagement", description: "Generar interacción" },
  { id: "leads", icon: "📧", name: "Leads", description: "Capturar clientes" },
  { id: "sales", icon: "🛒", name: "Sales", description: "Impulsar ventas" },
  { id: "traffic", icon: "🔗", name: "Traffic", description: "Dirigir tráfico" }
];

export default function Step1Objective({ value, onChange }) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">¿Cuál es el objetivo?</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {objectives.map((obj) => (
          <button key={obj.id} type="button" onClick={() => onChange(obj.id)}
            className={`p-4 text-left rounded-lg border-2 transition-all ${value === obj.id ? "border-indigo-500 bg-indigo-50" : "border-gray-200 hover:border-gray-300"}`}>
            <span className="text-3xl">{obj.icon}</span>
            <h4 className="mt-2 font-medium">{obj.name}</h4>
            <p className="text-sm text-gray-500">{obj.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
