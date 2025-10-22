# filepath: agents/marketing/retentionpredictorea.py
"""
RetentionPredictorIA v3.3.0 - Enterprise Customer Retention Prediction Engine
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
READY FOR PRODUCTION âœ…

PredicciÃ³n avanzada de retenciÃ³n con:
- Circuit Breaker (OPEN/HALF_OPEN/CLOSED) y Fallback mode
- Cache LRU con TTL
- PII detection + masking (email/telÃ©fono/IDs)
- Scoring de churn (0-100) y clasificaciÃ³n de riesgo
- SeÃ±ales tempranas (early warning) y cohort segmentation
- Estrategias de intervenciÃ³n priorizadas (proactive/reactive/preventive/recovery)
- Audit trail (decision trace + eventos), logging estructurado
- Feature flags y mÃ©tricas avanzadas (latencia p95/p99, cache hit rate)

Author: Nadakki AI Suite
Version: 3.3.0
"""

# PRODUCTION READY - ENTERPRISE v3.2.0

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Logging estructurado
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
VERSION = "3.2.0"
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RetentionPredictorIA")

VERSION = "3.3.0"
MAX_CACHE_SIZE = 600
DEFAULT_TTL_SECONDS = 1800
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60

Language = Literal["es", "en", "pt"]
Jurisdiction = Literal["US", "MX", "BR", "CO", "EU", "DO", "AR", "CL", "PE", "UY", "PA", "CR", "EC", "VE"]

ChurnRisk = Literal["critical", "high", "medium", "low", "minimal"]
RetentionStage = Literal["onboarding", "active", "engaged", "at_risk", "churning"]
InterventionType = Literal["proactive", "reactive", "preventive", "recovery"]
Cohort = Literal["new_0_30d", "30_90d", "90_180d", "180_365d", "365d_plus"]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FEATURE FLAGS & CIRCUIT BREAKER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class FeatureFlags:
    """Manejo de flags para activar/desactivar capacidades del agente."""
    def __init__(self, initial: Optional[Dict[str, bool]] = None):
        self.flags: Dict[str, bool] = {
            "CACHE_ENABLED": True,
            "CIRCUIT_BREAKER": True,
            "FALLBACK_MODE": True,
            "ADVANCED_METRICS": True,
            "PII_DETECTION": True,
            "PREDICTIVE_SCORING": True,
            "AUDIT_TRAIL": True,
            "COHORT_SEGMENTATION": True,
        }
        if initial:
            self.flags.update(initial)

    def is_enabled(self, name: str) -> bool:
        return self.flags.get(name, False)

class CircuitBreaker:
    """Circuit breaker sencillo con estados CLOSED/HALF_OPEN/OPEN."""
    def __init__(self, failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD, timeout=CIRCUIT_BREAKER_TIMEOUT):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if (time.time() - (self.last_failure_time or 0.0)) > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self) -> None:
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = None

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PII UTILS (detecciÃ³n y enmascaramiento)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class PIIUtils:
    EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
    PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3}[\s-]?\d{4}\b")
    ID_RE = re.compile(r"\b(?:SSN|DNI|RFC|CUIT|CURP|NIF)[:\s-]*([A-Za-z0-9\-]{5,})\b", re.IGNORECASE)

    @staticmethod
    def mask_email(text: str) -> str:
        return PIIUtils.EMAIL_RE.sub(lambda m: f"{m.group(1)[:2]}***@***.{m.group(2).split('.')[-1]}", text)

    @staticmethod
    def mask_phone(text: str) -> str:
        def repl(m: re.Match) -> str:
            raw = re.sub(r"\D", "", m.group(0))
            if len(raw) < 4:
                return "***"
            return f"{'*' * (len(raw)-4)}{raw[-4:]}"
        return PIIUtils.PHONE_RE.sub(repl, text)

    @staticmethod
    def mask_ids(text: str) -> str:
        return PIIUtils.ID_RE.sub(lambda _: "ID:***", text)

    @staticmethod
    def scrub_text(text: Optional[str]) -> Tuple[Optional[str], bool]:
        if not text:
            return text, False
        original = text
        text = PIIUtils.mask_email(text)
        text = PIIUtils.mask_phone(text)
        text = PIIUtils.mask_ids(text)
        return text, text != original

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DATA MODELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@dataclass
class CustomerBehavior:
    customer_id: str
    days_since_signup: int
    days_since_last_login: int
    days_since_last_transaction: int
    total_transactions: int
    avg_transaction_value: float
    login_frequency_30d: int
    support_tickets_30d: int
    product_usage_score: float  # 0-10
    nps_score: Optional[int] = None  # -100 to 100
    email: Optional[str] = None
    language: Language = "es"
    jurisdiction: Jurisdiction = "MX"
    marketing_consent: bool = True  # consentimiento para comunicaciones

    def scrub(self, enable_pii: bool) -> Tuple["CustomerBehavior", bool]:
        """Devuelve copia con PII enmascarada y flag si hubo PII."""
        if not enable_pii:
            return self, False
        pii_found = False
        masked_email, flag = PIIUtils.scrub_text(self.email)
        pii_found = pii_found or flag
        clone = CustomerBehavior(**{**asdict(self), "email": masked_email})
        return clone, pii_found

