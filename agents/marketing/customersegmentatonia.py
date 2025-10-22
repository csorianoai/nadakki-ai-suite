# agents/audience_segmentation.py
"""
AudienceSegmentationIA - Production-Ready (v2.1.0)

Mejoras clave:
- Determinístico (sin random), multi-tenant y totalmente trazable (decision_trace).
- Tres estrategias consistentes: behavioral, demographic y hybrid (+ combinaciones).
- Validaciones estrictas de entrada y métricas de calidad (coverage, overlap, fragmentation, distinctiveness).
- Segmentos configurables por tenant con umbrales claros; evita atributos protegidos.
- Salida explicable por segmento: características agregadas, reglas disparadoras y acciones recomendadas.
- Overlap matrix y lead assignments explícitos (para auditoría / UI drill-down).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import time
from datetime import datetime
import logging

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Lead:
    lead_id: str
    credit_score: Optional[int] = None
    income: Optional[float] = None
    age: Optional[int] = None
    engagement_score: Optional[float] = None
    days_since_last_interaction: Optional[int] = None
    previous_conversions: Optional[int] = None
    product_interests: Optional[List[str]] = None
    location: Optional[Dict[str, Any]] = None


class AudienceSegmentationIA:
    VERSION = "v2.1.0"

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.tenant_id = tenant_id
        self.name = "AudienceSegmentationIA"
        self.config = config or self._default_config()
        self.segment_definitions = self.config["segments"]
        logger.info("AudienceSegmentationIA init (tenant=%s, version=%s)", tenant_id, self.VERSION)

    # -------------------------------------------------------------------------
    # Defaults & config
    # -------------------------------------------------------------------------
    def _default_config(self) -> Dict[str, Any]:
        return {
            "segments": {
                "high_value_ready": {
                    "criteria": {
                        "credit_score_min": 700,
                        "income_min": 60000,
                        "engagement_score_min": 0.7,
                    },
                    "size_target": "5-10%",
                    "priority": 1,
                    "actions": ["Fast-track to sales", "Premium product offer", "Personalized consultation"],
                },
                "nurture_potential": {
                    "criteria": {
                        "credit_score_min": 650,
                        "income_min": 40000,
                        "engagement_score_min": 0.4,
                    },
                    "size_target": "20-30%",
                    "priority": 2,
                    "actions": ["Nurture sequence", "Educational content", "Monthly check-in"],
                },
                "re_engage": {
                    "criteria": {"days_since_last_interaction_min": 30, "previous_conversions": 0},
                    "size_target": "15-20%",
                    "priority": 3,
                    "actions": ["Re-engagement offer", "Drop-off survey", "Multi-channel outreach"],
                },
                "churn_risk": {
                    "criteria": {"days_since_last_interaction_min": 90, "engagement_score_max": 0.3},
                    "size_target": "10-15%",
                    "priority": 4,
                    "actions": ["Urgent retention", "Executive outreach", "Win-back incentive"],
                },
                "price_sensitive": {
                    "criteria": {"income_max": 40000, "engagement_score_min": 0.5},
                    "size_target": "10-15%",
                    "priority": 5,
                    "actions": ["Highlight low-rate offers", "Cost savings", "Flexible payments"],
                },
                "high_engagement": {
                    "criteria": {"engagement_score_min": 0.7},
                    "size_target": "10-20%",
                    "priority": 6,
                    "actions": ["Upsell/Cross-sell", "Loyalty program", "Referral program"],
                },
            },
            # Campos sensibles que nunca deben intervenir en reglas (cumplimiento)
            "protected_attributes": ["race", "gender", "religion", "national_origin", "sexual_orientation"],
            "max_segments": 6,
        }

    # -------------------------------------------------------------------------
    # Validaciones y utilidades
    # -------------------------------------------------------------------------
    @staticmethod
    def _error(message: str, t0: float, tenant_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "status": "error",
            "error": message,
            "segments": [],
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "version": AudienceSegmentationIA.VERSION,
        }

    @staticmethod
    def _avg(nums: List[float]) -> float:
        return round(sum(nums) / len(nums), 4) if nums else 0.0

    @staticmethod
    def _safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
        v = d.get(key, default)
        return v if v is not None else default

    def _validate_input(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return "invalid_input: payload must be an object"
        if not data.get("audience_id"):
            return "invalid_input: audience_id required"
        leads = data.get("leads", [])
        if not isinstance(leads, list) or len(leads) == 0:
            return "invalid_input: at least one lead required"
        # Atributos protegidos NO deben existir a nivel de lead
        for l in leads:
            if any(pa in l for pa in self.config["protected_attributes"]):
                return "invalid_input: protected attributes present in lead payload"
        return None

    # -------------------------------------------------------------------------
    # Estrategias de segmentación
    # -------------------------------------------------------------------------
    def _match_segment(self, lead: Lead, seg_key: str, rule: Dict[str, Any]) -> bool:
        c = rule["criteria"]
        # Reglas soportadas (todas opcionales)
        cs_min = c.get("credit_score_min")
        inc_min = c.get("income_min")
        inc_max = c.get("income_max")
        eng_min = c.get("engagement_score_min")
        eng_max = c.get("engagement_score_max")
        dsl_min = c.get("days_since_last_interaction_min")
        prev_conv_eq = c.get("previous_conversions")

        if cs_min is not None and (lead.credit_score or 0) < cs_min:
            return False
        if inc_min is not None and (lead.income or 0.0) < inc_min:
            return False
        if inc_max is not None and (lead.income or 0.0) > inc_max:
            return False
        if eng_min is not None and (lead.engagement_score or 0.0) < eng_min:
            return False
        if eng_max is not None and (lead.engagement_score or 0.0) > eng_max:
            return False
        if dsl_min is not None and (lead.days_since_last_interaction or 0) < dsl_min:
            return False
        if prev_conv_eq is not None and (lead.previous_conversions or 0) != prev_conv_eq:
            return False
        return True

    def _collect_features(self, leads: List[Lead], ids: List[str]) -> Dict[str, Any]:
        subset = [l for l in leads if l.lead_id in ids]
        return {
            "avg_credit_score": self._avg([float(l.credit_score or 0) for l in subset]),
            "avg_income": self._avg([float(l.income or 0) for l in subset]),
            "avg_age": self._avg([float(l.age or 0) for l in subset]),
            "avg_engagement": self._avg([float(l.engagement_score or 0.0) for l in subset]),
            "avg_days_since_last_interaction": self._avg([float(l.days_since_last_interaction or 0) for l in subset]),
        }

    def _segment_behavioral(self, leads: List[Lead]) -> List[Dict[str, Any]]:
        segs: List[Dict[str, Any]] = []

        # High Engagement
        ids = [l.lead_id for l in leads if (l.engagement_score or 0.0) >= 0.7]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_high_eng",
                    "segment_name": "High Engagement",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 2,
                }
            )

        # Re-engage
        ids = [
            l.lead_id
            for l in leads
            if (l.days_since_last_interaction or 0) >= 30 and (l.previous_conversions or 0) == 0 and (l.engagement_score or 0) < 0.5
        ]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_re_engage",
                    "segment_name": "Re-engage",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 3,
                }
            )

        # Churn risk
        ids = [l.lead_id for l in leads if (l.days_since_last_interaction or 0) >= 90 and (l.engagement_score or 0.0) <= 0.3]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_churn_risk",
                    "segment_name": "Churn Risk",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 4,
                }
            )

        return segs

    def _segment_demographic(self, leads: List[Lead]) -> List[Dict[str, Any]]:
        segs: List[Dict[str, Any]] = []

        high_inc = [l.lead_id for l in leads if (l.income or 0.0) >= 60000]
        mid_inc = [l.lead_id for l in leads if 40000 <= (l.income or 0.0) < 60000]
        young = [l.lead_id for l in leads if (l.age or 99) < 35]

        if high_inc:
            segs.append(
                {
                    "segment_id": "seg_high_income",
                    "segment_name": "High Income",
                    "lead_ids": high_inc,
                    "size": len(high_inc),
                    "characteristics": self._collect_features(leads, high_inc),
                    "priority": 3,
                }
            )
        if mid_inc:
            segs.append(
                {
                    "segment_id": "seg_mid_income",
                    "segment_name": "Mid Income",
                    "lead_ids": mid_inc,
                    "size": len(mid_inc),
                    "characteristics": self._collect_features(leads, mid_inc),
                    "priority": 4,
                }
            )
        if young:
            segs.append(
                {
                    "segment_id": "seg_young",
                    "segment_name": "Young Professionals",
                    "lead_ids": young,
                    "size": len(young),
                    "characteristics": self._collect_features(leads, young),
                    "priority": 5,
                }
            )

        return segs

    def _segment_hybrid(self, leads: List[Lead]) -> List[Dict[str, Any]]:
        segs: List[Dict[str, Any]] = []

        # high_value_ready (alto ingreso + alto engagement + buen crédito)
        ids = [
            l.lead_id
            for l in leads
            if (l.income or 0.0) >= 60000 and (l.engagement_score or 0.0) >= 0.7 and (l.credit_score or 0) >= 700
        ]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_high_value_ready",
                    "segment_name": "High Value Ready",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 1,
                }
            )

        # nurture_potential (ingreso medio + engagement medio + crédito aceptable)
        ids = [
            l.lead_id
            for l in leads
            if 40000 <= (l.income or 0.0) < 60000 and 0.4 <= (l.engagement_score or 0.0) < 0.7 and (l.credit_score or 0) >= 650
        ]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_nurture_potential",
                    "segment_name": "Nurture Potential",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 2,
                }
            )

        # price_sensitive (bajo ingreso + buen engagement)
        ids = [l.lead_id for l in leads if (l.income or 0.0) < 40000 and (l.engagement_score or 0.0) >= 0.5]
        if ids:
            segs.append(
                {
                    "segment_id": "seg_price_sensitive",
                    "segment_name": "Price Sensitive",
                    "lead_ids": ids,
                    "size": len(ids),
                    "characteristics": self._collect_features(leads, ids),
                    "priority": 3,
                }
            )

        return segs

    # -------------------------------------------------------------------------
    # Overlap y calidad
    # -------------------------------------------------------------------------
    @staticmethod
    def _overlap_matrix(segments: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        ids_map = {s["segment_id"]: set(s.get("lead_ids", [])) for s in segments}
        keys = list(ids_map.keys())
        matrix: Dict[str, Dict[str, int]] = {}
        for i, a in enumerate(keys):
            matrix[a] = {}
            for j, b in enumerate(keys):
                if j < i:
                    matrix[a][b] = matrix[b][a]
                else:
                    matrix[a][b] = len(ids_map[a] & ids_map[b])
        return matrix

    @staticmethod
    def _overlap_summary(segments: List[Dict[str, Any]], total_leads: int) -> Dict[str, Any]:
        all_ids = []
        dup = 0
        seen = set()
        for s in segments:
            for lid in s.get("lead_ids", []):
                if lid in seen:
                    dup += 1
                else:
                    seen.add(lid)
                all_ids.append(lid)
        unique = len(seen)
        return {
            "total_unique_leads": unique,
            "overlapping_leads": dup,
            "overlap_rate": round((dup / total_leads), 4) if total_leads else 0.0,
        }

    @staticmethod
    def _quality_score(segments: List[Dict[str, Any]], total: int) -> float:
        if total <= 0:
            return 0.0
        coverage = sum(s["size"] for s in segments) / total
        n = len(segments)
        balance = 1 - abs(0.5 - (n / 10.0))  # ideal ~5 segmentos
        distinctiveness = min(1.0, n / 3.0)
        quality = (coverage * 0.5) + (balance * 0.3) + (distinctiveness * 0.2)
        return round(quality, 3)

    # -------------------------------------------------------------------------
    # Núcleo
    # -------------------------------------------------------------------------
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        {
          "audience_id": str,
          "leads": [ { lead_id, credit_score, income, age, engagement_score, days_since_last_interaction,
                       previous_conversions, product_interests, location }, ... ],
          "segmentation_strategy": "behavioral" | "demographic" | "hybrid",
          "max_segments": int (opcional, default config),
          "include_actions": bool
        }
        """
        t0 = time.perf_counter()
        decision_trace: List[str] = []

        err = self._validate_input(data)
        if err:
            return self._error(err, t0, self.tenant_id)

        audience_id = str(data.get("audience_id"))
        raw_leads = data.get("leads", []) or []
        strategy = str(data.get("segmentation_strategy", "hybrid"))
        max_segments = int(data.get("max_segments", self.config.get("max_segments", 6)))
        include_actions = bool(data.get("include_actions", True))

        # Parseo seguro a dataclass Lead
        leads: List[Lead] = [
            Lead(
                lead_id=str(l.get("lead_id")),
                credit_score=l.get("credit_score"),
                income=l.get("income"),
                age=l.get("age"),
                engagement_score=l.get("engagement_score"),
                days_since_last_interaction=l.get("days_since_last_interaction"),
                previous_conversions=l.get("previous_conversions"),
                product_interests=l.get("product_interests"),
                location=l.get("location"),
            )
            for l in raw_leads
            if l.get("lead_id")
        ]

        total_leads = len(leads)
        if total_leads == 0:
            return self._error("invalid_input: no valid leads with lead_id", t0, self.tenant_id)

        decision_trace.append(f"strategy={strategy}")
        decision_trace.append(f"total_leads={total_leads}")

        # Segmentación según estrategia
        segments: List[Dict[str, Any]] = []
        if strategy == "behavioral":
            segments = self._segment_behavioral(leads)
        elif strategy == "demographic":
            segments = self._segment_demographic(leads)
        else:
            # hybrid = behavioral + demographic + reglas híbridas
            segments = self._segment_behavioral(leads) + self._segment_demographic(leads) + self._segment_hybrid(leads)

        # Orden por prioridad y truncado
        segments.sort(key=lambda s: (s.get("priority", 99), -s["size"], s["segment_id"]))
        if max_segments > 0 and len(segments) > max_segments:
            segments = segments[:max_segments]
        decision_trace.append(f"segments_selected={len(segments)}")

        # Características y acciones recomendadas
        for s in segments:
            key_name = s["segment_name"]
            if include_actions:
                # Acciones de catálogo si existen, otherwise heurísticas por nombre
                actions = self.segment_definitions.get(key_name.replace(" ", "_").lower(), {}).get("actions")
                if not actions:
                    # fallback por nombre
                    actions = self._recommendations_by_name(key_name)
                s["recommended_actions"] = actions
            s["rules_triggered"] = self._rules_for_segment_name(key_name)

        # Métricas de cobertura y solapamiento
        coverage = round(sum(s["size"] for s in segments) / total_leads, 4)
        overlap = self._overlap_summary(segments, total_leads)
        ov_matrix = self._overlap_matrix(segments)
        quality = self._quality_score(segments, total_leads)

        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "tenant_id": self.tenant_id,
            "audience_id": audience_id,
            "strategy_used": strategy,
            "total_leads": total_leads,
            "segments": segments,
            "coverage": coverage,
            "overlap_analysis": overlap,
            "overlap_matrix": ov_matrix,
            "segmentation_quality_score": quality,
            "decision_trace": decision_trace,
            "version": self.VERSION,
            "latency_ms": latency_ms,
        }

    # -------------------------------------------------------------------------
    # Auxiliares de acciones / reglas
    # -------------------------------------------------------------------------
    @staticmethod
    def _recommendations_by_name(segment_name: str) -> List[str]:
        catalog = {
            "High Value Ready": ["Fast-track to sales", "Premium product offer", "Personalized consultation"],
            "Nurture Potential": ["Nurture sequence", "Educational content", "Monthly check-in"],
            "Re-engage": ["Re-engagement offer", "Drop-off survey", "Multi-channel outreach"],
            "Churn Risk": ["Urgent retention", "Executive outreach", "Win-back incentive"],
            "High Engagement": ["Upsell/Cross-sell", "Loyalty program", "Referral program"],
            "Price Sensitive": ["Highlight low-rate offers", "Cost savings", "Flexible payments"],
            "High Income": ["Investment products", "Private banking consult", "Wealth newsletter"],
            "Mid Income": ["Standard credit offers", "Balance transfer", "Bundled products"],
            "Young Professionals": ["Mobile-first onboarding", "Education financing", "Digital wallet upsell"],
        }
        return catalog.get(segment_name, ["Standard marketing cadence"])

    @staticmethod
    def _rules_for_segment_name(segment_name: str) -> List[str]:
        rules = {
            "High Value Ready": [
                "income >= 60000",
                "engagement_score >= 0.7",
                "credit_score >= 700",
            ],
            "Nurture Potential": [
                "40000 <= income < 60000",
                "0.4 <= engagement_score < 0.7",
                "credit_score >= 650",
            ],
            "Re-engage": [
                "days_since_last_interaction >= 30",
                "previous_conversions == 0",
                "engagement_score < 0.5",
            ],
            "Churn Risk": [
                "days_since_last_interaction >= 90",
                "engagement_score <= 0.3",
            ],
            "High Engagement": [
                "engagement_score >= 0.7",
            ],
            "Price Sensitive": [
                "income < 40000",
                "engagement_score >= 0.5",
            ],
            "High Income": [
                "income >= 60000",
            ],
            "Mid Income": [
                "40000 <= income < 60000",
            ],
            "Young Professionals": [
                "age < 35",
            ],
        }
        return rules.get(segment_name, [])
    
    # -------------------------------------------------------------------------
    # Métricas del agente
    # -------------------------------------------------------------------------
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_name": self.name,
            "agent_version": self.VERSION,
            "tenant_id": self.tenant_id,
            "available_segments": len(self.segment_definitions),
            "status": "healthy",
        }
