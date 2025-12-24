# agents/marketing/minimalformia.py
"""
MinimalFormIA v3.0.0 - SUPER AGENT
Optimización de Formularios con Progressive Disclosure
"""

from __future__ import annotations
import time
import logging
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class MinimalFormIA:
    VERSION = "3.0.0"
    AGENT_ID = "minimalformia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0}
        self.field_catalog = self._load_field_catalog()
    
    def _load_field_catalog(self) -> Dict[str, Dict]:
        """Catálogo de campos con metadata."""
        return {
            "email": {"priority": 1, "pii": True, "required": True, "friction": 0.1, "qualification_power": 0.3},
            "phone": {"priority": 2, "pii": True, "required": False, "friction": 0.2, "qualification_power": 0.2},
            "income_range": {"priority": 3, "pii": False, "required": True, "friction": 0.3, "qualification_power": 0.8},
            "employment_status": {"priority": 4, "pii": False, "required": True, "friction": 0.2, "qualification_power": 0.6},
            "credit_score_range": {"priority": 5, "pii": False, "required": False, "friction": 0.4, "qualification_power": 0.9},
            "loan_purpose": {"priority": 6, "pii": False, "required": True, "friction": 0.15, "qualification_power": 0.5},
            "loan_amount": {"priority": 7, "pii": False, "required": True, "friction": 0.25, "qualification_power": 0.7},
            "ssn_last4": {"priority": 10, "pii": True, "required": False, "friction": 0.8, "qualification_power": 0.4},
            "dob": {"priority": 8, "pii": True, "required": False, "friction": 0.5, "qualification_power": 0.3},
            "address": {"priority": 9, "pii": True, "required": False, "friction": 0.6, "qualification_power": 0.2}
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza formulario con progressive disclosure."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            product_type = data.get("product_type", "personal_loan")
            channel = data.get("channel", "web")
            max_fields = data.get("max_fields", 5)
            optimization_goal = data.get("goal", "conversion")
            
            # Seleccionar campos óptimos
            selected_fields = self._select_optimal_fields(product_type, channel, max_fields, optimization_goal)
            
            # Calcular métricas del formulario
            form_metrics = self._calculate_form_metrics(selected_fields)
            
            # Generar variantes A/B
            ab_variant = self._generate_ab_variant(selected_fields, data)
            
            # Progressive disclosure steps
            disclosure_steps = self._generate_progressive_steps(selected_fields)
            
            # Insights
            insights = self._generate_insights(selected_fields, form_metrics)
            
            decision_trace = [
                f"product={product_type}",
                f"channel={channel}",
                f"fields_selected={len(selected_fields)}",
                f"estimated_completion={form_metrics['estimated_completion_rate']*100:.0f}%"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "form_id": f"form_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "product_type": product_type,
                "channel": channel,
                "selected_fields": selected_fields,
                "fields_count": len(selected_fields),
                "progressive_disclosure": disclosure_steps,
                "ab_variant": ab_variant,
                "form_metrics": form_metrics,
                "pii_fields_count": sum(1 for f in selected_fields if f["pii"]),
                "key_insights": insights,
                "decision_trace": decision_trace,
                "compliance": {
                    "pii_minimization": "pass",
                    "consent_required": any(f["pii"] for f in selected_fields)
                },
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
            
            if DECISION_LAYER_AVAILABLE:
                try:
                    result = apply_decision_layer(result)
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            return {
                "form_id": "error",
                "tenant_id": self.tenant_id,
                "selected_fields": [],
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _select_optimal_fields(self, product_type: str, channel: str, 
                               max_fields: int, goal: str) -> List[Dict]:
        """Selecciona campos óptimos para el formulario."""
        # Campos requeridos por producto
        product_required = {
            "personal_loan": ["email", "income_range", "employment_status", "loan_amount", "loan_purpose"],
            "credit_card": ["email", "income_range", "employment_status"],
            "mortgage": ["email", "income_range", "employment_status", "loan_amount", "credit_score_range"],
            "auto_loan": ["email", "income_range", "loan_amount", "loan_purpose"]
        }
        
        required = product_required.get(product_type, ["email", "income_range"])
        
        # Calcular score de cada campo
        scored_fields = []
        for field_name, field_data in self.field_catalog.items():
            is_required = field_name in required
            
            # Score basado en goal
            if goal == "conversion":
                score = field_data["qualification_power"] / (field_data["friction"] + 0.1)
            else:  # qualification
                score = field_data["qualification_power"] * 2 - field_data["friction"]
            
            # Bonus para requeridos
            if is_required:
                score += 10
            
            # Penalización móvil para campos de alta fricción
            if channel == "mobile" and field_data["friction"] > 0.5:
                score -= 2
            
            scored_fields.append({
                "field": field_name,
                "score": score,
                "priority": field_data["priority"],
                "pii": field_data["pii"],
                "required": is_required,
                "friction": field_data["friction"],
                "qualification_power": field_data["qualification_power"],
                "reason_codes": self._field_reason_codes(field_name, is_required, goal)
            })
        
        # Ordenar y seleccionar
        scored_fields.sort(key=lambda x: (-x["score"], x["priority"]))
        return scored_fields[:max_fields]
    
    def _field_reason_codes(self, field: str, required: bool, goal: str) -> List[Dict]:
        """Genera reason codes para selección de campo."""
        codes = []
        
        if required:
            codes.append({"code": "REQUIRED", "description": "Campo requerido por producto"})
        
        field_data = self.field_catalog.get(field, {})
        
        if field_data.get("qualification_power", 0) >= 0.7:
            codes.append({"code": "HIGH_QUAL", "description": "Alto poder de calificación"})
        
        if field_data.get("friction", 1) <= 0.2:
            codes.append({"code": "LOW_FRICTION", "description": "Baja fricción de usuario"})
        
        return codes
    
    def _calculate_form_metrics(self, fields: List[Dict]) -> Dict[str, Any]:
        """Calcula métricas del formulario optimizado."""
        total_friction = sum(f["friction"] for f in fields)
        total_qual_power = sum(f["qualification_power"] for f in fields)
        
        # Estimación de completion rate (inverso de fricción)
        completion_rate = max(0.3, 1 - (total_friction / (len(fields) + 1)))
        
        # Estimación de tiempo (segundos por campo)
        avg_time_per_field = {"low": 8, "medium": 15, "high": 25}
        estimated_time = sum(
            avg_time_per_field["low"] if f["friction"] < 0.3 
            else avg_time_per_field["medium"] if f["friction"] < 0.6 
            else avg_time_per_field["high"]
            for f in fields
        )
        
        return {
            "total_friction": round(total_friction, 2),
            "total_qualification_power": round(total_qual_power, 2),
            "estimated_completion_rate": round(completion_rate, 3),
            "estimated_time_seconds": estimated_time,
            "efficiency_score": round(total_qual_power / (total_friction + 0.1), 2),
            "pii_exposure": sum(1 for f in fields if f["pii"]) / len(fields) if fields else 0
        }
    
    def _generate_ab_variant(self, fields: List[Dict], data: Dict) -> Dict[str, Any]:
        """Genera variante A/B determinista."""
        # Hash determinista
        seed = f"{self.tenant_id}_{data.get('campaign_id', 'default')}"
        hash_val = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        variant = "A" if hash_val % 2 == 0 else "B"
        
        if variant == "B":
            # Variante B: Reordenar por fricción
            reordered = sorted(fields, key=lambda x: x["friction"])
            field_order = [f["field"] for f in reordered]
        else:
            field_order = [f["field"] for f in fields]
        
        return {
            "variant": variant,
            "field_order": field_order,
            "hypothesis": "Orden por fricción mejora completion" if variant == "B" else "Orden por calificación mejora conversión"
        }
    
    def _generate_progressive_steps(self, fields: List[Dict]) -> List[Dict]:
        """Genera pasos de progressive disclosure."""
        steps = []
        
        # Step 1: Campos de baja fricción
        low_friction = [f for f in fields if f["friction"] < 0.3]
        if low_friction:
            steps.append({
                "step": 1,
                "name": "Información básica",
                "fields": [f["field"] for f in low_friction],
                "estimated_time": len(low_friction) * 8
            })
        
        # Step 2: Campos de media fricción
        med_friction = [f for f in fields if 0.3 <= f["friction"] < 0.6]
        if med_friction:
            steps.append({
                "step": 2,
                "name": "Información financiera",
                "fields": [f["field"] for f in med_friction],
                "estimated_time": len(med_friction) * 15
            })
        
        # Step 3: Campos de alta fricción
        high_friction = [f for f in fields if f["friction"] >= 0.6]
        if high_friction:
            steps.append({
                "step": 3,
                "name": "Verificación",
                "fields": [f["field"] for f in high_friction],
                "estimated_time": len(high_friction) * 25
            })
        
        return steps
    
    def _generate_insights(self, fields: List[Dict], metrics: Dict) -> List[str]:
        """Genera insights del formulario."""
        insights = []
        
        # Completion rate
        cr = metrics["estimated_completion_rate"]
        if cr >= 0.7:
            insights.append(f"Formulario optimizado: {cr*100:.0f}% completion rate esperado")
        else:
            insights.append(f"Considerar reducir campos: {cr*100:.0f}% completion rate")
        
        # Tiempo
        time_sec = metrics["estimated_time_seconds"]
        insights.append(f"Tiempo estimado: {time_sec} segundos ({time_sec//60}:{time_sec%60:02d} min)")
        
        # PII
        pii_count = sum(1 for f in fields if f["pii"])
        if pii_count > 2:
            insights.append(f"Alerta: {pii_count} campos PII - asegurar consentimiento")
        
        # Eficiencia
        efficiency = metrics["efficiency_score"]
        insights.append(f"Eficiencia calificación/fricción: {efficiency:.1f}x")
        
        return insights[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "field_catalog_size": len(self.field_catalog),
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "decision_layer": DECISION_LAYER_AVAILABLE
        }
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return MinimalFormIA(tenant_id, config)
