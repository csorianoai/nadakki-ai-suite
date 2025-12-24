"""
CashOfferFilterIA v3.0 - Production-Ready (Mejora Quirúrgica)

Principio: NO romper lo que funciona, SOLO agregar valor medible.

Mejoras v3.0 sobre v2.1:
- Reason Codes Layer opcional (composición)
- Audit trail estructurado
- Confidence score
- 100% compatible con API existente

NO incluye:
- Over-engineering con múltiples clases
- Reason codes inflados
- Complejidad innecesaria
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Layer opcional (composición, no dependencia)
try:
    from agents.marketing.layers.reason_codes_layer import apply_reason_codes
    REASON_CODES_LAYER_AVAILABLE = True
except ImportError:
    REASON_CODES_LAYER_AVAILABLE = False


class CashOfferFilterIA:
    VERSION = "v3.0.0"
    AGENT_ID = "cashofferfilteria"

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.tenant_id = tenant_id
        self.name = "CashOfferFilterIA"
        self.config = config or self._default_config()
        
        # Métricas
        self.metrics = {"requests": 0, "errors": 0, "approvals": 0, "rejections": 0, "total_ms": 0.0}
        
        logger.info("CashOfferFilterIA v3.0 init tenant=%s", tenant_id)

    # ═══════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN
    # ═══════════════════════════════════════════════════════════════════
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            "offer_tiers": {
                "platinum": {"credit_score_min": 750, "income_min": 60000, "max_amount": 50000, "base_apr": 8.99, "terms_months": [12, 24, 36, 48, 60]},
                "gold": {"credit_score_min": 700, "income_min": 40000, "max_amount": 30000, "base_apr": 12.99, "terms_months": [12, 24, 36, 48]},
                "silver": {"credit_score_min": 650, "income_min": 30000, "max_amount": 15000, "base_apr": 18.99, "terms_months": [12, 24, 36]},
                "bronze": {"credit_score_min": 600, "income_min": 20000, "max_amount": 7500, "base_apr": 24.99, "terms_months": [12, 24]}
            },
            "risk_limits": {
                "max_loan_to_income_ratio": 0.40,
                "max_debt_to_income_ratio": 0.50,
                "min_credit_score": 600,
                "max_loan_amount": 50000
            },
            "pricing_matrix": {12: 0.0, 24: 0.5, 36: 1.0, 48: 1.5, 60: 2.0},
            "compliance": {
                "require_apr_disclosure": True,
                "fair_lending_check": True,
                "affordability_check": True,
                "max_apr": 35.99
            }
        }

    # ═══════════════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════════════
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta evaluación de oferta de crédito."""
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        # Validar input
        err = self._validate_request(data)
        if err:
            self.metrics["errors"] += 1
            return self._error_response(err, t0)
        
        decision_trace: List[str] = []
        customer_id = data["customer_id"]
        customer = data["customer"]
        requested_amount = data.get("requested_amount")
        
        credit_score = customer.get("credit_score", 0)
        income = Decimal(str(customer.get("income", 0)))
        
        # ─────────────────────────────────────────────────────────────
        # 1. ELEGIBILIDAD
        # ─────────────────────────────────────────────────────────────
        if credit_score < self.config["risk_limits"]["min_credit_score"]:
            self.metrics["rejections"] += 1
            return self._rejection_response(
                customer_id, 
                f"credit_score_below_minimum_{credit_score}",
                ["rejected_low_credit_score"],
                t0
            )
        
        # ─────────────────────────────────────────────────────────────
        # 2. TIER DETERMINATION
        # ─────────────────────────────────────────────────────────────
        tier = self._determine_tier(customer)
        if not tier:
            self.metrics["rejections"] += 1
            return self._rejection_response(
                customer_id,
                "no_qualifying_tier",
                ["no_tier_match"],
                t0
            )
        decision_trace.append(f"tier={tier}")
        
        # ─────────────────────────────────────────────────────────────
        # 3. MAX OFFER CALCULATION
        # ─────────────────────────────────────────────────────────────
        max_offer = self._calculate_max_offer(customer, tier)
        if max_offer <= 0:
            self.metrics["rejections"] += 1
            return self._rejection_response(
                customer_id,
                "max_offer_zero_due_to_debt",
                decision_trace + ["max_offer=0"],
                t0
            )
        
        # ─────────────────────────────────────────────────────────────
        # 4. OFFER GENERATION
        # ─────────────────────────────────────────────────────────────
        base_amount = self._determine_base_amount(requested_amount, max_offer)
        variants = self._generate_variants(base_amount, tier, credit_score)
        primary = next(v for v in variants if v["variant"] == "balanced")
        
        # ─────────────────────────────────────────────────────────────
        # 5. AFFORDABILITY CHECK
        # ─────────────────────────────────────────────────────────────
        existing_payment = Decimal(str(customer.get("existing_debt_monthly_payment", 0)))
        affordable, why = self._affordability_check(
            Decimal(str(primary["monthly_payment"])), 
            income, 
            existing_payment
        )
        decision_trace.append(f"affordable={affordable}")
        
        if not affordable and self.config["compliance"]["affordability_check"]:
            self.metrics["rejections"] += 1
            return self._rejection_response(customer_id, why, decision_trace, t0)
        
        # ─────────────────────────────────────────────────────────────
        # 6. COMPLIANCE CHECK
        # ─────────────────────────────────────────────────────────────
        compliance = self._compliance_check(primary)
        decision_trace.append(f"compliance={compliance['status']}")
        
        # ─────────────────────────────────────────────────────────────
        # 7. RISK ASSESSMENT
        # ─────────────────────────────────────────────────────────────
        risk = self._build_risk_assessment(tier, max_offer, base_amount, income, primary, existing_payment)
        
        # ─────────────────────────────────────────────────────────────
        # 8. REASON CODES (COMPOSICIÓN OPCIONAL)
        # ─────────────────────────────────────────────────────────────
        reason_codes = self._generate_reason_codes(customer, tier, affordable, compliance)
        
        # ─────────────────────────────────────────────────────────────
        # 9. BUILD RESPONSE
        # ─────────────────────────────────────────────────────────────
        self.metrics["approvals"] += 1
        latency = int((time.perf_counter() - t0) * 1000)
        self.metrics["total_ms"] += latency
        
        response = {
            "tenant_id": self.tenant_id,
            "customer_id": customer_id,
            "eligible": True,
            "tier": tier,
            "primary_offer": primary,
            "alternative_offers": [v for v in variants if v["variant"] != "balanced"],
            "compliance": compliance,
            "risk_assessment": risk,
            "decision_trace": decision_trace,
            "reason_codes": reason_codes,
            "confidence": self._calculate_confidence(customer, tier, affordable),
            "version": self.VERSION,
            "latency_ms": latency
        }
        
        logger.info(
            "cash_offer approved tenant=%s customer=%s tier=%s amount=%.2f apr=%.2f latency=%dms",
            self.tenant_id, customer_id, tier, primary["amount"], primary["apr"], latency
        )
        
        return response

    # ═══════════════════════════════════════════════════════════════════
    # HELPERS DE NEGOCIO
    # ═══════════════════════════════════════════════════════════════════
    
    def _validate_request(self, data: Dict[str, Any]) -> Optional[str]:
        """Valida el request de entrada."""
        if not isinstance(data, dict):
            return "invalid_input: payload must be object"
        if not data.get("customer_id"):
            return "invalid_input: customer_id required"
        c = data.get("customer")
        if not isinstance(c, dict):
            return "invalid_input: customer must be object"
        if "credit_score" not in c or "income" not in c:
            return "invalid_input: customer.credit_score and customer.income required"
        return None

    def _determine_tier(self, customer: Dict[str, Any]) -> Optional[str]:
        """Determina el tier del cliente."""
        cs = customer.get("credit_score", 0)
        inc = customer.get("income", 0)
        
        for name in ["platinum", "gold", "silver", "bronze"]:
            cfg = self.config["offer_tiers"][name]
            if cs >= cfg["credit_score_min"] and inc >= cfg["income_min"]:
                return name
        return None

    def _calculate_max_offer(self, customer: Dict[str, Any], tier: str) -> Decimal:
        """Calcula el monto máximo de oferta."""
        tier_cfg = self.config["offer_tiers"][tier]
        risk = self.config["risk_limits"]
        
        income = Decimal(str(customer.get("income", 0)))
        existing_debt = Decimal(str(customer.get("existing_debt", 0)))
        
        tier_max = Decimal(str(tier_cfg["max_amount"]))
        lti_max = income * Decimal(str(risk["max_loan_to_income_ratio"]))
        
        max_dti = Decimal(str(risk["max_debt_to_income_ratio"]))
        dti_max = max(Decimal("0"), (max_dti * income) - existing_debt)
        
        global_max = Decimal(str(risk["max_loan_amount"]))
        
        return min(tier_max, lti_max, dti_max, global_max).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _determine_base_amount(self, requested: Optional[float], max_offer: Decimal) -> Decimal:
        """Determina el monto base de la oferta."""
        if requested:
            req = Decimal(str(requested))
            return min(req, max_offer)
        return (max_offer * Decimal("0.80")).quantize(Decimal("0.01"))

    def _calculate_apr(self, tier: str, term_months: int, credit_score: int) -> Decimal:
        """Calcula el APR para una oferta."""
        tier_cfg = self.config["offer_tiers"][tier]
        base = Decimal(str(tier_cfg["base_apr"]))
        adj_term = Decimal(str(self.config["pricing_matrix"].get(term_months, 0)))
        score_adj = Decimal("1.0") if credit_score < tier_cfg["credit_score_min"] + 30 else Decimal("0.0")
        
        apr = base + adj_term + score_adj
        return min(apr, Decimal(str(self.config["compliance"]["max_apr"]))).quantize(Decimal("0.01"))

    def _calculate_monthly_payment(self, amount: Decimal, apr: Decimal, term: int) -> Decimal:
        """Calcula el pago mensual."""
        if amount <= 0:
            return Decimal("0.00")
        
        monthly_rate = (apr / Decimal("100")) / Decimal("12")
        if monthly_rate == 0:
            return (amount / Decimal(str(term))).quantize(Decimal("0.01"))
        
        num = monthly_rate * ((Decimal("1") + monthly_rate) ** term)
        den = ((Decimal("1") + monthly_rate) ** term) - Decimal("1")
        return (amount * (num / den)).quantize(Decimal("0.01"))

    def _generate_variants(self, base_amount: Decimal, tier: str, credit_score: int) -> List[Dict[str, Any]]:
        """Genera variantes de oferta."""
        terms = self.config["offer_tiers"][tier]["terms_months"]
        variants = []
        
        # Conservative (70% del monto, plazo corto)
        a1 = (base_amount * Decimal("0.70")).quantize(Decimal("0.01"))
        t1 = terms[0]
        apr1 = self._calculate_apr(tier, t1, credit_score)
        mp1 = self._calculate_monthly_payment(a1, apr1, t1)
        variants.append(self._build_variant("conservative", a1, t1, apr1, mp1))
        
        # Balanced (100% del monto, plazo medio)
        t2 = terms[len(terms) // 2] if len(terms) > 1 else terms[0]
        apr2 = self._calculate_apr(tier, t2, credit_score)
        mp2 = self._calculate_monthly_payment(base_amount, apr2, t2)
        variants.append(self._build_variant("balanced", base_amount, t2, apr2, mp2))
        
        # Aggressive (100% del monto, plazo largo)
        t3 = terms[-1]
        apr3 = self._calculate_apr(tier, t3, credit_score)
        mp3 = self._calculate_monthly_payment(base_amount, apr3, t3)
        variants.append(self._build_variant("aggressive", base_amount, t3, apr3, mp3))
        
        return variants

    def _build_variant(self, name: str, amount: Decimal, term: int, apr: Decimal, mp: Decimal) -> Dict[str, Any]:
        """Construye un objeto de variante."""
        return {
            "variant": name,
            "amount": float(amount),
            "term_months": term,
            "apr": float(apr),
            "monthly_payment": float(mp),
            "total_cost": float(mp * term)
        }

    def _affordability_check(self, monthly_payment: Decimal, income: Decimal, existing_payment: Decimal) -> Tuple[bool, Optional[str]]:
        """Verifica affordability."""
        monthly_income = income / Decimal("12")
        if monthly_income <= 0:
            return False, "no_income"
        
        total_debt = monthly_payment + existing_payment
        dti = total_debt / monthly_income
        max_dti = Decimal(str(self.config["risk_limits"]["max_debt_to_income_ratio"]))
        
        if dti > max_dti:
            return False, f"dti_too_high_{float(dti):.2f}"
        return True, None

    def _compliance_check(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica compliance."""
        issues = []
        
        if self.config["compliance"]["require_apr_disclosure"] and "apr" not in offer:
            issues.append("missing_apr_disclosure")
        
        apr = float(offer.get("apr", 0))
        if apr > float(self.config["compliance"]["max_apr"]):
            issues.append("apr_exceeds_legal_max")
        
        return {"status": "fail" if issues else "pass", "issues": issues}

    def _build_risk_assessment(self, tier: str, max_offer: Decimal, base_amount: Decimal, 
                               income: Decimal, primary: Dict, existing_payment: Decimal) -> Dict[str, Any]:
        """Construye el risk assessment."""
        monthly_income = income / Decimal("12") if income > 0 else Decimal("1")
        
        return {
            "tier": tier,
            "max_offer_amount": float(max_offer),
            "loan_to_income_ratio": float(base_amount / income) if income > 0 else 0.0,
            "debt_to_income_ratio": float(
                ((Decimal(str(primary["monthly_payment"])) + existing_payment) * 12) / income
            ) if income > 0 else 0.0,
            "risk_level": "low" if tier in ["platinum", "gold"] else ("medium" if tier == "silver" else "high")
        }

    def _generate_reason_codes(self, customer: Dict, tier: str, affordable: bool, compliance: Dict) -> List[str]:
        """Genera reason codes explicativos."""
        reasons = []
        
        credit_score = customer.get("credit_score", 0)
        income = customer.get("income", 0)
        
        # Factores positivos
        if credit_score >= 750:
            reasons.append("Excelente historial crediticio (750+)")
        elif credit_score >= 700:
            reasons.append("Buen historial crediticio (700-749)")
        elif credit_score >= 650:
            reasons.append("Historial crediticio aceptable (650-699)")
        
        if income >= 80000:
            reasons.append("Ingresos altos (>$80k)")
        elif income >= 50000:
            reasons.append("Ingresos moderados-altos ($50k-$80k)")
        elif income >= 30000:
            reasons.append("Ingresos moderados ($30k-$50k)")
        
        # Tier
        tier_descriptions = {
            "platinum": "Calificado para tier Platinum (mejores condiciones)",
            "gold": "Calificado para tier Gold (condiciones preferenciales)",
            "silver": "Calificado para tier Silver (condiciones estándar)",
            "bronze": "Calificado para tier Bronze (condiciones básicas)"
        }
        reasons.append(tier_descriptions.get(tier, f"Tier: {tier}"))
        
        # Affordability
        if affordable:
            reasons.append("Capacidad de pago verificada")
        
        # Compliance
        if compliance["status"] == "pass":
            reasons.append("Cumple requisitos regulatorios")
        
        # Intentar usar Reason Codes Layer si está disponible
        if REASON_CODES_LAYER_AVAILABLE:
            try:
                enhanced = apply_reason_codes({
                    "score": credit_score,
                    "credit_score": credit_score,
                    "income": income
                })
                if enhanced.get("explanation", {}).get("top_positive_factors"):
                    for factor in enhanced["explanation"]["top_positive_factors"][:2]:
                        if factor.get("explanation") and factor["explanation"] not in reasons:
                            reasons.append(factor["explanation"])
            except Exception:
                pass  # Usar reasons básicos si el layer falla
        
        return reasons[:6]  # Máximo 6 reasons

    def _calculate_confidence(self, customer: Dict, tier: str, affordable: bool) -> float:
        """Calcula score de confianza de la decisión."""
        score = 0.5  # Base
        
        credit_score = customer.get("credit_score", 0)
        income = customer.get("income", 0)
        
        # Ajustes por credit score
        if credit_score >= 750:
            score += 0.20
        elif credit_score >= 700:
            score += 0.15
        elif credit_score >= 650:
            score += 0.10
        
        # Ajustes por income
        if income >= 80000:
            score += 0.15
        elif income >= 50000:
            score += 0.10
        
        # Ajustes por tier
        tier_bonus = {"platinum": 0.10, "gold": 0.08, "silver": 0.05, "bronze": 0.02}
        score += tier_bonus.get(tier, 0)
        
        # Affordability
        if affordable:
            score += 0.05
        
        return min(0.99, max(0.10, round(score, 2)))

    # ═══════════════════════════════════════════════════════════════════
    # RESPUESTAS
    # ═══════════════════════════════════════════════════════════════════
    
    def _rejection_response(self, customer_id: str, reason: str, trace: List[str], t0: float) -> Dict[str, Any]:
        """Construye respuesta de rechazo."""
        latency = int((time.perf_counter() - t0) * 1000)
        self.metrics["total_ms"] += latency
        
        return {
            "tenant_id": self.tenant_id,
            "customer_id": customer_id,
            "eligible": False,
            "ineligibility_reason": reason,
            "decision_trace": trace,
            "version": self.VERSION,
            "latency_ms": latency
        }

    def _error_response(self, error: str, t0: float) -> Dict[str, Any]:
        """Construye respuesta de error."""
        latency = int((time.perf_counter() - t0) * 1000)
        self.metrics["total_ms"] += latency
        
        return {
            "tenant_id": self.tenant_id,
            "status": "error",
            "error": error,
            "version": self.VERSION,
            "latency_ms": latency
        }

    # ═══════════════════════════════════════════════════════════════════
    # HEALTH & METRICS
    # ═══════════════════════════════════════════════════════════════════
    
    def health(self) -> Dict[str, Any]:
        """Health check del agente."""
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "status": "healthy",
            "tenant_id": self.tenant_id,
            "metrics": {
                "requests": self.metrics["requests"],
                "approvals": self.metrics["approvals"],
                "rejections": self.metrics["rejections"],
                "errors": self.metrics["errors"],
                "approval_rate": round(self.metrics["approvals"] / req, 4),
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2)
            },
            "reason_codes_layer": REASON_CODES_LAYER_AVAILABLE
        }

    def health_check(self) -> Dict[str, Any]:
        """Alias para compatibilidad."""
        return self.health()

    def get_metrics(self) -> Dict[str, Any]:
        """Métricas del agente."""
        return self.health()


# Factory para registry
def create_agent_instance(tenant_id: str, config: Dict = None):
    return CashOfferFilterIA(tenant_id, config)
