# filepath: agents/marketing/abtestingimpactia.py
"""
ABTestingImpactIA v3.2.0 - Enterprise A/B Testing Impact Analysis Engine
Author: Nadakki AI Suite
Version: 3.2.0
"""

from __future__ import annotations
import hashlib, json, logging, math, re, time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ABTestingImpactIA")

VERSION = "3.2.0"
MAX_CACHE_SIZE = 500
DEFAULT_TTL_SECONDS = 3600
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60

TestType = Literal["conversion", "engagement", "revenue", "retention"]

class FeatureFlags:
    def __init__(self, initial: Optional[Dict[str, bool]] = None):
        self.flags = {"CACHE_ENABLED": True, "CIRCUIT_BREAKER": True, "FALLBACK_MODE": True,
                     "ADVANCED_METRICS": True, "PII_DETECTION": True, "COMPLIANCE_CHECK": True}
        if initial:
            self.flags.update(initial)
    
    def is_enabled(self, name: str) -> bool:
        return self.flags.get(name, False)

class CircuitBreaker:
    def __init__(self, failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD, timeout=CIRCUIT_BREAKER_TIMEOUT):
        self.failure_threshold, self.timeout = failure_threshold, timeout
        self.failures, self.last_failure_time, self.state = 0, None, "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "OPEN" and (time.time() - (self.last_failure_time or 0)) > self.timeout:
            self.state = "HALF_OPEN"
            return True
        return self.state != "OPEN"

    def record_success(self):
        if self.state == "HALF_OPEN": self.state = "CLOSED"
        self.failures = 0; self.last_failure_time = None

    def record_failure(self):
        self.failures += 1; self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold: self.state = "OPEN"

@dataclass
class VariantData:
    variant_name: str
    sample_size: int
    conversions: int
    revenue: float = 0.0

@dataclass
class ABTestInput:
    tenant_id: str
    test_name: str
    test_type: TestType
    control: VariantData
    treatment: VariantData
    confidence_level: float = 0.95
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.tenant_id.startswith("tn_"):
            raise ValueError("Invalid tenant_id")

@dataclass
class StatisticalResults:
    statistically_significant: bool
    p_value: float
    confidence_interval: tuple
    min_sample_size_needed: int
    power: float

@dataclass
class ImpactMetrics:
    relative_lift: float
    absolute_lift: float
    winner: str
    recommendation: str

@dataclass
class ComplianceSummary:
    passed: bool
    issues: List[str]
    rules_applied: List[str]

@dataclass
class AuditTrail:
    template_version: str
    config_hash: str
    decision_trace: List[str]
    reason_codes: List[str]

@dataclass
class ABTestResult:
    analysis_id: str
    tenant_id: str
    test_name: str
    statistical_results: StatisticalResults
    impact_metrics: ImpactMetrics
    compliance_summary: ComplianceSummary
    audit_trail: AuditTrail
    latency_ms: int
    metadata: Dict[str, Any]

class ComplianceEngine:
    @staticmethod
    def validate_inputs(inp: ABTestInput) -> Tuple[bool, List[str], List[str]]:
        issues, rules, reasons = [], [], []
        rules.extend(["bounds:confidence_level", "sanity:non_negative_counts"])
        
        for vname, v in [("control", inp.control), ("treatment", inp.treatment)]:
            if v.sample_size < 1:
                issues.append(f"{vname}:invalid_sample")
                reasons.append("invalid_sample_size")
            if v.conversions > v.sample_size:
                issues.append(f"{vname}:invalid_conversions")
                reasons.append("inconsistent_counts")
        
        passed = len(issues) == 0
        return passed, issues, list(set(reasons))

class StatEngine:
    @staticmethod
    def z_score(p1: float, p2: float, n1: int, n2: int) -> float:
        p_pool = (p1 * n1 + p2 * n2) / max(1, (n1 + n2))
        se = math.sqrt(max(1e-12, p_pool * (1 - p_pool) * (1/n1 + 1/n2)))
        return (p1 - p2) / se if se > 0 else 0.0
    
    @staticmethod
    def p_value_from_z(z: float) -> float:
        return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    
    @staticmethod
    def confidence_interval(p: float, n: int, z: float) -> tuple:
        se = math.sqrt(max(1e-12, p * (1 - p) / max(1, n)))
        return (max(0.0, p - z * se), min(1.0, p + z * se))
    
    @staticmethod
    def min_sample_size(p1: float, p2: float) -> int:
        z_alpha, z_beta = 1.96, 0.84
        p_avg = max(1e-6, (p1 + p2) / 2)
        effect = max(1e-6, abs(p1 - p2))
        n = ((z_alpha + z_beta) ** 2 * 2 * p_avg * (1 - p_avg)) / (effect ** 2)
        return int(math.ceil(n))

