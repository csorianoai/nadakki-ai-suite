import React from "react";

const frequencies = [
  { id: "once", name: "Una vez", icon: "1️⃣" },
  { id: "daily", name: "Diario", icon: "📅" },
  { id: "weekly", name: "Semanal", icon: "📆" },
  { id: "monthly", name: "Mensual", icon: "🗓️" }
];

export default function Step3Schedule({ data, onChange }) {
  const handleDateChange = (e) => {
    const date = e.target.value;
    const time = data.scheduled_at?.split("T")[1] || "09:00";
    onChange({ scheduled_at: `${date}T${time}` });
  };

  const handleTimeChange = (e) => {
    const time = e.target.value;
    const date = data.scheduled_at?.split("T")[0] || new Date().toISOString().split("T")[0];
    onChange({ scheduled_at: `${date}T${time}` });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">¿Cuándo publicar?</h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <button type="button" onClick={() => onChange({ publish_now: true, scheduled_at: null })}
          className={`p-4 text-left rounded-lg border-2 ${data.publish_now ? "border-indigo-500 bg-indigo-50" : "border-gray-200"}`}>
          <span className="text-2xl">🚀</span><h4 className="mt-2 font-medium">Publicar ahora</h4>
        </button>
        <button type="button" onClick={() => onChange({ publish_now: false })}
          className={`p-4 text-left rounded-lg border-2 ${!data.publish_now ? "border-indigo-500 bg-indigo-50" : "border-gray-200"}`}>
          <span className="text-2xl">📅</span><h4 className="mt-2 font-medium">Programar</h4>
        </button>
      </div>
      {!data.publish_now && (
        <div className="grid gap-4 sm:grid-cols-2 p-4 bg-gray-50 rounded-lg">
          <div>
            <label className="block text-sm font-medium mb-2">Fecha</label>
            <input type="date" value={data.scheduled_at?.split("T")[0] || ""} onChange={handleDateChange}
              min={new Date().toISOString().split("T")[0]} className="w-full px-4 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Hora</label>
            <input type="time" value={data.scheduled_at?.split("T")[1]?.substring(0, 5) || "09:00"} onChange={handleTimeChange}
              className="w-full px-4 py-2 border rounded-lg" />
          </div>
        </div>
      )}
      <div>
        <label className="block text-sm font-medium mb-2">Frecuencia</label>
        <div className="flex flex-wrap gap-3">
          {frequencies.map((freq) => (
            <button key={freq.id} type="button" onClick={() => onChange({ frequency: freq.id })}
              className={`px-4 py-2 rounded-lg border ${data.frequency === freq.id ? "border-indigo-500 bg-indigo-50" : "border-gray-200"}`}>
              <span>{freq.icon}</span> {freq.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
