import React, { useState } from "react";
import Step1Objective from "./Step1Objective";
import Step2Content from "./Step2Content";
import Step3Schedule from "./Step3Schedule";
import Step4Networks from "./Step4Networks";

const steps = [
  { id: 1, name: "Objetivo", icon: "🎯" },
  { id: 2, name: "Contenido", icon: "📝" },
  { id: 3, name: "Programación", icon: "📅" },
  { id: 4, name: "Redes", icon: "📱" }
];

export default function CampaignWizard({ connections = [], onSubmit, onCancel, initialData = {} }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "", objective: "awareness", content_type: "text", content_text: "", content_media_urls: [],
    hashtags: [], scheduled_at: null, frequency: "once", target_pages: [], publish_now: false, ...initialData
  });
  const [submitting, setSubmitting] = useState(false);

  const updateFormData = (updates) => setFormData((prev) => ({ ...prev, ...updates }));
  const nextStep = () => { if (currentStep < 4) setCurrentStep(currentStep + 1); };
  const prevStep = () => { if (currentStep > 1) setCurrentStep(currentStep - 1); };

  const handleSubmit = async () => {
    setSubmitting(true);
    try { await onSubmit(formData); } finally { setSubmitting(false); }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1: return !!formData.objective;
      case 2: return !!(formData.content_text || formData.content_media_urls?.length);
      case 3: return formData.publish_now || !!formData.scheduled_at;
      case 4: return formData.target_pages?.length > 0;
      default: return false;
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${currentStep >= step.id ? "bg-indigo-600 text-white" : "bg-gray-200"}`}>
                {step.icon}
              </div>
              <span className="mt-2 text-xs">{step.name}</span>
            </div>
            {idx < steps.length - 1 && <div className={`flex-1 h-1 mx-2 ${currentStep > step.id ? "bg-indigo-600" : "bg-gray-200"}`} />}
          </React.Fragment>
        ))}
      </div>
      {currentStep === 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Nombre de la campaña</label>
          <input type="text" value={formData.name} onChange={(e) => updateFormData({ name: e.target.value })}
            placeholder="Ej: Campaña Black Friday" className="w-full px-4 py-2 border rounded-lg" />
        </div>
      )}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        {currentStep === 1 && <Step1Objective value={formData.objective} onChange={(v) => updateFormData({ objective: v })} />}
        {currentStep === 2 && <Step2Content data={formData} onChange={updateFormData} />}
        {currentStep === 3 && <Step3Schedule data={formData} onChange={updateFormData} />}
        {currentStep === 4 && <Step4Networks data={formData} onChange={updateFormData} connections={connections} />}
      </div>
      <div className="flex justify-between mt-6">
        <button type="button" onClick={currentStep === 1 ? onCancel : prevStep} className="px-4 py-2 text-gray-600">
          {currentStep === 1 ? "Cancelar" : "← Anterior"}
        </button>
        {currentStep < 4 ? (
          <button type="button" onClick={nextStep} disabled={!canProceed()} className="px-6 py-2 bg-indigo-600 text-white rounded-lg disabled:opacity-50">
            Siguiente →
          </button>
        ) : (
          <button type="button" onClick={handleSubmit} disabled={!canProceed() || submitting} className="px-6 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50">
            {submitting ? "⏳ Creando..." : "✓ Crear Campaña"}
          </button>
        )}
      </div>
    </div>
  );
}
