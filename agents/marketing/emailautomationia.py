# agents/marketing/emailautomationia.py
"""
EmailAutomationIA v3.0.0 - SUPER AGENT
Automatización de Email con Personalización y Timing Óptimo
"""

from __future__ import annotations
import time
import logging
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from agents.marketing.layers.decision_layer import apply_decision_layer
    DECISION_LAYER_AVAILABLE = True
except ImportError:
    DECISION_LAYER_AVAILABLE = False


class EmailAutomationIA:
    VERSION = "3.0.0"
    AGENT_ID = "emailautomationia"
    
    def __init__(self, tenant_id: str, config: Optional[Dict] = None):
        self.tenant_id = tenant_id
        self.config = config or {}
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0, "emails_scheduled": 0}
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Carga templates de email."""
        return {
            "welcome": {"subject": "Bienvenido a {company}", "open_rate": 0.45, "ctr": 0.12},
            "onboarding_1": {"subject": "Primeros pasos con tu cuenta", "open_rate": 0.38, "ctr": 0.08},
            "onboarding_2": {"subject": "Descubre todas las funciones", "open_rate": 0.32, "ctr": 0.06},
            "promotion": {"subject": "Oferta especial para ti", "open_rate": 0.25, "ctr": 0.04},
            "reactivation": {"subject": "Te extrañamos", "open_rate": 0.22, "ctr": 0.05},
            "nurture": {"subject": "Contenido que te puede interesar", "open_rate": 0.28, "ctr": 0.03},
            "upsell": {"subject": "Mejora tu experiencia", "open_rate": 0.30, "ctr": 0.07}
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera automatización de email personalizada."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            data = input_data.get("input_data", input_data) if isinstance(input_data, dict) else {}
            
            lead_id = data.get("lead_id", "lead_001")
            lead_data = data.get("lead", {})
            campaign_type = data.get("campaign_type", "nurture")
            
            # Seleccionar template
            template = self._select_template(campaign_type, lead_data)
            
            # Personalizar contenido
            personalization = self._personalize_content(template, lead_data)
            
            # Calcular timing óptimo
            timing = self._calculate_optimal_timing(lead_data)
            
            # Verificar compliance
            compliance = self._check_compliance(lead_data)
            
            # Generar secuencia
            sequence = self._generate_sequence(campaign_type, template)
            
            # Estimar métricas
            estimated_metrics = self._estimate_metrics(template, personalization)
            
            # Insights
            insights = self._generate_insights(template, timing, compliance)
            
            self.metrics["emails_scheduled"] += len(sequence)
            
            decision_trace = [
                f"lead_id={lead_id}",
                f"campaign={campaign_type}",
                f"template={template['id']}",
                f"emails_in_sequence={len(sequence)}"
            ]
            
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            result = {
                "automation_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tenant_id": self.tenant_id,
                "lead_id": lead_id,
                "campaign_type": campaign_type,
                "selected_template": template,
                "personalization": personalization,
                "optimal_timing": timing,
                "sequence": sequence,
                "estimated_metrics": estimated_metrics,
                "compliance": compliance,
                "summary": {
                    "emails_scheduled": len(sequence),
                    "expected_open_rate": estimated_metrics["expected_open_rate"],
                    "expected_ctr": estimated_metrics["expected_ctr"],
                    "send_window": timing["recommended_window"]
                },
                "key_insights": insights,
                "decision_trace": decision_trace,
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
                "automation_id": "error",
                "tenant_id": self.tenant_id,
                "sequence": [],
                "key_insights": [f"Error: {str(e)[:100]}"],
                "decision_trace": ["error_occurred"],
                "version": self.VERSION,
                "latency_ms": latency_ms
            }
    
    def _select_template(self, campaign_type: str, lead_data: Dict) -> Dict[str, Any]:
        """Selecciona template óptimo."""
        # Mapeo de campaña a templates
        campaign_templates = {
            "welcome": ["welcome"],
            "onboarding": ["onboarding_1", "onboarding_2"],
            "nurture": ["nurture"],
            "promotion": ["promotion"],
            "reactivation": ["reactivation"],
            "upsell": ["upsell"]
        }
        
        templates = campaign_templates.get(campaign_type, ["nurture"])
        template_id = templates[0]
        template_data = self.templates.get(template_id, self.templates["nurture"])
        
        return {
            "id": template_id,
            "subject": template_data["subject"],
            "base_open_rate": template_data["open_rate"],
            "base_ctr": template_data["ctr"],
            "reason_codes": [{"code": "TEMPLATE_MATCH", "description": f"Template óptimo para {campaign_type}"}]
        }
    
    def _personalize_content(self, template: Dict, lead_data: Dict) -> Dict[str, Any]:
        """Personaliza contenido del email."""
        name = lead_data.get("name", lead_data.get("first_name", "Cliente"))
        company = lead_data.get("company", "Nuestra empresa")
        
        # Variables de personalización
        variables = {
            "name": name,
            "company": company,
            "product_interest": lead_data.get("product_interest", "nuestros productos"),
            "last_activity": lead_data.get("last_activity", "tu última visita")
        }
        
        # Personalizar subject
        subject = template["subject"].format(**{"company": company})
        
        # Calcular boost por personalización
        personalization_boost = 0.0
        if name != "Cliente":
            personalization_boost += 0.15
        if lead_data.get("product_interest"):
            personalization_boost += 0.10
        
        return {
            "variables": variables,
            "personalized_subject": subject,
            "personalization_level": "high" if personalization_boost > 0.2 else "medium" if personalization_boost > 0.1 else "low",
            "expected_boost": round(personalization_boost, 2),
            "dynamic_content_blocks": ["header", "body", "cta", "footer"]
        }
    
    def _calculate_optimal_timing(self, lead_data: Dict) -> Dict[str, Any]:
        """Calcula timing óptimo de envío."""
        # Timezone del lead
        timezone = lead_data.get("timezone", "America/New_York")
        
        # Horas óptimas por tipo de lead
        engagement_history = lead_data.get("engagement_hours", [10, 14, 20])
        
        # Determinar mejor hora
        best_hour = max(set(engagement_history), key=engagement_history.count) if engagement_history else 10
        
        # Días óptimos
        best_days = ["Tuesday", "Wednesday", "Thursday"]
        
        # Cooldown desde último email
        last_email = lead_data.get("last_email_date")
        cooldown_met = True
        if last_email:
            try:
                last = datetime.fromisoformat(last_email)
                cooldown_met = (datetime.now() - last).days >= 3
            except:
                pass
        
        return {
            "timezone": timezone,
            "best_hour": best_hour,
            "best_days": best_days,
            "recommended_window": f"{best_hour}:00-{best_hour+2}:00 {timezone}",
            "cooldown_met": cooldown_met,
            "do_not_disturb": self._check_dnd(best_hour),
            "reason_codes": [
                {"code": "TIMING_OPT", "description": f"Hora óptima basada en engagement histórico"}
            ]
        }
    
    def _check_dnd(self, hour: int) -> bool:
        """Verifica si está en horario DND."""
        return hour < 8 or hour > 21
    
    def _check_compliance(self, lead_data: Dict) -> Dict[str, Any]:
        """Verifica compliance de email."""
        has_consent = lead_data.get("email_consent", True)
        is_suppressed = lead_data.get("suppressed", False)
        has_unsubscribed = lead_data.get("unsubscribed", False)
        
        can_send = has_consent and not is_suppressed and not has_unsubscribed
        
        issues = []
        if not has_consent:
            issues.append("No consent on file")
        if is_suppressed:
            issues.append("Lead is suppressed")
        if has_unsubscribed:
            issues.append("Lead has unsubscribed")
        
        return {
            "can_send": can_send,
            "has_consent": has_consent,
            "is_suppressed": is_suppressed,
            "has_unsubscribed": has_unsubscribed,
            "issues": issues,
            "gdpr_compliant": has_consent,
            "can_spam_compliant": not has_unsubscribed
        }
    
    def _generate_sequence(self, campaign_type: str, template: Dict) -> List[Dict]:
        """Genera secuencia de emails."""
        sequences = {
            "welcome": [
                {"day": 0, "template": "welcome", "subject": "Bienvenido"},
                {"day": 2, "template": "onboarding_1", "subject": "Primeros pasos"},
                {"day": 5, "template": "onboarding_2", "subject": "Descubre más"}
            ],
            "nurture": [
                {"day": 0, "template": "nurture", "subject": "Contenido para ti"},
                {"day": 7, "template": "nurture", "subject": "Más contenido"},
                {"day": 14, "template": "promotion", "subject": "Oferta especial"}
            ],
            "reactivation": [
                {"day": 0, "template": "reactivation", "subject": "Te extrañamos"},
                {"day": 3, "template": "promotion", "subject": "Oferta de regreso"},
                {"day": 7, "template": "reactivation", "subject": "Última oportunidad"}
            ]
        }
        
        base_sequence = sequences.get(campaign_type, sequences["nurture"])
        
        return [
            {
                "step": i + 1,
                "day_offset": s["day"],
                "template_id": s["template"],
                "subject_preview": s["subject"],
                "expected_open_rate": self.templates.get(s["template"], {}).get("open_rate", 0.25),
                "status": "scheduled"
            }
            for i, s in enumerate(base_sequence)
        ]
    
    def _estimate_metrics(self, template: Dict, personalization: Dict) -> Dict[str, Any]:
        """Estima métricas del email."""
        base_open = template["base_open_rate"]
        base_ctr = template["base_ctr"]
        boost = personalization["expected_boost"]
        
        expected_open = min(0.60, base_open * (1 + boost))
        expected_ctr = min(0.15, base_ctr * (1 + boost * 0.5))
        
        return {
            "expected_open_rate": round(expected_open, 3),
            "expected_ctr": round(expected_ctr, 3),
            "expected_conversion_rate": round(expected_ctr * 0.2, 4),
            "confidence_interval": "±15%",
            "benchmark_comparison": {
                "vs_industry_open": f"+{(expected_open - 0.20) * 100:.0f}pp" if expected_open > 0.20 else f"{(expected_open - 0.20) * 100:.0f}pp",
                "vs_industry_ctr": f"+{(expected_ctr - 0.025) * 100:.1f}pp" if expected_ctr > 0.025 else f"{(expected_ctr - 0.025) * 100:.1f}pp"
            }
        }
    
    def _generate_insights(self, template: Dict, timing: Dict, compliance: Dict) -> List[str]:
        """Genera insights de la automatización."""
        insights = []
        
        # Template
        insights.append(f"Template seleccionado: {template['id']} (open rate base {template['base_open_rate']*100:.0f}%)")
        
        # Timing
        insights.append(f"Mejor horario: {timing['recommended_window']}")
        
        # Compliance
        if compliance["can_send"]:
            insights.append("Compliance verificado: OK para enviar")
        else:
            insights.append(f"Alerta compliance: {', '.join(compliance['issues'])}")
        
        # Cooldown
        if not timing["cooldown_met"]:
            insights.append("Cooldown no cumplido: Esperar antes de enviar")
        
        return insights[:5]
    
    def health(self) -> Dict[str, Any]:
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "templates_available": len(self.templates),
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "emails_scheduled": self.metrics["emails_scheduled"],
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "decision_layer": DECISION_LAYER_AVAILABLE
        }
    
    def health_check(self) -> Dict[str, Any]:
        return self.health()


def create_agent_instance(tenant_id: str, config: Dict = None):
    return EmailAutomationIA(tenant_id, config)
