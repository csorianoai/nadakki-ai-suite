# filepath: agents/marketing/leadscoringia.py
"""
LeadScoringIA v2.2 — Enterprise Grade (compatible con schemas canónicos)

Mejoras clave:
- Merge seguro de configuración (evita KeyError como 'income_range')
- Token Bucket rate-limiter por tenant
- LRU Cache con TTL (cache hits sub-ms)
- Circuit Breaker de resiliencia
- Fairness básico por canal
- Model Registry (versionado de pesos/umbrales)
- Normalización robusta (acepta min/max, min_val/max_val o posicional)
- Totalmente compatible con schemas.canonical (Lead, LeadScoringOutput)

Contrato: leads.v2.2
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import os
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Usa los modelos canónicos existentes del proyecto
from schemas.canonical import Lead, LeadScoringOutput

# ─────────────────────────────────────────────────────────────────────
# Infraestructura (Rate limit, Cache, Circuit Breaker, Fairness, Models)
# ─────────────────────────────────────────────────────────────────────

class TokenBucket:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def stats(self) -> Dict[str, Any]:
        return {"tokens_available": round(self.tokens, 2), "rate_per_sec": self.rate, "capacity": self.capacity}


class LRUCacheTTL:
    def __init__(self, capacity: int = 1000, ttl_seconds: int = 300):
        self._store: OrderedDict = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        item = self._store.pop(key, None)
        if item is None:
            self.misses += 1
            return None
        value, ts = item
        if time.time() - ts > self.ttl:
            self.misses += 1
            return None
        self._store[key] = (value, ts)
        self.hits += 1
        return value

    def put(self, key: str, value: Any):
        if key in self._store:
            self._store.pop(key, None)
        elif len(self._store) >= self.capacity:
            self._store.popitem(last=False)
        self._store[key] = (value, time.time())

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 4) if total else 0.0,
            "size": len(self._store),
            "ttl_sec": self.ttl,
            "capacity": self.capacity,
        }


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout_sec: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_sec = timeout_sec  # FIXED: Proper indentation
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def call(self, fn, *args, **kwargs):
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_failure_time > self.timeout_sec:
                self.state = "HALF_OPEN"
            else:
                raise RuntimeError("circuit_breaker_open")
        try:
            res = fn(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return res
        except Exception as e:
            self.failures += 1
            self.last_failure_time = now
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            raise e

    def status(self) -> Dict[str, Any]:
        return {"state": self.state, "failures": self.failures, "last_failure": self.last_failure_time}


class FairnessMonitor:
    def __init__(self):
        self.scores_by_channel: Dict[str, List[float]] = {}

    def record(self, score: float, channel: str):
        self.scores_by_channel.setdefault(channel, []).append(score)

    def disparity(self) -> Dict[str, Any]:
        if not self.scores_by_channel:
            return {"disparity": 0.0, "flag": False}
        avgs = {ch: (sum(v) / len(v)) for ch, v in self.scores_by_channel.items() if v}
        if len(avgs) < 2:
            return {"disparity": 0.0, "flag": False, "by_channel": {k: round(v, 4) for k, v in avgs.items()}}
        mx, mn = max(avgs.values()), min(avgs.values())
        gap = mx - mn
        return {"disparity": round(gap, 4), "flag": gap > 0.05, "by_channel": {k: round(v, 4) for k, v in avgs.items()}}


class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}

    def register(self, version: str, weights: Dict, thresholds: Dict):
        self.models[version] = {
            "weights": weights,
            "thresholds": thresholds,
            "created_at": datetime.now().isoformat(),
        }

    def get(self, version: str = "latest") -> Dict[str, Any]:
        if version == "latest" and self.models:
            latest = max(self.models.items(), key=lambda x: x[1]["created_at"])
            return latest[1]
        return self.models.get(version, self.models.get("default", {}))

    def list_versions(self) -> List[str]:
        return list(self.models.keys())


# ─────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────────────
DEFAULT_WEIGHTS = {"income": 0.30, "credit_score": 0.35, "channel": 0.20, "engagement": 0.15}
CHANNEL_SCORES = {
    "referral": 1.0, "search": 0.85, "landing_form": 0.70, "social": 0.55, "display": 0.40, "email": 0.75, "partner": 0.80
}


# ─────────────────────────────────────────────────────────────────────
# Agente
# ─────────────────────────────────────────────────────────────────────
class LeadScoringIA:
    CONTRACT_VERSION = "leads.v2.2"
    AGENT_ID = "lead_scoring_ia"
    VERSION = "2.2.0"

    def __init__(
        self,
        tenant_id: str,
        config: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True,
        enable_fairness: bool = True,
        enable_rate_limit: bool = True,
    ) -> None:
        self.tenant_id = tenant_id

        # --- MERGE SEGURO: default + overrides ---
        base = self._default_config()
        if config:
            self._merge_deep(base, config)
        self.config = base
        # -----------------------------------------

        # Modelos / pesos / umbrales
        self.model_registry = ModelRegistry()
        self._register_default_models()
        model_version = self.config.get("model_version", "default")
        model = self.model_registry.get(model_version)
        self.weights = model.get("weights", DEFAULT_WEIGHTS)
        self.bucket_thresholds = model.get("thresholds", {"A": 0.80, "B": 0.60, "C": 0.40})
        self.channel_scores = self.config.get("channel_scores", CHANNEL_SCORES)

        # Enterprise features
        self.cache = LRUCacheTTL(1000, 300) if enable_cache else None
        self.cache_secret = self.config.get("cache_secret") or os.urandom(32).hex()
        self.circuit_breaker = CircuitBreaker(5, 60)
        self.fairness = FairnessMonitor() if enable_fairness else None

        # Rate limiting (post-merge)
        rl = self.config.get("rate_limit", {})
        rate = rl.get("rate", 100)
        capacity = rl.get("capacity", 200)
        self.rate_limiter = TokenBucket(rate, capacity) if enable_rate_limit else None

        # Métricas
        self.requests = 0
        self.errors = 0
        self.total_time_ms = 0.0

    # Helper merge profundo simple (dicts anidados)
    def _merge_deep(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._merge_deep(base[k], v)
            else:
                base[k] = v

    def _register_default_models(self):
        self.model_registry.register("default", DEFAULT_WEIGHTS, {"A": 0.80, "B": 0.60, "C": 0.40})
        self.model_registry.register(
            "engagement_focused",
            {"income": 0.25, "credit_score": 0.30, "channel": 0.20, "engagement": 0.25},
            {"A": 0.75, "B": 0.55, "C": 0.35},
        )

    def _default_config(self) -> Dict[str, Any]:
        return {
            "weights": DEFAULT_WEIGHTS,
            "channel_scores": CHANNEL_SCORES,
            "income_range": {"min": 0.0, "max": 200000.0},
            "credit_range": {"min": 300.0, "max": 850.0},
            "bucket_thresholds": {"A": 0.80, "B": 0.60, "C": 0.40},
            "model_version": "default",
            "rate_limit": {"rate": 100, "capacity": 200},
        }

    # ─────────────────────────────────────────────────────────────────
    # API Pública
    # ─────────────────────────────────────────────────────────────────
    async def execute(self, lead: Lead) -> LeadScoringOutput:
        """
        Ejecuta el scoring para un lead (usando schemas canónicos).
        """
        self.requests += 1
        t0 = time.perf_counter()

        try:
            # Rate limit
            if self.rate_limiter and not self.rate_limiter.consume():
                raise ValueError("rate_limit_exceeded")

            # Tenant guard
            if lead.tenant_id != self.tenant_id:
                raise ValueError("tenant_mismatch")

            # Cache
            key = self._cache_key_hmac(lead)
            cached = self.cache.get(key) if self.cache else None
            if cached:
                dt = max(1, int((time.perf_counter() - t0) * 1000))
                self.total_time_ms += dt
                # Construye salida canónica desde el resultado cacheado
                return self._build_output(
                    success=True,
                    tenant_id=self.tenant_id,
                    execution_time_ms=dt,
                    result=cached,
                    reason_codes=cached.get("reason_codes", []),
                )

            # Score (con circuit breaker)
            scored = self.circuit_breaker.call(self._score, lead)

            # Fairness
            if self.fairness:
                ch = getattr(lead, "channel", None) or getattr(lead.attributes, "channel", "landing_form")
                self.fairness.record(scored["score"], str(ch).lower())

            # Cache write
            if self.cache:
                self.cache.put(key, scored)

            dt = max(1, int((time.perf_counter() - t0) * 1000))
            self.total_time_ms += dt

            logger.info(
                "success tenant=%s lead=%s score=%.4f bucket=%s dt=%dms",
                self.tenant_id, scored["lead_id"], scored["score"], scored["bucket"], dt
            )

            return self._build_output(
                success=True,
                tenant_id=self.tenant_id,
                execution_time_ms=dt,
                result=scored,
                reason_codes=scored.get("reason_codes", []),
            )

        except Exception as e:
            self.errors += 1
            dt = max(1, int((time.perf_counter() - t0) * 1000))
            self.total_time_ms += dt
            logger.exception("error tenant=%s err=%s dt=%dms", self.tenant_id, str(e), dt)
            # Devuelve un LeadScoringOutput válido con error para trazabilidad
            return self._build_output(
                success=False,
                tenant_id=self.tenant_id,
                execution_time_ms=dt,
                result={"error": str(e)},
                reason_codes=["execution_error"],
            )

    async def execute_batch(self, leads: List[Lead], max_concurrent: int = 10) -> List[LeadScoringOutput]:
        leads = leads[:1000]  # Anti-DoS
        sem = asyncio.Semaphore(max_concurrent)

        async def _one(l: Lead):
            async with sem:
                return await self.execute(l)

        return await asyncio.gather(*[ _one(l) for l in leads ], return_exceptions=False)

    # ─────────────────────────────────────────────────────────────────
    # Helpers de negocio
    # ─────────────────────────────────────────────────────────────────
    def _cache_key_hmac(self, lead: Lead) -> str:
        ch = getattr(lead, "channel", None) or getattr(lead.attributes, "channel", "landing_form")
        key_data = f"{lead.lead_id}:{str(ch)}"
        return hmac.new(self.cache_secret.encode(), key_data.encode(), hashlib.sha256).hexdigest()[:32]

    def _normalize(
        self,
        value: float,
        *args,
        min: float = None, max: float = None,
        min_val: float = None, max_val: float = None,
        **kwargs
    ) -> float:
        """
        Normaliza en [0,1]. Firma flexible:
          - _normalize(v, min=..., max=...)
          - _normalize(v, min_val=..., max_val=...)
          - _normalize(v, <min>, <max>)  # posicional
        """
        if len(args) >= 2 and min is None and max is None and min_val is None and max_val is None:
            min_v, max_v = float(args[0]), float(args[1])
        else:
            min_v = float(min if min is not None else (min_val if min_val is not None else float(kwargs.get("min", kwargs.get("min_val", 0.0)))))
            max_v = float(max if max is not None else (max_val if max_val is not None else float(kwargs.get("max", kwargs.get("max_val", 1.0)))))

        if max_v == min_v:
            return 0.5

        try:
            norm = (float(value) - min_v) / (max_v - min_v)
        except Exception:
            return 0.0

        if norm < 0.0: return 0.0
        if norm > 1.0: return 1.0
        return norm

    def _engagement(self, events: Optional[List]) -> float:
        if not events:
            return 0.0
        weights = {"form_submit": 1.0, "call": 0.9, "download": 0.7, "click": 0.5, "email_open": 0.4, "pageview": 0.3}
        def etype(e) -> str:
            # admite pydantic o dict
            if isinstance(e, dict):
                return str(e.get("type", "other")).lower()
            return str(getattr(e, "type", "other")).lower()
        total = sum(weights.get(etype(e), 0.1) for e in events[:100])
        return min(1.0, total / 10.0)

    def _bucket_of(self, score: float) -> str:
        th = self.bucket_thresholds
        if score >= th["A"]: return "A"
        if score >= th["B"]: return "B"
        if score >= th["C"]: return "C"
        return "D"

    def _score(self, lead: Lead) -> Dict[str, Any]:
        # Datos
        attrs = lead.attributes
        income = float(getattr(attrs, "income", 0) or 0)
        credit = float(getattr(attrs, "credit_score", 0) or 0)
        channel_name = getattr(lead, "channel", None) or getattr(attrs, "channel", "landing_form")
        engagement = self._engagement(getattr(lead, "events", None))

        # Componentes
        channel = float(self.channel_scores.get(str(channel_name).lower(), 0.5))
        income_norm = self._normalize(income, **self.config["income_range"])
        credit_norm = self._normalize(credit, **self.config["credit_range"])

        # Score ponderado
        w = self.weights
        score = income_norm * w["income"] + credit_norm * w["credit_score"] + channel * w["channel"] + engagement * w["engagement"]
        bucket = self._bucket_of(score)

        # Reason codes + acción recomendada
        reasons = []
        if credit_norm >= 0.8: reasons.append("high_credit")
        if income_norm >= 0.8: reasons.append("high_income")
        if channel >= 0.8: reasons.append("quality_channel")
        if engagement >= 0.6: reasons.append("engaged_user")
        if score < 0.4: reasons.append("low_overall_score")
        if not reasons: reasons.append("standard_scoring")

        actions = {"A": "assign_to_sales", "B": "assign_to_sales", "C": "nurture", "D": "reject"}

        return {
            "lead_id": lead.lead_id,
            "score": round(float(score), 3),
            "bucket": bucket,
            "components": {
                "income_norm": round(income_norm, 4),
                "credit_norm": round(credit_norm, 4),
                "channel": round(channel, 4),
                "engagement": round(engagement, 4),
            },
            "reason_codes": reasons,
            "recommended_action": actions[bucket],
        }

    # ─────────────────────────────────────────────────────────────────
    # Observabilidad
    # ─────────────────────────────────────────────────────────────────
    def health(self) -> Dict[str, Any]:
        avg = (self.total_time_ms / self.requests) if self.requests else 0.0
        err_rate = (self.errors / self.requests) if self.requests else 0.0

        data = {
            "agent": self.AGENT_ID,
            "version": self.VERSION,
            "contract": self.CONTRACT_VERSION,
            "status": "healthy" if err_rate < 0.05 else "degraded",
            "metrics": {"requests": self.requests, "errors": self.errors, "error_rate": round(err_rate, 4), "avg_time_ms": round(avg, 2)},
            "circuit_breaker": self.circuit_breaker.status(),
            "weights": self.weights,
            "channels": list(self.channel_scores.keys()),
            "model_versions": self.model_registry.list_versions(),
        }

        if self.cache:
            data["cache"] = self.cache.stats()
        if self.fairness:
            data["fairness"] = self.fairness.disparity()
        if self.rate_limiter:
            data["rate_limiter"] = self.rate_limiter.stats()

        data["features"] = {
            "cache": self.cache is not None,
            "fairness": self.fairness is not None,
            "rate_limit": self.rate_limiter is not None,
            "batch_scoring": True,
            "model_versioning": True,
        }
        return data

    def _build_output(
        self,
        *,
        success: bool,
        tenant_id: str,
        execution_time_ms: int,
        result: Dict[str, Any],
        reason_codes: List[str],
    ) -> LeadScoringOutput:
        """
        Construye un LeadScoringOutput canónico a partir de los datos de scoring/caché.
        No asume campos extra no soportados por el esquema canónico.
        """
        payload = {
            "success": success,
            "agent": self.AGENT_ID,
            "tenant_id": tenant_id,
            "execution_time_ms": execution_time_ms,
            "reason_codes": reason_codes,
            "result": result,
        }
        # Pydantic validará contra el modelo canónico.
        return LeadScoringOutput.model_validate(payload)


# Fábrica estándar (consumida por el registry/canonical)
def create_agent_instance(tenant_id: str, config: Dict = None):
    return LeadScoringIA(tenant_id, config)