class ABTestingImpactIA:
    def __init__(self, tenant_id: str, config: Optional[Dict] = None, flags: Optional[Dict[str, bool]] = None):
        self.tenant_id, self.agent_id, self.version = tenant_id, "ab_testing_impact_ia", VERSION
        self.config = config or {"enable_cache": True, "cache_ttl_seconds": DEFAULT_TTL_SECONDS}
        self.flags, self.breaker = FeatureFlags(flags), CircuitBreaker()
        self._cache: "OrderedDict[str, tuple]" = OrderedDict()
        self._cache_max_size = MAX_CACHE_SIZE
        self._metrics = {"total": 0, "ok": 0, "fail": 0, "cache_hits": 0, "fallbacks": 0,
                        "avg_latency_ms": 0.0, "latency_hist": []}

    def _cache_key(self, inp: ABTestInput) -> str:
        s = json.dumps({"tenant": inp.tenant_id, "test": inp.test_name, 
                       "ctrl": [inp.control.sample_size, inp.control.conversions],
                       "trt": [inp.treatment.sample_size, inp.treatment.conversions]}, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()[:16]

    def _get_from_cache(self, key: str) -> Optional[ABTestResult]:
        if not self.flags.is_enabled("CACHE_ENABLED"): return None
        item = self._cache.get(key)
        if not item: return None
        result, ts = item
        ttl = self.config.get("cache_ttl_seconds", 0)
        if ttl and (time.time() - ts) > ttl:
            self._cache.pop(key, None); return None
        self._cache.move_to_end(key); self._metrics["cache_hits"] += 1
        return result

    def _put_in_cache(self, key: str, result: ABTestResult):
        if not self.flags.is_enabled("CACHE_ENABLED"): return
        self._cache[key] = (result, time.time())
        if len(self._cache) > self._cache_max_size: self._cache.popitem(last=False)

    def _execute_core(self, inp: ABTestInput) -> ABTestResult:
        t0 = time.perf_counter()
        decision_trace, reason_codes = [], []

        passed, issues, rc = ComplianceEngine.validate_inputs(inp)
        reason_codes.extend(rc)

        p_ctrl = inp.control.conversions / max(1, inp.control.sample_size)
        p_trt = inp.treatment.conversions / max(1, inp.treatment.sample_size)
        
        z = StatEngine.z_score(p_trt, p_ctrl, inp.treatment.sample_size, inp.control.sample_size)
        p_val = StatEngine.p_value_from_z(z)
        
        alpha = 1 - inp.confidence_level
        significant = p_val < alpha
        ci_trt = StatEngine.confidence_interval(p_trt, inp.treatment.sample_size, 1.96)
        
        min_n = StatEngine.min_sample_size(p_ctrl, p_trt)
        current_n = min(inp.control.sample_size, inp.treatment.sample_size)
        power = min(0.99, current_n / max(1, min_n))
        
        stat_results = StatisticalResults(
            statistically_significant=significant,
            p_value=round(p_val, 6),
            confidence_interval=(round(ci_trt[0], 6), round(ci_trt[1], 6)),
            min_sample_size_needed=min_n,
            power=round(power, 3)
        )
        
        rel_lift = ((p_trt - p_ctrl) / max(1e-6, p_ctrl)) * 100 if p_ctrl > 0 else 0
        abs_lift = p_trt - p_ctrl
        
        if significant and p_trt > p_ctrl:
            winner, rec = "treatment", f"Deploy treatment (lift: {rel_lift:+.1f}%)"
        elif significant:
            winner, rec = "control", "Keep control"
        else:
            winner, rec = "inconclusive", "Continue testing"
        
        impact = ImpactMetrics(round(rel_lift, 4), round(abs_lift, 6), winner, rec)
        
        compliance = ComplianceSummary(passed, issues, ["bounds", "sanity"])
        config_hash = hashlib.sha256(json.dumps(self.config, sort_keys=True).encode()).hexdigest()[:16]
        audit = AuditTrail(VERSION, config_hash, decision_trace, reason_codes)
        
        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        self._metrics["latency_hist"].append(latency_ms)
        n = max(1, self._metrics["total"])
        self._metrics["avg_latency_ms"] = ((self._metrics["avg_latency_ms"] * (n - 1)) + latency_ms) / n
        
        analysis_id = f"abtest_{int(datetime.utcnow().timestamp()*1000)}_{hashlib.sha256(inp.test_name.encode()).hexdigest()[:6]}"
        
        return ABTestResult(analysis_id, self.tenant_id, inp.test_name, stat_results, 
                          impact, compliance, audit, latency_ms, 
                          {"agent_version": VERSION, "request_id": inp.request_id})

    async def execute(self, inp: ABTestInput) -> ABTestResult:
        self._metrics["total"] += 1
        
        if self.flags.is_enabled("CIRCUIT_BREAKER") and not self.breaker.can_execute():
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise RuntimeError("Circuit breaker OPEN")
        
        key = self._cache_key(inp)
        cached = self._get_from_cache(key)
        if cached: return cached
        
        try:
            result = self._execute_core(inp)
            self.breaker.record_success(); self._metrics["ok"] += 1
            self._put_in_cache(key, result)
            return result
        except Exception as e:
            logger.exception("ABTestingImpactIA failed", extra={"error": str(e)})
            self.breaker.record_failure(); self._metrics["fail"] += 1
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise

    def _fallback(self, inp: ABTestInput) -> ABTestResult:
        stat = StatisticalResults(False, 1.0, (0.0, 0.0), 10000, 0.0)
        impact = ImpactMetrics(0.0, 0.0, "inconclusive", "Fallback mode")
        compliance = ComplianceSummary(True, ["fallback"], [])
        audit = AuditTrail(VERSION, "fallback", ["fallback_mode"], ["system_recovery"])
        return ABTestResult(f"fallback_{int(datetime.utcnow().timestamp())}", 
                          self.tenant_id, inp.test_name, stat, impact, compliance, 
                          audit, 1, {"fallback": True, "agent_version": VERSION})

    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "agent_id": self.agent_id, "agent_version": VERSION,
               "tenant_id": self.tenant_id, "total_requests": self._metrics["total"]}

    def get_metrics(self) -> Dict[str, Any]:
        return {"agent_name": self.agent_id, "agent_version": VERSION,
               "tenant_id": self.tenant_id, **self._metrics}

def create_agent_instance(tenant_id: str, config: Optional[Dict] = None, flags: Optional[Dict[str, bool]] = None):
    return ABTestingImpactIA(tenant_id, config, flags)
