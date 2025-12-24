# filepath: agents/marketing/leadscoringia.py
"""
LeadScoringIA v3.0 — Enterprise Grade (Composición sin Duplicación)

Arquitectura:
- Un solo agente, un solo contrato
- Reason Codes como post-processing opcional (composición)
- Acepta dict O Lead (máxima compatibilidad)
- Schema canónico estricto (reasons, latency_ms)

Contrato: leads.v3.0
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import os
import time
import random
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from schemas.canonical import Lead, LeadScoringOutput, LeadAttributes, ContactInfo

# ─────────────────────────────────────────────────────────────
# LAYER OPCIONAL: Reason Codes (composición, no dependencia)
# ─────────────────────────────────────────────────────────────
try:
    from agents.marketing.layers.reason_codes_layer import apply_reason_codes
    REASON_CODES_LAYER_AVAILABLE = True
except ImportError:
    REASON_CODES_LAYER_AVAILABLE = False

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "income": 0.30,
    "credit_score": 0.35,
    "channel": 0.20,
    "engagement": 0.15
}

CHANNEL_SCORES = {
    "referral": 1.0,
    "search": 0.85,
    "landing_form": 0.70,
    "web": 0.70,
    "social": 0.55,
    "email": 0.75,
    "display": 0.40,
    "partner": 0.80
}

BUCKET_THRESHOLDS = {"A": 0.80, "B": 0.60, "C": 0.40}
BUCKET_ACTIONS = {"A": "assign_to_sales", "B": "assign_to_sales", "C": "nurture", "D": "reject"}


# ─────────────────────────────────────────────────────────────
# Infraestructura (minimal, sin over-engineering)
# ─────────────────────────────────────────────────────────────

class TokenBucket:
    """Rate limiter simple."""
    def __init__(self, rate: int = 100, capacity: int = 200):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()

    def consume(self) -> bool:
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_update) * self.rate)
        self.last_update = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class LRUCache:
    """Cache LRU con TTL."""
    def __init__(self, capacity: int = 1000, ttl: int = 300):
        self.store: OrderedDict = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        item = self.store.pop(key, None)
        if not item:
            self.misses += 1
            return None
        value, ts = item
        if time.time() - ts > self.ttl:
            self.misses += 1
            return None
        self.store[key] = (value, ts)
        self.hits += 1
        return value

    def put(self, key: str, value: Any):
        self.store.pop(key, None)
        if len(self.store) >= self.capacity:
            self.store.popitem(last=False)
        self.store[key] = (value, time.time())

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses, "hit_rate": round(self.hits / total, 4) if total else 0.0}


class CircuitBreaker:
    """Circuit breaker para resiliencia."""
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = 0.0
        self.state = "CLOSED"

    def execute(self, fn, *args, **kwargs):
        now = time.time()
        if self.state == "OPEN" and now - self.last_failure < self.timeout:
            raise RuntimeError("circuit_breaker_open")
        try:
            result = fn(*args, **kwargs)
            self.failures = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = now
            if self.failures >= self.threshold:
                self.state = "OPEN"
            raise


# ─────────────────────────────────────────────────────────────
# AGENTE PRINCIPAL
# ─────────────────────────────────────────────────────────────

class LeadScoringIA:
    """
    Agente de Lead Scoring Enterprise.
    
    Responsabilidades:
    1. Recibir input (dict o Lead)
    2. Calcular score
    3. Generar reasons (básicas o enhanced via layer)
    4. Devolver LeadScoringOutput canónico
    """
    
    AGENT_ID = "leadscoringia"
    VERSION = "3.0.0"
    CONTRACT = "leads.v3.0"

    def __init__(
        self,
        tenant_id: str,
        config: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True,
        enable_rate_limit: bool = True,
        enable_reason_codes_layer: bool = True
    ):
        self.tenant_id = tenant_id
        self.config = config or {}
        
        # Configuración de scoring
        self.weights = self.config.get("weights", DEFAULT_WEIGHTS)
        self.channel_scores = self.config.get("channel_scores", CHANNEL_SCORES)
        self.thresholds = self.config.get("thresholds", BUCKET_THRESHOLDS)
        
        # Infraestructura opcional
        self.cache = LRUCache() if enable_cache else None
        self.cache_secret = os.urandom(16).hex()
        self.rate_limiter = TokenBucket() if enable_rate_limit else None
        self.circuit_breaker = CircuitBreaker()
        
        # Flag para usar Reason Codes Layer
        self.use_reason_codes_layer = enable_reason_codes_layer and REASON_CODES_LAYER_AVAILABLE
        
        # Métricas
        self.metrics = {"requests": 0, "errors": 0, "total_ms": 0.0, "layer_hits": 0}

    # ─────────────────────────────────────────────────────────
    # INPUT HANDLING
    # ─────────────────────────────────────────────────────────
    
    def _to_lead(self, input_data: Union[Lead, Dict]) -> Lead:
        """Convierte input a Lead. Acepta dict o Lead."""
        if isinstance(input_data, Lead):
            return input_data
        
        # Es dict - extraer datos
        data = input_data.get("lead", input_data)
        
        # Lead ID válido
        lead_id = str(data.get("lead_id", ""))
        if not lead_id.startswith("L-"):
            lead_id = f"L-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999):04d}"
        
        # Attributes
        attrs = data.get("attributes", {})
        if not attrs:
            attrs = {k: data.get(k) for k in ["income", "credit_score", "channel", "age", "industry"] if data.get(k) is not None}
        attrs.setdefault("channel", "landing_form")
        
        # Contact
        contact = data.get("contact", {})
        email = contact.get("email") or data.get("email", "unknown@example.com")
        phone = contact.get("phone") or data.get("phone", "+1-000-000-0000")
        
        return Lead(
            tenant_id=data.get("tenant_id", self.tenant_id),
            lead_id=lead_id,
            persona=data.get("persona", {"segment": "unknown", "country": "DO", "region": "latam"}),
            attributes=LeadAttributes(**{k: v for k, v in attrs.items() if k in ["age", "income", "credit_score", "industry", "channel"]}),
            contact=ContactInfo(email=email, phone=phone),
            events=data.get("events", [])
        )

    # ─────────────────────────────────────────────────────────
    # SCORING CORE
    # ─────────────────────────────────────────────────────────
    
    def _normalize(self, value: float, min_v: float, max_v: float) -> float:
        """Normaliza valor a [0,1]."""
        if max_v == min_v:
            return 0.5
        return max(0.0, min(1.0, (value - min_v) / (max_v - min_v)))

    def _calculate_score(self, lead: Lead) -> Dict[str, Any]:
        """Calcula score y componentes."""
        attrs = lead.attributes
        
        # Extraer valores
        income = float(getattr(attrs, "income", 0) or 0)
        credit = float(getattr(attrs, "credit_score", 0) or 0)
        channel = str(getattr(attrs, "channel", "landing_form")).lower()
        
        # Normalizar
        income_n = self._normalize(income, 0, 200000)
        credit_n = self._normalize(credit, 300, 850)
        channel_n = self.channel_scores.get(channel, 0.5)
        engagement_n = 0.0  # Sin eventos = 0
        
        # Score ponderado
        w = self.weights
        score = (
            income_n * w["income"] +
            credit_n * w["credit_score"] +
            channel_n * w["channel"] +
            engagement_n * w["engagement"]
        )
        
        # Bucket y acción
        bucket = "A" if score >= self.thresholds["A"] else \
                 "B" if score >= self.thresholds["B"] else \
                 "C" if score >= self.thresholds["C"] else "D"
        
        # Reasons básicas (sin layer)
        reasons = []
        if credit_n >= 0.8:
            reasons.append("high_credit_score")
        if income_n >= 0.7:
            reasons.append("good_income")
        if channel_n >= 0.8:
            reasons.append("quality_channel")
        if score < 0.4:
            reasons.append("low_overall_score")
        if not reasons:
            reasons.append("standard_scoring")
        
        return {
            "lead_id": lead.lead_id,
            "score": round(score, 3),
            "bucket": bucket,
            "recommended_action": BUCKET_ACTIONS[bucket],
            "reasons": reasons,
            "factors": {
                "income": income,
                "credit_score": credit,
                "channel": channel,
                "income_normalized": round(income_n, 4),
                "credit_normalized": round(credit_n, 4),
                "channel_score": round(channel_n, 4)
            }
        }

    def _enhance_with_layer(self, result: Dict[str, Any]) -> List[str]:
        """Aplica Reason Codes Layer si está disponible."""
        if not self.use_reason_codes_layer:
            return result["reasons"]
        
        try:
            # Preparar input para el layer
            layer_input = {
                "score": result["score"] * 100,  # Layer espera 0-100
                "credit_score": result["factors"]["credit_score"],
                "income": result["factors"]["income"]
            }
            
            enhanced = apply_reason_codes(layer_input)
            
            if enhanced.get("explanation", {}).get("reason_codes"):
                self.metrics["layer_hits"] += 1
                # Extraer explanations de los reason codes
                return [
                    rc.get("explanation", rc.get("factor", "unknown"))
                    for rc in enhanced["explanation"]["reason_codes"][:5]
                ]
        except Exception as e:
            logger.warning(f"Reason codes layer failed: {e}")
        
        return result["reasons"]

    # ─────────────────────────────────────────────────────────
    # API PÚBLICA
    # ─────────────────────────────────────────────────────────

    async def execute(self, input_data: Union[Lead, Dict]) -> LeadScoringOutput:
        """
        Ejecuta scoring para un lead.
        
        Args:
            input_data: Lead object o dict con datos del lead
            
        Returns:
            LeadScoringOutput canónico
        """
        self.metrics["requests"] += 1
        t0 = time.perf_counter()
        
        try:
            # 1. Convertir input
            lead = self._to_lead(input_data)
            
            # 2. Rate limit
            if self.rate_limiter and not self.rate_limiter.consume():
                raise RuntimeError("rate_limit_exceeded")
            
            # 3. Tenant check
            if lead.tenant_id != self.tenant_id:
                raise PermissionError(f"tenant_mismatch: {lead.tenant_id} != {self.tenant_id}")
            
            # 4. Cache check
            cache_key = hmac.new(
                self.cache_secret.encode(),
                lead.lead_id.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            cached = self.cache.get(cache_key) if self.cache else None
            
            if cached:
                result = cached
            else:
                # 5. Score (con circuit breaker)
                result = self.circuit_breaker.execute(self._calculate_score, lead)
                if self.cache:
                    self.cache.put(cache_key, result)
            
            # 6. Enhance reasons (composición)
            enhanced_reasons = self._enhance_with_layer(result)
            
            # 7. Build output
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            return LeadScoringOutput.model_validate({
                "lead_id": result["lead_id"],
                "score": result["score"],
                "bucket": result["bucket"],
                "reasons": enhanced_reasons,
                "recommended_action": result["recommended_action"],
                "latency_ms": latency_ms,
                "tenant_id": self.tenant_id
            })
            
        except Exception as e:
            self.metrics["errors"] += 1
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            self.metrics["total_ms"] += latency_ms
            
            logger.exception(f"leadscoringia error: {e}")
            
            return LeadScoringOutput.model_validate({
                "lead_id": "L-00000000-0000",
                "score": 0.0,
                "bucket": "D",
                "reasons": [f"error: {str(e)[:50]}"],
                "recommended_action": "reject",
                "latency_ms": latency_ms,
                "tenant_id": self.tenant_id
            })

    async def execute_batch(self, leads: List[Union[Lead, Dict]], max_concurrent: int = 10) -> List[LeadScoringOutput]:
        """Ejecuta scoring en batch."""
        sem = asyncio.Semaphore(max_concurrent)
        async def _one(lead):
            async with sem:
                return await self.execute(lead)
        return await asyncio.gather(*[_one(l) for l in leads[:1000]])

    def health(self) -> Dict[str, Any]:
        """Estado del agente."""
        req = max(1, self.metrics["requests"])
        return {
            "agent_id": self.AGENT_ID,
            "version": self.VERSION,
            "contract": self.CONTRACT,
            "tenant_id": self.tenant_id,
            "status": "healthy" if self.metrics["errors"] / req < 0.05 else "degraded",
            "metrics": {
                "requests": self.metrics["requests"],
                "errors": self.metrics["errors"],
                "error_rate": round(self.metrics["errors"] / req, 4),
                "avg_latency_ms": round(self.metrics["total_ms"] / req, 2),
                "layer_coverage": round(self.metrics["layer_hits"] / req, 4)
            },
            "cache": self.cache.stats() if self.cache else None,
            "reason_codes_layer": self.use_reason_codes_layer
        }


# ─────────────────────────────────────────────────────────────
# FACTORY (única)
# ─────────────────────────────────────────────────────────────

def create_agent_instance(tenant_id: str, config: Dict = None) -> LeadScoringIA:
    """Factory estándar para el registry."""
    return LeadScoringIA(tenant_id, config)
