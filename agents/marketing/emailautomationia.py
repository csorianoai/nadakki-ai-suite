# agents/email_personalizer.py
"""
EmailPersonalizerIA - Production-Ready (v2.1.0)

Mejoras clave:
- Determinístico (sin random, hashing estable).
- Timezone-aware (IANA) + cooldown + DND correcto (maneja medianoche).
- Multi-tenant configurable (templates/constraints/timing por tenant).
- Validaciones de entrada y trazabilidad (decision_trace).
- Gate de consentimiento (suppression) y chequeo básico de compliance.
- A/B seeding por (tenant|lead|campaign) para experimentos por campaña.
- Bloques de contenido con footer + unsubscribe/contact placeholders.
- Métricas estimadas para orquestación (open_rate_p50/p90, ctr_p50).

Compatibilidad: Python 3.12+ (zoneinfo en stdlib).
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from zoneinfo import ZoneInfo

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailPersonalizerIA:
    """Agente de personalización de emails (determinístico y compliance-aware)."""

    VERSION = "v2.1.0"

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Args:
            tenant_id: ID del tenant (p.ej., "tn_bank001")
            config: Configuración opcional por tenant
        """
        self.tenant_id = tenant_id
        self.name = "EmailPersonalizerIA"
        self.config = config or self._default_config()
        self.templates = self.config.get("templates", self._default_templates())
        self.optimal_timing = self.config.get("timing", self._default_timing())
        logger.info("EmailPersonalizerIA inicializado (tenant=%s, version=%s)", tenant_id, self.VERSION)

    # -------------------------------------------------------------------------
    # Defaults
    # -------------------------------------------------------------------------
    def _default_config(self) -> Dict[str, Any]:
        return {
            "templates": self._default_templates(),
            "timing": self._default_timing(),
            "constraints": {
                "avoid_terms": ["garantizado", "sin riesgo", "pre-aprobado"],
                "max_subject_length": 60,
                "cooldown_hours": 48,
                # Ventana DND cruza medianoche (21:00–08:00)
                "dnd_window": {"start": "21:00", "end": "08:00"},
            },
        }

    def _default_templates(self) -> Dict[str, Any]:
        return {
            "high_value": {
                "subjects": [
                    "Oferta exclusiva para ti, {name}",
                    "{name}, tu pre-calificación está lista",
                    "Beneficios premium esperándote",
                ],
                "tone": "premium",
                "cta": "Ver mi oferta exclusiva",
                "template_id": "tmpl_high_value_01",
            },
            "mid_value": {
                "subjects": [
                    "Hola {name}, tenemos algo para ti",
                    "Tu solicitud puede ser aprobada hoy",
                    "Revisa esta oferta especial",
                ],
                "tone": "friendly",
                "cta": "Ver oferta",
                "template_id": "tmpl_mid_value_01",
            },
            "low_value": {
                "subjects": [
                    "Información sobre tu solicitud",
                    "Próximos pasos",
                    "Actualización importante",
                ],
                "tone": "professional",
                "cta": "Más información",
                "template_id": "tmpl_low_value_01",
            },
        }

    def _default_timing(self) -> Dict[str, Any]:
        return {
            "young_professional": {"hour": 19, "day": "weekday"},
            "business_owner": {"hour": 9, "day": "weekday"},
            "retired": {"hour": 10, "day": "any"},
            "default": {"hour": 14, "day": "weekday"},
        }

    # -------------------------------------------------------------------------
    # Helpers (determinismo, sanitización, validaciones)
    # -------------------------------------------------------------------------
    def _deterministic_choice(self, options: List[str], seed: str) -> str:
        h = hashlib.sha256(seed.encode()).hexdigest()
        idx = int(h[:8], 16) % len(options)
        return options[idx]

    def _get_ab_variant(self, tenant_id: str, lead_id: str, campaign_id: Optional[str]) -> str:
        seed = f"{tenant_id}|{lead_id}|{campaign_id or 'no-campaign'}|ab"
        h = hashlib.sha256(seed.encode()).hexdigest()
        return "A" if int(h[:8], 16) % 2 == 0 else "B"

    def _sanitize_subject(self, subject: str, avoid_terms: List[str]) -> str:
        # Normaliza múltiples signos de exclamación
        s = re.sub(r"!{2,}", "!", subject)
        # Bloqueo de términos con límites de palabra e insensitive
        for term in avoid_terms:
            s = re.sub(rf"\b{re.escape(term)}\b", "evaluación disponible", s, flags=re.IGNORECASE)

        # Limitar longitud
        max_len = int(self.config["constraints"]["max_subject_length"])
        return (s[: max_len - 3] + "...") if len(s) > max_len else s

    def _validate_input(self, data: Dict[str, Any]) -> Optional[str]:
        """Retorna mensaje de error si algo crítico falta/está mal."""
        if not isinstance(data, dict):
            return "invalid_input: payload_must_be_object"
        if not data.get("lead_id"):
            return "invalid_input: lead_id_required"
        if "name" in data and not isinstance(data["name"], str):
            return "invalid_input: name_must_be_string"
        if data.get("segment") and data["segment"] not in self.templates:
            return "invalid_input: unsupported_segment"
        if "timezone" in data:
            try:
                ZoneInfo(str(data["timezone"]))
            except Exception:
                return "invalid_input: invalid_timezone"
        return None

    # -------------------------------------------------------------------------
    # Time (DND, cooldown, TZ)
    # -------------------------------------------------------------------------
    @staticmethod
    def _parse_hhmm(s: str) -> tuple[int, int]:
        hh, mm = s.split(":")
        return int(hh), int(mm)

    @staticmethod
    def _in_dnd(dt: datetime, start_h: int, start_m: int, end_h: int, end_m: int) -> bool:
        start = dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end = dt.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
        if start <= end:
            # Ventana NO cruza medianoche
            return start <= dt < end
        # Ventana cruza medianoche (ej. 21:00–08:00)
        return dt >= start or dt < end

    def _calculate_send_time(
        self,
        timing: Dict[str, Any],
        timezone: str = "UTC",
        last_contact: Optional[datetime] = None,
    ) -> datetime:
        try:
            tz = ZoneInfo(timezone)
        except Exception as e:
            logger.warning("Timezone inválido '%s', usando UTC. Error: %s", timezone, e)
            tz = ZoneInfo("UTC")

        now = datetime.now(tz)
        candidate = now.replace(hour=int(timing["hour"]), minute=0, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)

        dnd = self.config["constraints"]["dnd_window"]
        sh, sm = self._parse_hhmm(dnd["start"])
        eh, em = self._parse_hhmm(dnd["end"])

        # Empuja fuera de DND de manera segura
        guard = 0
        while self._in_dnd(candidate, sh, sm, eh, em):
            candidate += timedelta(hours=1)
            guard += 1
            if guard > 48:  # evita loops (máx. 2 días de avance)
                break

        # Cooldown desde último contacto
        if last_contact:
            cooldown_hours = int(self.config["constraints"]["cooldown_hours"])
            min_next = last_contact.astimezone(tz) + timedelta(hours=cooldown_hours)
            if candidate < min_next:
                candidate = min_next

        return candidate

    # -------------------------------------------------------------------------
    # Scoring & métricas
    # -------------------------------------------------------------------------
    @staticmethod
    def _calculate_personalization_score(
        has_name: bool, has_offer: bool, has_context: bool, segment_matched: bool
    ) -> float:
        score = 0.0
        if has_name:
            score += 0.30
        if has_offer:
            score += 0.30
        if has_context:
            score += 0.20
        if segment_matched:
            score += 0.20
        return min(score, 1.0)

    @staticmethod
    def _estimate_open_rate(personalization_score: float, previous_emails: int) -> float:
        base_rate = 0.22
        boost = min(personalization_score * 0.15, 0.15)
        fatigue = min(previous_emails * 0.02, 0.10)
        return round(max(base_rate + boost - fatigue, 0.05), 3)

    @staticmethod
    def _estimate_metrics(personalization_score: float, previous_emails: int, segment: str) -> Dict[str, float]:
        base_map = {"high_value": 0.26, "mid_value": 0.22, "low_value": 0.18}
        base = base_map.get(segment, 0.22)
        boost = min(personalization_score * 0.15, 0.15)
        fatigue = min(previous_emails * 0.02, 0.10)
        open_p50 = max(base + boost - fatigue, 0.05)
        open_p90 = min(open_p50 + 0.07, 0.60)
        ctr_p50 = open_p50 * 0.16  # ratio heurístico
        return {
            "open_rate_p50": round(open_p50, 3),
            "open_rate_p90": round(open_p90, 3),
            "ctr_p50": round(ctr_p50, 3),
        }

    # -------------------------------------------------------------------------
    # Render helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _generate_preview(segment: str, context: Dict[str, Any]) -> str:
        product = context.get("product", "producto")
        amount = context.get("offer_amount", 0)
        if segment == "high_value" and amount:
            return f"Hasta ${amount:,.0f} según evaluación"
        if segment == "mid_value":
            return f"Tu solicitud de {product} puede ser aprobada hoy"
        return "Información importante sobre tu solicitud"

    @staticmethod
    def _generate_content_blocks(segment: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = [
            {"type": "hero", "content": "Tu oferta personalizada está lista", "order": 0}
        ]
        if context.get("offer_amount"):
            blocks.append(
                {
                    "type": "offer",
                    "amount": context["offer_amount"],
                    "product": context.get("product", "producto"),
                    "order": 1,
                }
            )
        blocks.append(
            {
                "type": "benefits",
                "items": ["Decisión en 24 horas", "Sin costos ocultos", "Atención personalizada"],
                "order": 2,
            }
        )
        blocks.append(
            {
                "type": "disclaimer",
                "content": "Sujeto a aprobación crediticia. Términos y condiciones aplican.",
                "order": 3,
            }
        )
        blocks.append({"type": "cta", "text": "Ver oferta completa", "order": 4})
        # Footer obligatorio (compliance-ready)
        blocks.append(
            {
                "type": "footer",
                "unsubscribe_link": "{{unsubscribe_link}}",
                "contact_link": "{{contact_link}}",
                "order": 5,
            }
        )
        return blocks

    def _compliance_check(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Chequeo muy ligero de compliance (placeholder robusto para hardening posterior)."""
        txt_parts = [draft.get("subject_line", ""), draft.get("preview_text", "")]
        for b in draft.get("content_blocks", []):
            txt_parts.append(str(b.get("content") or b.get("text") or ""))
        txt = " ".join(txt_parts)

        violations: List[str] = []
        for t in self.config["constraints"]["avoid_terms"]:
            if re.search(rf"\b{re.escape(t)}\b", txt, flags=re.IGNORECASE):
                violations.append(f"blocked_term:{t}")

        # Asegurar que existe disclaimer (ya se añade por defecto, pero reforzamos)
        has_disclaimer = any(b.get("type") == "disclaimer" for b in draft.get("content_blocks", []))
        if not has_disclaimer:
            draft.setdefault("content_blocks", []).append(
                {
                    "type": "disclaimer",
                    "content": "Sujeto a aprobación crediticia. Términos y condiciones aplican.",
                    "order": 3,
                }
            )

        status = "fail" if violations else "pass"
        return {"status": status, "blocked_reasons": violations}

    # -------------------------------------------------------------------------
    # Execute
    # -------------------------------------------------------------------------
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input esperado:
        {
          "lead_id": str,
          "name": str,
          "segment": "high_value|mid_value|low_value",
          "persona": "young_professional|business_owner|retired|default",
          "timezone": "America/Mexico_City",
          "campaign_id": str (opcional),
          "context": {"product": str, "offer_amount": float, "approval_probability": float},
          "previous_emails": int,
          "last_contact_at": ISO 8601 | None,
          "consent_opt_in": bool (default=True)
        }
        """
        t0 = time.perf_counter()
        decision_trace: List[str] = []

        # Validación
        err = self._validate_input(data)
        if err:
            latency = int((time.perf_counter() - t0) * 1000)
            return {
                "tenant_id": self.tenant_id,
                "status": "error",
                "error": err,
                "latency_ms": latency,
                "version": self.VERSION,
            }

        # Gate de consentimiento
        lead_id = str(data.get("lead_id"))
        if not data.get("consent_opt_in", True):
            latency = int((time.perf_counter() - t0) * 1000)
            return {
                "tenant_id": self.tenant_id,
                "lead_id": lead_id,
                "status": "suppressed",
                "reason": "no_consent",
                "latency_ms": latency,
                "version": self.VERSION,
            }
        decision_trace.append("consent=ok")

        # Extracción segura de inputs
        name = data.get("name", "Cliente")
        segment = data.get("segment", "mid_value")
        persona = data.get("persona", "default")
        timezone = data.get("timezone", "UTC")
        campaign_id = data.get("campaign_id")
        context = data.get("context", {}) or {}
        previous_emails = int(data.get("previous_emails", 0))
        last_contact_str = data.get("last_contact_at")

        last_contact: Optional[datetime] = None
        if last_contact_str:
            try:
                # Soporta "Z"
                last_contact = datetime.fromisoformat(str(last_contact_str).replace("Z", "+00:00"))
            except Exception as e:
                logger.warning("Error parseando last_contact_at (%s): %s", last_contact_str, e)

        # Template por segmento
        template = self.templates.get(segment, self.templates["mid_value"])

        # Subject determinístico
        subject_options = template["subjects"]
        subj_seed = f"{self.tenant_id}|{lead_id}|{campaign_id or 'no-campaign'}|subject"
        subject_raw = self._deterministic_choice(subject_options, subj_seed).format(name=name)

        # Ajustes por contexto
        approval_prob = float(context.get("approval_probability", 0) or 0.0)
        if approval_prob > 0.8:
            subject_raw = f"¡Excelentes noticias, {name}!"
            decision_trace.append("subject=high_approval_override")
        elif previous_emails > 3:
            subject_raw = f"{name}, ¿aún interesado?"
            decision_trace.append("subject=fatigue_reengagement")

        subject_line = self._sanitize_subject(subject_raw, self.config["constraints"]["avoid_terms"])

        # Preview y contenido
        preview_text = self._generate_preview(segment, context)
        content_blocks = self._generate_content_blocks(segment, context)
        cta_text = template["cta"]

        # Timing óptimo
        timing_cfg = self.optimal_timing.get(persona, self.optimal_timing["default"])
        optimal_dt = self._calculate_send_time(timing_cfg, timezone, last_contact)

        # Personalización y variantes
        personalization_score = self._calculate_personalization_score(
            has_name=(name != "Cliente"),
            has_offer=bool(context.get("offer_amount")),
            has_context=bool(context),
            segment_matched=True,
        )
        ab_variant = self._get_ab_variant(self.tenant_id, lead_id, campaign_id)
        decision_trace.append(f"variant={ab_variant}")

        # Estimaciones
        estimated_open_rate = self._estimate_open_rate(personalization_score, previous_emails)
        estimated_metrics = self._estimate_metrics(personalization_score, previous_emails, segment)

        # Borrador de resultado
        result: Dict[str, Any] = {
            "tenant_id": self.tenant_id,
            "lead_id": lead_id,
            "campaign_id": campaign_id,
            "subject_line": subject_line,
            "preview_text": preview_text,
            "content_blocks": content_blocks,
            "cta_text": cta_text,
            "optimal_send_time": optimal_dt.isoformat(),
            "personalization_score": round(personalization_score, 3),
            "ab_variant": ab_variant,
            "tone": template["tone"],
            "estimated_open_rate": estimated_open_rate,
            "estimated_metrics": estimated_metrics,
            "template_id": template["template_id"],
            "version": self.VERSION,
        }

        # Compliance básico
        comp = self._compliance_check(result)
        result["compliance"] = comp
        result["status"] = "blocked" if comp["status"] == "fail" else "ready"
        decision_trace.append(f"compliance={comp['status']}")

        # Latencia
        latency_ms = int((time.perf_counter() - t0) * 1000)
        result["latency_ms"] = latency_ms
        result["decision_trace"] = decision_trace

        logger.info(
            "Email personalizado (tenant=%s lead=%s campaign=%s) status=%s latency=%sms",
            self.tenant_id,
            lead_id,
            campaign_id,
            result["status"],
            latency_ms,
        )
        return result

    # -------------------------------------------------------------------------
    # Métricas del agente
    # -------------------------------------------------------------------------
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_name": self.name,
            "agent_version": self.VERSION,
            "tenant_id": self.tenant_id,
            "templates_available": sum(len(t["subjects"]) for t in self.templates.values()),
            "status": "healthy",
        }


# =============================================================================
# Helpers de testing manual
# =============================================================================
def create_test_lead() -> Dict[str, Any]:
    return {
        "lead_id": "L-TEST001",
        "name": "María González",
        "segment": "high_value",
        "persona": "young_professional",
        "timezone": "America/Mexico_City",
        "campaign_id": "cmp_demo_001",
        "context": {"product": "crédito personal", "offer_amount": 50000, "approval_probability": 0.85},
        "previous_emails": 1,
        "last_contact_at": "2025-10-01T10:00:00Z",
        "consent_opt_in": True,
    }


# =============================================================================
# Main de prueba
# =============================================================================
async def main() -> None:
    print("=" * 80)
    print("EMAIL PERSONALIZER IA - TEST")
    print("=" * 80)

    agent = EmailPersonalizerIA(tenant_id="tn_bank001")
    lead = create_test_lead()

    print(f"\nPersonalizando email para: {lead['name']} (segment={lead['segment']}, tz={lead['timezone']})")
    result = await agent.execute(lead)

    print("\nRESULTADO:")
    for k in [
        "status",
        "subject_line",
        "preview_text",
        "cta_text",
        "optimal_send_time",
        "personalization_score",
        "ab_variant",
        "estimated_open_rate",
        "estimated_metrics",
        "template_id",
        "version",
        "latency_ms",
    ]:
        print(f" - {k}: {result.get(k)}")

    print("\nContent Blocks:")
    for b in result.get("content_blocks", []):
        kind = b.get("type")
        detail = b.get("content") or b.get("text") or b.get("items")
        print(f"   • {kind}: {detail}")

    print("\nDecision Trace:", result.get("decision_trace"))
    print("=" * 80)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