@dataclass
class RetentionPredictionInput:
    tenant_id: str
    customers: List[CustomerBehavior]
    prediction_horizon_days: int = 30
    language: Language = "es"
    jurisdiction: Jurisdiction = "MX"
    request_id: Optional[str] = None

    def __post_init__(self):
        if not re.match(r"^tn_[a-z0-9_]{8,64}$", self.tenant_id):
            raise ValueError("Invalid tenant_id")
        if not self.customers:
            raise ValueError("At least one customer required")

@dataclass
class EarlyWarningSignal:
    signal_type: str
    severity: Literal["critical", "high", "medium", "low"]
    description: str

@dataclass
class InterventionStrategy:
    intervention_type: InterventionType
    priority: int  # 1-5
    action: str
    expected_impact: str
    estimated_cost: str

@dataclass
class CustomerRetentionPrediction:
    customer_id: str
    churn_risk: ChurnRisk
    churn_probability: float  # 0-100
    retention_stage: RetentionStage
    predicted_ltv_impact: float
    early_warning_signals: List[EarlyWarningSignal]
    intervention_strategies: List[InterventionStrategy]
    cohort: Cohort
    pii_detected: bool

@dataclass
class AuditEvent:
    ts: str
    step: str
    detail: Dict[str, Any]

@dataclass
class RetentionPredictionResult:
    prediction_id: str
    tenant_id: str
    predictions: List[CustomerRetentionPrediction]
    risk_distribution: Dict[ChurnRisk, int]
    high_risk_customers: List[str]
    retention_score: float  # 0-100 (overall health)
    recommended_budget_allocation: Dict[str, float]
    latency_ms: int
    metadata: Dict[str, Any]
    decision_trace: List[str] = field(default_factory=list)
    audit_trail: List[AuditEvent] = field(default_factory=list)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENGINES (Churn, Signals, Interventions, Cohorts)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class ChurnPredictionEngine:
    """Motor de predicciÃ³n de churn con scoring multi-factorial."""
    @staticmethod
    def calculate_churn_score(customer: CustomerBehavior, seed: str) -> float:
        score = 0.0

        # 1) Recencia de login (35%)
        if customer.days_since_last_login > 30:
            score += 35
        elif customer.days_since_last_login > 14:
            score += 25
        elif customer.days_since_last_login > 7:
            score += 15
        elif customer.days_since_last_login > 3:
            score += 5

        # 2) Recencia de transacciÃ³n (30%)
        if customer.days_since_last_transaction > 60:
            score += 30
        elif customer.days_since_last_transaction > 30:
            score += 20
        elif customer.days_since_last_transaction > 14:
            score += 10

        # 3) Frecuencia de uso (20%)
        if customer.login_frequency_30d == 0:
            score += 20
        elif customer.login_frequency_30d <= 2:
            score += 15
        elif customer.login_frequency_30d <= 5:
            score += 8

        # 4) Product usage (10%)
        usage_penalty = max(0.0, (5.0 - customer.product_usage_score) * 2.0)
        score += usage_penalty

        # 5) Tickets de soporte (5%)
        if customer.support_tickets_30d >= 3:
            score += 5
        elif customer.support_tickets_30d >= 2:
            score += 3

        # 6) NPS (bonus/penalty)
        if customer.nps_score is not None:
            if customer.nps_score < 0:
                score += 10
            elif customer.nps_score < 30:
                score += 5
            elif customer.nps_score >= 70:
                score -= 10

        # Variabilidad determinÃ­stica Â±1%
        hash_val = int(hashlib.sha256(f"{seed}_{customer.customer_id}".encode()).hexdigest()[:4], 16)
        variance = (hash_val % 20 - 10) / 10.0

        return round(max(0.0, min(100.0, score + variance)), 1)

    @staticmethod
    def classify_risk(churn_score: float) -> ChurnRisk:
        if churn_score >= 75.0:
            return "critical"
        if churn_score >= 50.0:
            return "high"
        if churn_score >= 30.0:
            return "medium"
        if churn_score >= 10.0:
            return "low"
        return "minimal"

    @staticmethod
    def determine_retention_stage(customer: CustomerBehavior, churn_score: float) -> RetentionStage:
        if customer.days_since_signup < 30:
            return "onboarding"
        if churn_score >= 60.0:
            return "churning"
        if churn_score >= 40.0:
            return "at_risk"
        if customer.product_usage_score >= 7.0 and customer.login_frequency_30d >= 10:
            return "engaged"
        return "active"

