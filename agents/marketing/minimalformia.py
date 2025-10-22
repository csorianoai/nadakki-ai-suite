"""
MinimalFormIA - Production-Ready v2.3.0

PropÃ³sito
---------
Optimizar formularios de precalificaciÃ³n reduciendo fricciÃ³n sin perder capacidad
de calificar leads. DiseÃ±ado para entornos enterprise: determinista, auditable,
y con controles de privacidad/compliance.

Novedades v2.3.0 (vs v2.0.0)
----------------------------
- validate_request() estricta + contratos internos (tipos/campos mÃ­nimos)
- SelecciÃ³n de campos con trazabilidad: reason_codes por cada campo
- LÃ­mite de PII y consentimiento explÃ­cito con policy configurable
- A/B testing determinista (seed + tenant) y variante por canal/producto
- MÃ©tricas ampliadas (submit/abandon + p95 time, drop-off step estimado)
- Progressive disclosure robusto (siempre respeta min/max y prioridades)
- Health & metrics enriquecidos; logs y decision_trace accionables
- Sin dependencias externas (stdlib-only), determinista

Uso rÃ¡pido
----------
agent = MinimalFormIA("tenant_X")
result = await agent.execute({...payload...})
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from typing import Dict, List, Optional, Any, Literal, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinimalFormIA:
    """Agente de optimizaciÃ³n de formularios (mÃ­nima fricciÃ³n, mÃ¡xima conversiÃ³n)"""

    VERSION = "v2.3.0"

    # ---------------------------- Init & Config -------------------------------

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.tenant_id = tenant_id
        self.name = "MinimalFormIA"
        self.config = config or self._default_config()
        logger.info("MinimalFormIA init tenant=%s version=%s", tenant_id, self.VERSION)

    def _default_config(self) -> Dict[str, Any]:
        """ConfiguraciÃ³n por defecto (multi-tenant safe)."""
        return {
            "jurisdictions": ["US", "DO", "MX"],
            "channels": ["web", "mobile"],
            "field_catalog": self._default_field_catalog(),
            "validation_rules": self._default_validation_rules(),
            "progressive_disclosure": True,
            "max_fields_step1": 3,
            "pii_warnings": True,
            "pii_limits": {
                "max_pii_fields": 4,       # LÃ­mite de PII totales permitidas
                "forbid_ssn_without_consent": True
            },
            "channel_overrides": {
                # En mobile priorizamos menos campos en el primer paso
                "mobile": {"max_fields_step1": 2}
            },
            "product_overrides": {
                # Para savings, no pedir propÃ³sito ni deuda
                "savings_account": {
                    "skip_fields": ["loan_purpose", "existing_debt", "ssn_last4"]
                }
            }
        }

    def _default_field_catalog(self) -> Dict[str, Dict[str, Any]]:
        """CatÃ¡logo de campos con metadata (contrato interno)."""
        return {
            # ===== Campos bÃ¡sicos (siempre necesarios) =====
            "email": {
                "type": "email", "required": True, "priority": 1, "pii": True,
                "validation": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "placeholder": "tu@email.com", "error_msg": "Email invÃ¡lido"
            },
            "full_name": {
                "type": "text", "required": True, "priority": 2, "pii": True,
                "validation": r"^[a-zA-ZÃ¡Ã©Ã­Ã³ÃºÃ±ÃÃ‰ÃÃ“ÃšÃ‘\s]{3,100}$",
                "placeholder": "Nombre completo", "error_msg": "Nombre invÃ¡lido"
            },
            "phone": {
                "type": "tel", "required": True, "priority": 3, "pii": True,
                "validation": r"^\+?[1-9]\d{7,14}$",
                "placeholder": "+1-809-555-0100", "error_msg": "TelÃ©fono invÃ¡lido"
            },

            # ===== Campos de calificaciÃ³n (predictivos) =====
            "income_range": {
                "type": "select", "required": False, "priority": 4, "pii": False,
                "options": ["<30k", "30k-50k", "50k-80k", "80k-120k", ">120k"],
                "placeholder": "Rango de ingresos",
                "skip_if": {"product": ["savings_account"]}
            },
            "employment_status": {
                "type": "select", "required": False, "priority": 5, "pii": False,
                "options": ["employed", "self_employed", "retired", "student"],
                "placeholder": "SituaciÃ³n laboral"
            },
            "loan_purpose": {
                "type": "select", "required": False, "priority": 6, "pii": False,
                "options": ["debt_consolidation", "home_improvement", "business", "education", "other"],
                "placeholder": "Â¿Para quÃ© necesitas el prÃ©stamo?",
                "show_if": {"product": ["personal_loan", "business_loan"]}
            },

            # ===== Campos opcionales avanzados =====
            "credit_score_estimate": {
                "type": "select", "required": False, "priority": 7, "pii": False,
                "options": ["excellent_750+", "good_700-749", "fair_650-699", "poor_<650", "unknown"],
                "placeholder": "Â¿Conoces tu score crediticio?", "progressive": True
            },
            "existing_debt": {
                "type": "number", "required": False, "priority": 8, "pii": False,
                "validation": r"^\d{1,10}$",
                "placeholder": "Deudas actuales (aproximado)", "progressive": True
            },
            "ssn_last4": {
                "type": "text", "required": False, "priority": 10, "pii": True,
                "validation": r"^\d{4}$",
                "placeholder": "Ãšltimos 4 dÃ­gitos SSN", "jurisdiction": ["US"],
                "progressive": True,
                "warning": "Solo pedimos esto para verificaciÃ³n de identidad/ crÃ©dito"
            }
        }

    def _default_validation_rules(self) -> Dict[str, Any]:
        return {
            "min_fields": 3,
            "max_fields": 8,
            "require_consent": True,   # Debe mostrarse copy o checkbox
            "tcpa_compliant": True     # Para leads con contacto telefÃ³nico
        }

    # ------------------------------ ValidaciÃ³n --------------------------------

    def validate_request(self, data: Dict[str, Any]) -> Optional[str]:
        """Valida el payload de entrada (contract-first)."""
        if not isinstance(data, dict):
            return "invalid_input: payload must be an object"

        if not data.get("form_id"):
            return "invalid_input: form_id required"

        profile = data.get("profile")
        if not isinstance(profile, dict):
            return "invalid_input: profile must be an object"

        product = profile.get("product")
        jurisdiction = profile.get("jurisdiction")
        channel = profile.get("channel")

        if product not in ["personal_loan", "credit_card", "savings_account", "business_loan"]:
            return "invalid_input: unsupported product"
        if jurisdiction not in self.config["jurisdictions"]:
            return "invalid_input: unsupported jurisdiction"
        if channel not in self.config["channels"]:
            return "invalid_input: unsupported channel"

        current_fields = data.get("current_fields", [])
        if not isinstance(current_fields, list):
            return "invalid_input: current_fields must be a list"

        goal = data.get("optimization_goal", "balanced")
        if goal not in ["minimize_fields", "maximize_qualification", "balanced"]:
            return "invalid_input: unsupported optimization_goal"

        # ab_test_seed es opcional, pero si viene debe ser str
        ab = data.get("ab_test_seed")
        if ab is not None and not isinstance(ab, str):
            return "invalid_input: ab_test_seed must be a string or null"

        return None

    # ----------------------------- Field Helpers ------------------------------

    def _field_applicable(self, field_meta: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """EvalÃºa si un campo aplica (producto/jurisdicciÃ³n/show_if/skip_if)."""
        product = profile.get("product")
        jurisdiction = profile.get("jurisdiction")

        # skip_if por producto
        skip_if = field_meta.get("skip_if", {})
        if "product" in skip_if and product in skip_if["product"]:
            return False

        # show_if por producto
        show_if = field_meta.get("show_if", {})
        if show_if and "product" in show_if:
            if product not in show_if["product"]:
                return False

        # jurisdicciÃ³n especÃ­fica
        required_j = field_meta.get("jurisdiction")
        if required_j and jurisdiction not in required_j:
            return False

        # product_overrides globales
        prod_over = self.config.get("product_overrides", {}).get(product, {})
        if "skip_fields" in prod_over:
            # Si el nombre del campo estÃ¡ en la lista, se omite
            # (se resuelve fuera con el nombre del campo)
            pass

        return True

    def _deterministic_variant(self, seed: Optional[str], profile: Dict[str, Any]) -> str:
        """Variante A/B determinista (tenant + seed + product + channel)."""
        basis = f"{self.tenant_id}|{seed or ''}|{profile.get('product')}|{profile.get('channel')}"
        h = hashlib.sha256(basis.encode()).hexdigest()
        return "B" if int(h[:8], 16) % 2 else "A"

    def _deterministic_field_order(self, profile: Dict[str, Any], seed: Optional[str]) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Ordena campos aplicables de manera determinista y devuelve:
        - lista de campos ordenados
        - reason_codes por campo (por quÃ© entra / mÃ©tricas)
        """
        catalog = self.config["field_catalog"]
        product = profile.get("product", "unknown")

        # Filtrado inicial por aplicabilidad
        items: List[Tuple[str, Dict[str, Any]]] = []
        reasons: Dict[str, List[str]] = {}
        prod_skip = set(self.config.get("product_overrides", {}).get(product, {}).get("skip_fields", []))

        for fname, meta in catalog.items():
            if fname in prod_skip:
                reasons[fname] = ["skipped:product_override"]
                continue
            if self._field_applicable(meta, profile):
                items.append((fname, meta))
                reasons.setdefault(fname, []).append("applicable")
            else:
                reasons[fname] = reasons.get(fname, []) + ["skipped:show_or_skip_rules"]

        # Orden base por prioridad
        items.sort(key=lambda x: x[1]["priority"])

        # A/B: para la variante B invertimos los opcionales para probar impacto
        variant = self._deterministic_variant(seed, profile)
        required = [(f, m) for (f, m) in items if m["required"]]
        optional = [(f, m) for (f, m) in items if not m["required"]]
        if variant == "B":
            optional.reverse()
            for f, _ in optional:
                reasons.setdefault(f, []).append("ab_variant_B_reordered")
        ordered = required + optional

        # Emitir lista final + razones
        return [f for f, _ in ordered], reasons

    def _progressive_steps(self, fields: List[str], profile: Dict[str, Any]) -> List[List[str]]:
        """Divide campos en pasos progresivos respetando overrides por canal."""
        if not self.config["progressive_disclosure"]:
            return [fields]

        catalog = self.config["field_catalog"]
        max_step1 = int(self.config["max_fields_step1"])
        # Overrides por canal
        ch_over = self.config.get("channel_overrides", {}).get(profile.get("channel"), {})
        if "max_fields_step1" in ch_over:
            max_step1 = int(ch_over["max_fields_step1"])

        # Step 1: requeridos hasta max_step1
        required = [f for f in fields if catalog[f]["required"]]
        step1 = required[:max_step1]

        # Step 2: opcionales no progresivos
        step2 = [f for f in fields if f not in step1 and not catalog[f].get("progressive", False)]

        # Step 3: progresivos
        step3 = [f for f in fields if catalog[f].get("progressive", False) and f not in step1]

        steps = [step1]
        if step2:
            steps.append(step2)
        if step3:
            steps.append(step3)
        return steps

    def _validate_field(self, field_name: str, value: Any) -> Optional[str]:
        """Valida un campo individual (para extensiones futuras/inline checks)."""
        meta = self.config["field_catalog"].get(field_name)
        if not meta:
            return "unknown_field"

        if meta.get("required") and (value is None or value == ""):
            return meta.get("error_msg", "Campo requerido")

        pattern = meta.get("validation")
        if pattern and value:
            if not re.match(pattern, str(value)):
                return meta.get("error_msg", "Formato invÃ¡lido")
        return None

    # --------------------------- Compliance & MÃ©tricas ------------------------

    def _estimate_metrics(
        self, fields_count: int, has_pii_warnings: bool, progressive: bool, profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        EstimaciÃ³n heurÃ­stica (determinista) de mÃ©tricas:
        - submit_rate / abandonment_rate
        - p95 tiempo de completado
        - paso con mayor drop-off estimado
        """
        # Baseline (observado en mÃºltiples funnels de la industria ~42%)
        base_submit = 0.42

        # PenalizaciÃ³n por mÃ¡s campos (a partir de 3)
        field_penalty = max(0.0, min((fields_count - 3) * 0.05, 0.30))

        # Boosts
        progressive_boost = 0.08 if progressive else 0.0
        pii_boost = 0.03 if has_pii_warnings else 0.0

        # Ajuste por producto (mayor fricciÃ³n en prÃ©stamos)
        product_factor = {
            "savings_account": 0.10,
            "credit_card": 0.05,
            "personal_loan": -0.05,
            "business_loan": -0.10
        }.get(profile.get("product"), 0.0)

        submit_rate = max(0.10, min(0.95, base_submit - field_penalty + progressive_boost + pii_boost + product_factor))
        abandonment_rate = 1.0 - submit_rate

        # p95 time ~ 10s por campo (mÃ¡s conservador)
        p95_time = int(fields_count * 10)

        # Paso con mayor drop-off estimado:
        # - si hay paso 2 con campos opcionales largos, ahÃ­ suele caer
        drop_step = 2 if progressive else 1

        return {
            "estimated_submit_rate": round(submit_rate, 3),
            "estimated_abandonment_rate": round(abandonment_rate, 3),
            "p95_time_to_complete_seconds": p95_time,
            "likely_dropoff_step": drop_step
        }

    def _compliance_check(
        self, fields: List[str], warnings: List[str], profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Checks de compliance/privacidad bÃ¡sicos (PII/consent/SSN)."""
        catalog = self.config["field_catalog"]
        pii_fields = [f for f in fields if catalog[f].get("pii")]
        issues: List[str] = []

        # LÃ­mite de PII
        if len(pii_fields) > int(self.config["pii_limits"]["max_pii_fields"]):
            issues.append("excessive_pii_collection")

        # Consentimiento
        if self.config["validation_rules"]["require_consent"]:
            joined = " ".join(warnings).lower()
            if "tÃ©rminos" not in joined and "condiciones" not in joined and "consent" not in joined:
                issues.append("missing_consent_notice")

        # SSN solo en US y con copy de advertencia (si polÃ­tica activa)
        if "ssn_last4" in fields:
            if profile.get("jurisdiction") != "US":
                issues.append("ssn_outside_US")
            if self.config["pii_limits"]["forbid_ssn_without_consent"]:
                joined = " ".join(warnings).lower()
                if "identidad" not in joined and "crÃ©dito" not in joined:
                    issues.append("ssn_without_purpose_warning")

        status = "fail" if issues else "pass"
        return {
            "status": status,
            "issues": issues,
            "pii_fields_count": len(pii_fields),
            "tcpa_compliant": self.config["validation_rules"]["tcpa_compliant"]
        }

    # --------------------------------- API ------------------------------------

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        {
          "form_id": str,
          "profile": {
            "product": "personal_loan|credit_card|savings_account|business_loan",
            "jurisdiction": "US|DO|MX",
            "channel": "web|mobile",
            "user_segment": "high_value|mid_value|low_value"
          },
          "current_fields": [str],
          "optimization_goal": "minimize_fields|maximize_qualification|balanced",
          "ab_test_seed": str (opcional)
        }
        """
        t0 = time.perf_counter()
        err = self.validate_request(data)
        if err:
            return self._error_response(err, int((time.perf_counter() - t0) * 1000))

        decision_trace: List[str] = []
        form_id = data["form_id"]
        profile = data["profile"]
        current_fields = list(dict.fromkeys(data.get("current_fields", [])))  # dedupe
        goal = data.get("optimization_goal", "balanced")
        ab_seed = data.get("ab_test_seed")

        decision_trace.append(f"goal={goal}")
        decision_trace.append(f"profile.product={profile.get('product')}")
        decision_trace.append(f"profile.channel={profile.get('channel')}")
        decision_trace.append(f"profile.jurisdiction={profile.get('jurisdiction')}")

        # Orden determinista + razones
        ordered_fields, reasons = self._deterministic_field_order(profile, ab_seed)

        # Aplicar objetivo de optimizaciÃ³n (min/max)
        vrules = self.config["validation_rules"]
        min_fields = int(vrules["min_fields"])
        max_fields = int(vrules["max_fields"])

        catalog = self.config["field_catalog"]

        if goal == "minimize_fields":
            required = [f for f in ordered_fields if catalog[f]["required"]]
            optional_top = [f for f in ordered_fields if not catalog[f]["required"]]
            # Tomamos 1 opcional si hace falta para llegar al mÃ­nimo
            take_opt = max(0, min(1, min_fields - len(required)))
            recommended = required + optional_top[:take_opt]
            decision_trace.append("apply:minimize_fields")
        elif goal == "maximize_qualification":
            recommended = ordered_fields[:max_fields]  # aÃºn respetamos techo de UX
            decision_trace.append("apply:maximize_qualification")
        else:  # balanced
            recommended = ordered_fields[:max_fields]
            decision_trace.append("apply:balanced")

        # Garantizar el mÃ­nimo
        if len(recommended) < min_fields:
            # Rellenar con mÃ¡s opcionales si hay
            extra = [f for f in ordered_fields if f not in recommended]
            recommended += extra[: (min_fields - len(recommended))]
            decision_trace.append("enforced:min_fields")

        # Progressive steps
        steps = self._progressive_steps(recommended, profile)

        # Warnings (copy legal + PII)
        warnings: List[str] = []
        for f in recommended:
            meta = catalog[f]
            if meta.get("pii") and self.config["pii_warnings"] and "warning" in meta:
                warnings.append(meta["warning"])
        if vrules["require_consent"]:
            warnings.append("Al continuar, aceptas nuestros TÃ©rminos y Condiciones y autorizas la verificaciÃ³n de identidad/ crÃ©dito.")

        # AB variant
        ab_variant = self._deterministic_variant(ab_seed, profile)
        decision_trace.append(f"ab_variant={ab_variant}")

        # MÃ©tricas estimadas
        estimated = self._estimate_metrics(
            len(recommended),
            has_pii_warnings=bool(warnings),
            progressive=len(steps) > 1,
            profile=profile,
        )

        # Compliance
        compliance = self._compliance_check(recommended, warnings, profile)
        decision_trace.append(f"compliance={compliance['status']}")

        # ConstrucciÃ³n de field_config (contrato de salida por campo)
        field_config = []
        for f in recommended:
            m = catalog[f]
            field_config.append({
                "field_name": f,
                "type": m["type"],
                "required": m["required"],
                "placeholder": m.get("placeholder", ""),
                "validation": m.get("validation"),
                "error_msg": m.get("error_msg"),
                "options": m.get("options"),
                "pii": m.get("pii", False),
                "reason_codes": reasons.get(f, [])
            })

        latency_ms = int((time.perf_counter() - t0) * 1000)
        out = {
            "tenant_id": self.tenant_id,
            "form_id": form_id,
            "status": "ready" if compliance["status"] == "pass" else "needs_review",
            "recommended_fields": recommended,
            "field_config": field_config,
            "progressive_steps": steps,
            "validation_rules": vrules,
            "warnings": warnings,
            "compliance": compliance,
            "estimated_metrics": estimated,
            "ab_variant": ab_variant,
            "optimization_goal": goal,
            "decision_trace": decision_trace,
            "version": self.VERSION,
            "latency_ms": latency_ms,
        }
        logger.info(
            "MinimalFormIA result tenant=%s form=%s fields=%d steps=%d status=%s latency=%dms",
            self.tenant_id, form_id, len(recommended), len(steps), out["status"], latency_ms
        )
        return out

    # ------------------------------ Health/Metrics ----------------------------

    def health_check(self) -> Dict[str, Any]:
        cfg_ok = all(k in self.config for k in [
            "field_catalog", "validation_rules", "progressive_disclosure", "pii_limits"
        ])
        return {
            "status": "ok" if cfg_ok else "degraded",
            "version": self.VERSION,
            "tenant_id": self.tenant_id,
            "config_ok": cfg_ok
        }

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_name": self.name,
            "agent_version": self.VERSION,
            "tenant_id": self.tenant_id,
            "fields_catalog_size": len(self.config["field_catalog"]),
            "status": "healthy"
        }

    # -------------------------------- Errores ---------------------------------

    def _error_response(self, error: str, latency_ms: int) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "status": "error",
            "error": error,
            "latency_ms": latency_ms,
            "version": self.VERSION
        }


# =============================================================================
# Testing (quick async runner)
# =============================================================================
async def main() -> None:
    print("=" * 80)
    print("MINIMAL FORM IA - TEST (v2.3.0)")
    print("=" * 80)

    agent = MinimalFormIA(tenant_id="tn_bank001")

    test_request = {
        "form_id": "form_loan_001",
        "profile": {
            "product": "personal_loan",
            "jurisdiction": "US",
            "channel": "mobile",
            "user_segment": "mid_value"
        },
        "current_fields": [],
        "optimization_goal": "balanced",
        "ab_test_seed": "seed_demo_123"
    }

    print(f"\nOptimizando formulario para: {test_request['profile']['product']}")
    result = await agent.execute(test_request)

    if result.get("status") == "error":
        print("ERROR:", result.get("error"))
        return

    print(f"\nStatus: {result['status']} | Variant: {result['ab_variant']}")
    print(f"Campos recomendados ({len(result['recommended_fields'])}): {', '.join(result['recommended_fields'])}")
    print(f"\nProgressive steps: {len(result['progressive_steps'])}")
    for i, step in enumerate(result['progressive_steps'], 1):
        print(f"  Step {i}: {', '.join(step)}")

    em = result["estimated_metrics"]
    print(f"\nEstimated submit rate: {em['estimated_submit_rate']*100:.1f}%")
    print(f"Estimated abandonment: {em['estimated_abandonment_rate']*100:.1f}%")
    print(f"p95 time to complete: {em['p95_time_to_complete_seconds']}s")
    print(f"Likely drop-off step: {em['likely_dropoff_step']}")

    print(f"\nCompliance: {result['compliance']['status']} | Issues: {result['compliance']['issues']}")
    print(f"Decision trace: {result['decision_trace']}")
    print(f"Latency: {result['latency_ms']}ms")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
