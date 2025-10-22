"""
CashOfferFilterIA - Production-Ready v2.1.0

PropÃ³sito:
  Calcular ofertas de efectivo (monto/term/APR) con lÃ­mites de riesgo, affordability,
  cumplimiento legal y trazabilidad (reason_codes).

Mejoras:
  - validate_request() + reason_codes
  - health_check(), mÃ©tricas ampliadas
  - APR legal cap + affordability DTI/LTI
  - Variantes (conservative/balanced/aggressive) deterministas y claras
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CashOfferFilterIA:
    VERSION = "v2.1.0"

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.tenant_id = tenant_id
        self.name = "CashOfferFilterIA"
        self.config = config or self._default_config()
        logger.info("CashOfferFilterIA init tenant=%s version=%s", tenant_id, self.VERSION)

    # ------------------------- Config ----------------------------------------
    def _default_config(self) -> Dict[str, Any]:
        return {
            "offer_tiers": self._default_offer_tiers(),
            "risk_limits": {"max_loan_to_income_ratio": 0.40, "max_debt_to_income_ratio": 0.50, "min_credit_score": 600, "max_loan_amount": 50000},
            "pricing_matrix": self._default_pricing_matrix(),
            "compliance": {"require_apr_disclosure": True, "fair_lending_check": True, "affordability_check": True, "max_apr": 35.99}
        }

    def _default_offer_tiers(self) -> Dict[str, Dict[str, Any]]:
        return {
            "platinum": {"credit_score_min": 750, "income_min": 60000, "max_amount": 50000, "base_apr": 8.99, "terms_months": [12, 24, 36, 48, 60]},
            "gold": {"credit_score_min": 700, "income_min": 40000, "max_amount": 30000, "base_apr": 12.99, "terms_months": [12, 24, 36, 48]},
            "silver": {"credit_score_min": 650, "income_min": 30000, "max_amount": 15000, "base_apr": 18.99, "terms_months": [12, 24, 36]},
            "bronze": {"credit_score_min": 600, "income_min": 20000, "max_amount": 7500, "base_apr": 24.99, "terms_months": [12, 24]}
        }

    def _default_pricing_matrix(self) -> Dict[int, float]:
        return {12: 0.0, 24: 0.5, 36: 1.0, 48: 1.5, 60: 2.0}

    # -------------------- Validaciones & helpers ------------------------------
    def validate_request(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return "invalid_input: payload must be object"
        if not data.get("customer_id"):
            return "invalid_input: customer_id required"
        c = data.get("customer")
        if not isinstance(c, dict):
            return "invalid_input: customer must be object"
        if "credit_score" not in c or "income" not in c:
            return "invalid_input: customer.credit_score and customer.income are required"
        return None

    def _determine_tier(self, customer: Dict[str, Any]) -> Optional[str]:
        cs = customer.get("credit_score", 0)
        inc = customer.get("income", 0)
        t = self.config["offer_tiers"]
        for name in ["platinum", "gold", "silver", "bronze"]:
            cfg = t[name]
            if cs >= cfg["credit_score_min"] and inc >= cfg["income_min"]:
                return name
        return None

    def _calculate_max_offer_amount(self, customer: Dict[str, Any], tier: str) -> Decimal:
        tier_cfg = self.config["offer_tiers"][tier]
        risk = self.config["risk_limits"]
        income = Decimal(str(customer.get("income", 0)))
        existing_debt = Decimal(str(customer.get("existing_debt", 0)))
        tier_max = Decimal(str(tier_cfg["max_amount"]))
        lti_max = income * Decimal(str(risk["max_loan_to_income_ratio"]))
        max_dti = Decimal(str(risk["max_debt_to_income_ratio"]))
        dti_max = (max_dti * income) - existing_debt
        if dti_max < 0:
            dti_max = Decimal("0")
        global_max = Decimal(str(risk["max_loan_amount"]))
        max_amount = min(tier_max, lti_max, dti_max, global_max)
        return max_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_apr(self, tier: str, term_months: int, credit_score: int) -> Decimal:
        tier_cfg = self.config["offer_tiers"][tier]
        base = Decimal(str(tier_cfg["base_apr"]))
        adj_term = Decimal(str(self.config["pricing_matrix"].get(term_months, 0)))
        score_adj = Decimal("1.0") if credit_score < tier_cfg["credit_score_min"] + 30 else Decimal("0.0")
        apr = base + adj_term + score_adj
        apr = min(apr, Decimal(str(self.config["compliance"]["max_apr"])))
        return apr.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_monthly_payment(self, amount: Decimal, apr: Decimal, term_months: int) -> Decimal:
        if amount <= 0:
            return Decimal("0.00")
        monthly_rate = (apr / Decimal("100")) / Decimal("12")
        if monthly_rate == 0:
            return (amount / Decimal(str(term_months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        num = monthly_rate * ((Decimal("1") + monthly_rate) ** term_months)
        den = ((Decimal("1") + monthly_rate) ** term_months) - Decimal("1")
        pay = amount * (num / den)
        return pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _affordability_check(self, monthly_payment: Decimal, income: Decimal, existing_payment: Decimal) -> Tuple[bool, Optional[str]]:
        monthly_income = income / Decimal("12")
        total_monthly_debt = monthly_payment + existing_payment
        if monthly_income <= 0:
            return False, "no_income"
        dti = total_monthly_debt / monthly_income
        max_dti = Decimal(str(self.config["risk_limits"]["max_debt_to_income_ratio"]))
        if dti > max_dti:
            return False, f"dti_too_high_{float(dti):.2f}"
        return True, None

    def _compliance_check(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if self.config["compliance"]["require_apr_disclosure"] and "apr" not in offer:
            issues.append("missing_apr_disclosure")
        apr = float(offer.get("apr", 0.0))
        if apr > float(self.config["compliance"]["max_apr"]):
            issues.append("apr_exceeds_legal_max")
        return {"status": "fail" if issues else "pass", "issues": issues}

    def _generate_variants(self, base_amount: Decimal, tier: str, credit_score: int) -> List[Dict[str, Any]]:
        terms = self.config["offer_tiers"][tier]["terms_months"]
        variants: List[Dict[str, Any]] = []
        # Conservative
        a1 = (base_amount * Decimal("0.70")).quantize(Decimal("0.01"))
        t1 = terms[0]
        apr1 = self._calculate_apr(tier, t1, credit_score)
        mp1 = self._calculate_monthly_payment(a1, apr1, t1)
        variants.append({"variant": "conservative", "amount": float(a1), "term_months": t1, "apr": float(apr1), "monthly_payment": float(mp1), "total_cost": float(mp1 * t1)})
        # Balanced
        idx = len(terms) // 2 if len(terms) > 1 else 0
        t2 = terms[idx]
        apr2 = self._calculate_apr(tier, t2, credit_score)
        mp2 = self._calculate_monthly_payment(base_amount, apr2, t2)
        variants.append({"variant": "balanced", "amount": float(base_amount), "term_months": t2, "apr": float(apr2), "monthly_payment": float(mp2), "total_cost": float(mp2 * t2)})
        # Aggressive
        t3 = terms[-1]
        apr3 = self._calculate_apr(tier, t3, credit_score)
        mp3 = self._calculate_monthly_payment(base_amount, apr3, t3)
        variants.append({"variant": "aggressive", "amount": float(base_amount), "term_months": t3, "apr": float(apr3), "monthly_payment": float(mp3), "total_cost": float(mp3 * t3)})
        return variants

    # ------------------------------- API -------------------------------------
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()
        err = self.validate_request(data)
        if err:
            return self._error_response(err, int((time.perf_counter() - t0) * 1000))

        decision_trace: List[str] = []
        customer_id = data["customer_id"]
        c = data["customer"]
        requested_amount = data.get("requested_amount")
        cs = c.get("credit_score", 0)
        if cs < self.config["risk_limits"]["min_credit_score"]:
            latency = int((time.perf_counter() - t0) * 1000)
            return {"tenant_id": self.tenant_id, "customer_id": customer_id, "eligible": False, "ineligibility_reason": f"credit_score_below_minimum_{cs}", "decision_trace": ["rejected_low_credit_score"], "version": self.VERSION, "latency_ms": latency}

        tier = self._determine_tier(c)
        if not tier:
            latency = int((time.perf_counter() - t0) * 1000)
            return {"tenant_id": self.tenant_id, "customer_id": customer_id, "eligible": False, "ineligibility_reason": "no_qualifying_tier", "decision_trace": ["no_tier_match"], "version": self.VERSION, "latency_ms": latency}

        decision_trace.append(f"tier={tier}")
        max_offer = self._calculate_max_offer_amount(c, tier)
        if max_offer <= 0:
            latency = int((time.perf_counter() - t0) * 1000)
            return {"tenant_id": self.tenant_id, "customer_id": customer_id, "eligible": False, "ineligibility_reason": "max_offer_zero_due_to_debt", "decision_trace": decision_trace + ["max_offer=0"], "version": self.VERSION, "latency_ms": latency}

        base_amount = max_offer if (requested_amount and Decimal(str(requested_amount)) > max_offer) else (Decimal(str(requested_amount)) if requested_amount else (max_offer * Decimal("0.80")))
        variants = self._generate_variants(base_amount, tier, cs)
        primary = next(v for v in variants if v["variant"] == "balanced")

        income = Decimal(str(c.get("income", 0)))
        existing_payment = Decimal(str(c.get("existing_debt_monthly_payment", 0)))
        affordable, why = self._affordability_check(Decimal(str(primary["monthly_payment"])), income, existing_payment)
        decision_trace.append(f"affordable={affordable}")
        if not affordable and self.config["compliance"]["affordability_check"]:
            latency = int((time.perf_counter() - t0) * 1000)
            return {"tenant_id": self.tenant_id, "customer_id": customer_id, "eligible": False, "ineligibility_reason": why, "decision_trace": decision_trace, "version": self.VERSION, "latency_ms": latency}

        compliance = self._compliance_check(primary)
        decision_trace.append(f"compliance={compliance['status']}")

        risk = {
            "tier": tier,
            "max_offer_amount": float(max_offer),
            "loan_to_income_ratio": float(base_amount / income) if income > 0 else 0.0,
            "debt_to_income_ratio": float(((Decimal(str(primary["monthly_payment"])) + existing_payment) * 12) / income) if income > 0 else 0.0,
            "risk_level": "low" if tier in ["platinum", "gold"] else ("medium" if tier == "silver" else "high")
        }

        latency = int((time.perf_counter() - t0) * 1000)
        out = {"tenant_id": self.tenant_id, "customer_id": customer_id, "eligible": True, "tier": tier, "primary_offer": primary, "alternative_offers": [v for v in variants if v["variant"] != "balanced"], "compliance": compliance, "risk_assessment": risk, "decision_trace": decision_trace, "version": self.VERSION, "latency_ms": latency}
        logger.info("cash_offer result tenant=%s customer=%s tier=%s amount=%.2f apr=%.2f latency=%dms", self.tenant_id, customer_id, tier, primary["amount"], primary["apr"], latency)
        return out

    # ----------------------- Health & MÃ©tricas --------------------------------
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "version": self.VERSION, "tenant_id": self.tenant_id}

    def get_metrics(self) -> Dict[str, Any]:
        return {"agent_name": self.name, "agent_version": self.VERSION, "tenant_id": self.tenant_id, "tiers_available": len(self.config["offer_tiers"]), "status": "healthy"}

    def _error_response(self, error: str, latency_ms: int) -> Dict[str, Any]:
        return {"tenant_id": self.tenant_id, "status": "error", "error": error, "latency_ms": latency_ms, "version": self.VERSION}