class WarningSignalsEngine:
    """Motor de detecciÃ³n de seÃ±ales tempranas de churn."""
    @staticmethod
    def detect_signals(customer: CustomerBehavior) -> List[EarlyWarningSignal]:
        signals: List[EarlyWarningSignal] = []
        # Inactividad
        if customer.days_since_last_login > 21:
            signals.append(EarlyWarningSignal("prolonged_inactivity", "critical", f"No login en {customer.days_since_last_login} dÃ­as"))
        elif customer.days_since_last_login > 14:
            signals.append(EarlyWarningSignal("declining_activity", "high", f"Login inactivo por {customer.days_since_last_login} dÃ­as"))

        # Bajo uso
        if customer.product_usage_score < 3.0:
            signals.append(EarlyWarningSignal("low_product_adoption", "high", f"Uso muy bajo: {customer.product_usage_score}/10"))

        # Tickets
        if customer.support_tickets_30d >= 3:
            signals.append(EarlyWarningSignal("support_friction", "medium", f"{customer.support_tickets_30d} tickets en 30d - posible fricciÃ³n"))

        # Transacciones
        if customer.days_since_last_transaction > 45:
            signals.append(EarlyWarningSignal("transaction_lapse", "medium", f"Sin transacciones por {customer.days_since_last_transaction} dÃ­as"))

        # NPS
        if customer.nps_score is not None and customer.nps_score < 0:
            signals.append(EarlyWarningSignal("detractor_nps", "critical", f"NPS negativo: {customer.nps_score}"))

        return signals

class InterventionEngine:
    """Motor de estrategias de intervenciÃ³n personalizadas."""
    @staticmethod
    def generate_strategies(customer: CustomerBehavior, churn_risk: ChurnRisk, stage: RetentionStage) -> List[InterventionStrategy]:
        strategies: List[InterventionStrategy] = []

        # Por riesgo
        if churn_risk in {"critical", "high"}:
            strategies.append(InterventionStrategy("reactive", 1, "Llamada 1:1 por Account Manager", "RetenciÃ³n +40-60%", "Alto"))
            strategies.append(InterventionStrategy("recovery", 2, "Oferta personalizada (descuento/upgrade)", "RetenciÃ³n +30%", "Medio-Alto"))
        elif churn_risk == "medium":
            strategies.append(InterventionStrategy("preventive", 2, "Programa de re-engagement automatizado", "Churn -20%", "Bajo"))
            strategies.append(InterventionStrategy("proactive", 3, "Webinar/training de features clave", "AdopciÃ³n +25%", "Medio"))
        else:
            strategies.append(InterventionStrategy("proactive", 4, "Nurturing con best practices mensual", "Mantener engagement", "Bajo"))

        # Por etapa
        if stage == "onboarding":
            strategies.insert(0, InterventionStrategy("proactive", 1, "Onboarding guiado + check-in dÃ­a 7", "Early churn -50%", "Bajo"))

        return strategies[:3]

class CohortEngine:
    """Cohortes basadas en dÃ­as desde signup."""
    @staticmethod
    def assign_cohort(days_since_signup: int) -> Cohort:
        if days_since_signup < 30:
            return "new_0_30d"
        if days_since_signup < 90:
            return "30_90d"
        if days_since_signup < 180:
            return "90_180d"
        if days_since_signup < 365:
            return "180_365d"
        return "365d_plus"

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAIN AGENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class RetentionPredictorIA:
    """Agente principal de predicciÃ³n de retenciÃ³n de clientes."""
    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None, flags: Optional[Dict[str, bool]] = None):
        self.tenant_id = tenant_id
        self.agent_id = "retention_predictor_ia"
        self.version = VERSION
        self.config = config or {"enable_cache": True, "cache_ttl_seconds": DEFAULT_TTL_SECONDS}
        self.flags = FeatureFlags(flags)
        self.breaker = CircuitBreaker()

        self._cache: "OrderedDict[str, Tuple[RetentionPredictionResult, float]]" = OrderedDict()
        self._cache_max_size = MAX_CACHE_SIZE

        self._metrics: Dict[str, Any] = {
            "total": 0,
            "ok": 0,
            "fail": 0,
            "cache_hits": 0,
            "fallbacks": 0,
            "breaker_trips": 0,
            "critical_risk_detected": 0,
            "pii_detections": 0,
            "avg_latency_ms": 0.0,
            "latency_hist": [],  # List[int]
        }

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Utils: logs, mÃ©tricas, percentiles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _emit_log(self, level: int, msg: str, **extra: Any) -> None:
        logger.log(level, msg + " " + json.dumps(extra, default=str))

    @staticmethod
    def _percentile(sorted_values: List[int], p: float) -> float:
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * p
        f = int(k)
        c = min(f + 1, len(sorted_values) - 1)
        if f == c:
            return float(sorted_values[f])
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return float(d0 + d1)

    def _update_latency(self, ms: int) -> None:
        self._metrics["latency_hist"].append(ms)
        n = max(1, self._metrics["total"])
        self._metrics["avg_latency_ms"] = ((self._metrics["avg_latency_ms"] * (n - 1)) + ms) / n

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Cache helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _cache_key(self, inp: RetentionPredictionInput) -> str:
        ids = sorted([c.customer_id for c in inp.customers[:50]])
        s = json.dumps(
            {"tenant": inp.tenant_id, "count": len(inp.customers), "sample": ids[:5], "jurisdiction": inp.jurisdiction},
            sort_keys=True,
        )
        return hashlib.sha256(s.encode()).hexdigest()[:16]

    def _get_from_cache(self, key: str) -> Optional[RetentionPredictionResult]:
        if not self.flags.is_enabled("CACHE_ENABLED"):
            return None
        item = self._cache.get(key)
        if not item:
            return None
        result, ts = item
        ttl = self.config.get("cache_ttl_seconds", 0)
        if ttl and (time.time() - ts) > ttl:
            self._cache.pop(key, None)
            return None
        self._cache.move_to_end(key)
        self._metrics["cache_hits"] += 1
        return result

    def _put_in_cache(self, key: str, result: RetentionPredictionResult) -> None:
        if not self.flags.is_enabled("CACHE_ENABLED"):
            return
        self._cache[key] = (result, time.time())
        if len(self._cache) > self._cache_max_size:
            self._cache.popitem(last=False)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Core â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _execute_core(self, inp: RetentionPredictionInput) -> RetentionPredictionResult:
        t0 = time.perf_counter()
        seed = f"{inp.tenant_id}|{len(inp.customers)}"

        decision_trace: List[str] = []
        audit: List[AuditEvent] = []
        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="start", detail={"customers": len(inp.customers)}))

        # Scrubbing PII
        customers: List[CustomerBehavior] = []
        for c in inp.customers:
            cc, pii_found = c.scrub(enable_pii=self.flags.is_enabled("PII_DETECTION"))
            if pii_found:
                self._metrics["pii_detections"] += 1
                if self.flags.is_enabled("AUDIT_TRAIL"):
                    audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="pii_mask", detail={"customer_id": c.customer_id}))
            customers.append(cc)

        predictions: List[CustomerRetentionPrediction] = []
        risk_counts: Dict[ChurnRisk, int] = {}
        high_risk_ids: List[str] = []
        cohorts: Dict[Cohort, int] = {}

        for customer in customers:
            churn_score = ChurnPredictionEngine.calculate_churn_score(customer, seed) if self.flags.is_enabled("PREDICTIVE_SCORING") else 50.0
            churn_risk = ChurnPredictionEngine.classify_risk(churn_score)
            stage = ChurnPredictionEngine.determine_retention_stage(customer, churn_score)

            risk_counts[churn_risk] = risk_counts.get(churn_risk, 0) + 1
            if churn_risk in {"critical", "high"}:
                high_risk_ids.append(customer.customer_id)
                self._metrics["critical_risk_detected"] += 1

            signals = WarningSignalsEngine.detect_signals(customer)
            strategies = InterventionEngine.generate_strategies(customer, churn_risk, stage)

            # Cohort
            cohort = CohortEngine.assign_cohort(customer.days_since_signup) if self.flags.is_enabled("COHORT_SEGMENTATION") else "new_0_30d"
            cohorts[cohort] = cohorts.get(cohort, 0) + 1

            # LTV impact (simplificado)
            base_ltv = max(0.0, customer.total_transactions * customer.avg_transaction_value)
            ltv_at_risk = base_ltv * (churn_score / 100.0)

            predictions.append(
                CustomerRetentionPrediction(
                    customer_id=customer.customer_id,
                    churn_risk=churn_risk,
                    churn_probability=round(churn_score, 1),
                    retention_stage=stage,
                    predicted_ltv_impact=round(ltv_at_risk, 2),
                    early_warning_signals=signals,
                    intervention_strategies=strategies,
                    cohort=cohort,
                    pii_detected=bool(customer.email),
                )
            )

        decision_trace.append(f"high_risk={len(high_risk_ids)}")
        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="scored", detail={"predictions": len(predictions), "cohorts": cohorts}))

        # Overall retention score (inverso de churn promedio)
        avg_churn = sum(p.churn_probability for p in predictions) / max(1, len(predictions))
        retention_score = round(100.0 - avg_churn, 1)

        # Budget allocation (heurÃ­stica simple dependiente del mix de riesgo)
        total = len(predictions) or 1
        critical_high = sum(1 for p in predictions if p.churn_risk in {"critical", "high"})
        medium = sum(1 for p in predictions if p.churn_risk == "medium")
        low_min = total - critical_high - medium

        budget_alloc = {
            "critical_interventions": round(0.5 * critical_high, 2),
            "preventive_programs": round(0.3 * medium, 2),
            "engagement_programs": round(0.2 * low_min, 2),
        }

        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        self._update_latency(latency_ms)
        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="finish", detail={"latency_ms": latency_ms}))

        prediction_id = f"ret_{int(datetime.utcnow().timestamp()*1000)}_{hashlib.sha256(seed.encode()).hexdigest()[:6]}"
        self._emit_log(logging.INFO, "Retention prediction computed", prediction_id=prediction_id, latency_ms=latency_ms, size=len(predictions))

        return RetentionPredictionResult(
            prediction_id=prediction_id,
            tenant_id=self.tenant_id,
            predictions=predictions,
            risk_distribution=risk_counts,
            high_risk_customers=high_risk_ids,
            retention_score=retention_score,
            recommended_budget_allocation=budget_alloc,
            latency_ms=latency_ms,
            metadata={
                "agent_version": VERSION,
                "request_id": inp.request_id,
                "customers_analyzed": len(predictions),
                "jurisdiction": inp.jurisdiction,
                "language": inp.language,
                "cohorts": cohorts,
            },
            decision_trace=decision_trace,
            audit_trail=audit if self.flags.is_enabled("AUDIT_TRAIL") else [],
        )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    async def execute(self, inp: RetentionPredictionInput) -> RetentionPredictionResult:
        """Ejecuta la predicciÃ³n principal con circuit breaker + cache + fallback."""
        self._metrics["total"] += 1

        # Circuit Breaker
        if self.flags.is_enabled("CIRCUIT_BREAKER") and not self.breaker.can_execute():
            self._metrics["breaker_trips"] += 1
            self._emit_log(logging.WARNING, "Circuit breaker OPEN - using fallback", breaker_state=self.breaker.state)
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise RuntimeError("Circuit breaker OPEN")

        # Tenant check
        if not inp.tenant_id or not inp.tenant_id.startswith("tn_"):
            self.breaker.record_failure()
            self._metrics["fail"] += 1
            raise ValueError("Tenant mismatch or invalid")

        # Cache
        key = self._cache_key(inp)
        cached = self._get_from_cache(key)
        if cached:
            return cached

        try:
            result = self._execute_core(inp)
            self.breaker.record_success()
            self._metrics["ok"] += 1
            self._put_in_cache(key, result)
            return result
        except Exception as e:
            self._emit_log(logging.ERROR, "RetentionPredictorIA failed", error=str(e))
            self.breaker.record_failure()
            self._metrics["fail"] += 1
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise

    def _fallback(self, inp: RetentionPredictionInput) -> RetentionPredictionResult:
        """Respuesta conservadora y segura."""
        prediction_id = f"fallback_{int(datetime.utcnow().timestamp())}"
        self._emit_log(logging.WARNING, "Returning fallback result", prediction_id=prediction_id)
        return RetentionPredictionResult(
            prediction_id=prediction_id,
            tenant_id=self.tenant_id,
            predictions=[],
            risk_distribution={},
            high_risk_customers=[],
            retention_score=50.0,
            recommended_budget_allocation={},
            latency_ms=1,
            metadata={"fallback": True, "agent_version": VERSION, "request_id": inp.request_id},
            decision_trace=["fallback_mode"],
            audit_trail=[],
        )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Health & Metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "agent_id": self.agent_id,
            "version": VERSION,
            "tenant_id": self.tenant_id,
            "total_requests": self._metrics["total"],
            "success_rate": round(self._metrics["ok"] / max(1, self._metrics["total"]), 3),
            "breaker_state": self.breaker.state,
        }

    def get_metrics(self) -> Dict[str, Any]:
        hist: List[int] = self._metrics.get("latency_hist", [])
        hist_sorted = sorted(hist)
        p95 = self._percentile(hist_sorted, 0.95)
        p99 = self._percentile(hist_sorted, 0.99)
        cache_hit_rate = round(self._metrics["cache_hits"] / max(1, self._metrics["total"]), 3)

        return {
            "agent_name": self.agent_id,
            "agent_version": VERSION,
            "tenant_id": self.tenant_id,
            **self._metrics,
            "latency_p95_ms": round(p95, 2),
            "latency_p99_ms": round(p99, 2),
            "cache_hit_rate": cache_hit_rate,
        }

# Factory
def create_agent_instance(tenant_id: str, config: Optional[Dict[str, Any]] = None, flags: Optional[Dict[str, bool]] = None) -> RetentionPredictorIA:
    """
    Crea una instancia del agente con configuraciÃ³n/flags opcionales.
    """
    return RetentionPredictorIA(tenant_id, config, flags)

