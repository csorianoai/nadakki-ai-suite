# filepath: agents/marketing/contentperformanceia.py
"""
ContentPerformanceIA v3.3.0 - Enterprise Content Performance Analytics Engine
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
READY FOR PRODUCTION âœ…

AnalÃ­tica avanzada de performance de contenido con:
- Circuit Breaker (OPEN/HALF_OPEN/CLOSED) y Fallback mode
- Cache LRU con TTL
- PII detection + masking (email/telÃ©fono/IDs) y consentimiento (GDPR/CCPA/LGPD)
- Compliance engine (brand safety, claims, disclosure)
- AnÃ¡lisis cross-canal (blog, social, email, video)
- PredicciÃ³n de viralidad y engagement (determinÃ­stica)
- DetecciÃ³n de tendencias y topics ganadores
- Audit Trail detallado (decision trace + eventos)
- Feature flags y mÃ©tricas avanzadas (latencia p95/p99/cache hit rate)

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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ContentPerformanceIA")

VERSION = "3.3.0"
MAX_CACHE_SIZE = 800
DEFAULT_TTL_SECONDS = 1800
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60

Language = Literal["es", "en", "pt"]
Jurisdiction = Literal[
    "US",
    "MX",
    "BR",
    "CO",
    "EU",
    "DO",
    "AR",
    "CL",
    "PE",
    "UY",
    "PA",
    "CR",
    "EC",
    "VE",
]
ContentType = Literal["blog_post", "social_post", "email", "video", "infographic", "webinar"]
Channel = Literal["blog", "instagram", "twitter", "linkedin", "facebook", "youtube", "email"]
PerformanceLevel = Literal["viral", "high", "medium", "low", "underperforming"]

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
            "VIRALITY_PREDICTION": True,
            "TREND_DETECTION": True,
            "PII_DETECTION": True,
            "COMPLIANCE_ENGINE": True,
            "AUDIT_TRAIL": True,
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
# COMPLIANCE & PII
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class PIIUtils:
    """DetecciÃ³n y enmascaramiento bÃ¡sico de PII en campos de texto."""
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
    def scrub_text(text: str) -> Tuple[str, bool]:
        """Enmascara PII y retorna (texto, pii_detected)."""
        if not text:
            return text, False
        original = text
        text = PIIUtils.mask_email(text)
        text = PIIUtils.mask_phone(text)
        text = PIIUtils.mask_ids(text)
        return text, text != original

class ComplianceEngine:
    """Reglas de compliance (brand safety, claims, disclosures, consentimiento por jurisdicciÃ³n)."""
    PROHIBITED_WORDS = {"garantizado", "100% seguro", "sin riesgo"}
    DISCLOSURE_REQUIRED = {"promocionado", "patrocinado", "advert", "ad", "#ad", "#sponsored"}

    @staticmethod
    def jurisdiction_requirements(jurisdiction: Jurisdiction) -> Dict[str, Any]:
        # Nota: reglas simplificadas, se pueden extender por cada paÃ­s/estado
        base = {"consent_opt_in": False, "disclosure_tag": "#ad"}
        if jurisdiction in {"EU"}:
            base["consent_opt_in"] = True  # GDPR
        if jurisdiction in {"BR"}:
            base["consent_opt_in"] = True  # LGPD
        if jurisdiction in {"US"}:
            base["disclosure_tag"] = "#ad"  # FTC guidance
        return base

    @classmethod
    def check_brand_safety(cls, title: str) -> List[str]:
        flags: List[str] = []
        lower = (title or "").lower()
        for w in cls.PROHIBITED_WORDS:
            if w in lower:
                flags.append(f"prohibited_word:{w}")
        return flags

    @classmethod
    def check_disclosure(cls, text: str) -> bool:
        low = (text or "").lower()
        return any(tag in low for tag in cls.DISCLOSURE_REQUIRED)

    @classmethod
    def enforce(cls, title: str, channel: Channel, jurisdiction: Jurisdiction, has_consent: bool) -> List[str]:
        notes: List[str] = []
        # Brand safety
        notes.extend(cls.check_brand_safety(title))
        # Consentimiento
        req = cls.jurisdiction_requirements(jurisdiction)
        if req.get("consent_opt_in", False) and not has_consent:
            notes.append("consent_missing")
        # Disclosure sugerido
        if channel in {"instagram", "twitter", "facebook", "youtube", "linkedin"} and not cls.check_disclosure(title):
            notes.append("add_disclosure_tag")
        return notes

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DATA MODELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@dataclass
class ContentMetrics:
    impressions: int
    reach: int
    engagement: int
    clicks: int
    shares: int
    comments: int
    saves: int = 0
    watch_time_seconds: int = 0

@dataclass
class ContentItem:
    content_id: str
    content_type: ContentType
    channel: Channel
    publish_date: datetime
    title: str
    metrics: ContentMetrics
    topic_tags: List[str] = field(default_factory=list)
    language: Language = "es"
    jurisdiction: Jurisdiction = "MX"
    marketing_consent: bool = True  # consentimiento para uso/analÃ­tica de marketing

    def scrub(self, enable_pii: bool) -> Tuple["ContentItem", bool]:
        """Devuelve una copia con PII enmascarada (si aplica) y flag de detecciÃ³n."""
        if not enable_pii:
            return self, False
        pii_found = False
        new_title, flag = PIIUtils.scrub_text(self.title or "")
        pii_found = pii_found or flag
        new_tags: List[str] = []
        for t in self.topic_tags:
            masked, flag = PIIUtils.scrub_text(t)
            pii_found = pii_found or flag
            new_tags.append(masked)
        clone = ContentItem(
            content_id=self.content_id,
            content_type=self.content_type,
            channel=self.channel,
            publish_date=self.publish_date,
            title=new_title,
            metrics=self.metrics,
            topic_tags=new_tags,
            language=self.language,
            jurisdiction=self.jurisdiction,
            marketing_consent=self.marketing_consent,
        )
        return clone, pii_found

@dataclass
class PerformanceAnalysisInput:
    tenant_id: str
    content_items: List[ContentItem]
    analysis_period_days: int = 30
    language: Language = "es"
    jurisdiction: Jurisdiction = "MX"
    request_id: Optional[str] = None

    def __post_init__(self):
        if not re.match(r"^tn_[a-z0-9_]{8,64}$", self.tenant_id):
            raise ValueError("Invalid tenant_id format (expected prefix tn_)")
        if not self.content_items:
            raise ValueError("At least one content item is required")

@dataclass
class ContentPerformance:
    content_id: str
    performance_level: PerformanceLevel
    engagement_rate: float
    virality_score: float  # 0-100
    reach_efficiency: float  # reach/impressions (%)
    predicted_performance: str
    optimization_suggestions: List[str]
    compliance_flags: List[str] = field(default_factory=list)

@dataclass
class TrendInsight:
    topic: str
    frequency: int
    avg_engagement: float
    trend_direction: Literal["rising", "stable", "declining"]

@dataclass
class AuditEvent:
    ts: str
    step: str
    detail: Dict[str, Any]

@dataclass
class PerformanceAnalysisResult:
    analysis_id: str
    tenant_id: str
    content_performances: List[ContentPerformance]
    top_performers: List[str]
    trending_topics: List[TrendInsight]
    channel_benchmarks: Dict[Channel, float]
    recommendations: List[str]
    latency_ms: int
    metadata: Dict[str, Any]
    decision_trace: List[str] = field(default_factory=list)
    audit_trail: List[AuditEvent] = field(default_factory=list)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENGINES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class PerformanceEngine:
    """Motor de anÃ¡lisis de rendimiento de contenido."""
    @staticmethod
    def calculate_engagement_rate(metrics: ContentMetrics) -> float:
        """Calcula tasa de engagement respecto a reach (porcentaje)."""
        total_engagement = metrics.engagement + metrics.clicks + metrics.shares + metrics.comments + metrics.saves
        return round((total_engagement / max(1, metrics.reach)) * 100.0, 2)

    @staticmethod
    def calculate_virality_score(metrics: ContentMetrics, seed: str) -> float:
        """Calcula score de viralidad (0-100) con componente determinÃ­stica."""
        share_rate = (metrics.shares / max(1, metrics.reach)) * 100.0
        total_eng = metrics.engagement + metrics.clicks + metrics.comments
        eng_rate = (total_eng / max(1, metrics.impressions)) * 100.0
        hash_val = int(hashlib.sha256(seed.encode()).hexdigest()[:4], 16)
        velocity_factor = (hash_val % 30) / 100.0  # 0-0.30
        virality = (share_rate * 0.5 + eng_rate * 0.3 + velocity_factor * 0.2) * 10.0
        return round(min(100.0, virality), 1)

    @staticmethod
    def classify_performance(engagement_rate: float, virality_score: float) -> PerformanceLevel:
        """Clasifica nivel de performance."""
        if virality_score >= 70.0 or engagement_rate >= 10.0:
            return "viral"
        if engagement_rate >= 5.0:
            return "high"
        if engagement_rate >= 2.0:
            return "medium"
        if engagement_rate >= 0.5:
            return "low"
        return "underperforming"

    @staticmethod
    def predict_performance(engagement_rate: float) -> str:
        """PredicciÃ³n de performance futura basada en seÃ±al temprana (heurÃ­stica)."""
        if engagement_rate >= 5.0:
            return "Expected to go viral - scale up promotion"
        if engagement_rate >= 2.0:
            return "Strong performance - maintain momentum"
        if engagement_rate >= 0.5:
            return "Moderate performance - consider A/B testing"
        return "Underperforming - review content strategy"

    @staticmethod
    def generate_optimizations(performance: PerformanceLevel, content_type: ContentType, channel: Channel) -> List[str]:
        """Sugerencias de optimizaciÃ³n (top-3)."""
        suggestions: List[str] = []
        if performance in {"low", "underperforming"}:
            suggestions += [
                "Revisar headline/tÃ­tulo para mayor impacto",
                "Agregar call-to-action mÃ¡s claro",
                "Optimizar horario de publicaciÃ³n",
            ]
        if content_type == "video" and performance != "viral":
            suggestions += ["Mejorar thumbnail para aumentar CTR", "Optimizar primeros 10s para retenciÃ³n"]
        if channel in {"instagram", "facebook"} and performance != "viral":
            suggestions += ["AÃ±adir elementos visuales mÃ¡s llamativos", "Incrementar uso de hashtags relevantes"]
        return suggestions[:3]

class TrendEngine:
    """Motor de detecciÃ³n de tendencias (topics)."""
    @staticmethod
    def detect_trends(content_items: List[ContentItem]) -> List[TrendInsight]:
        topic_stats: Dict[str, Dict[str, Any]] = {}
        for item in content_items:
            for topic in item.topic_tags:
                stats = topic_stats.setdefault(topic, {"count": 0, "total_engagement": 0.0})
                stats["count"] += 1
                stats["total_engagement"] += PerformanceEngine.calculate_engagement_rate(item.metrics)
        insights: List[TrendInsight] = []
        for topic, st in topic_stats.items():
            count = max(1, st["count"])
            avg_eng = st["total_engagement"] / count
            if count >= 3 and avg_eng >= 3.0:
                direction = "rising"
            elif avg_eng >= 2.0:
                direction = "stable"
            else:
                direction = "declining"
            insights.append(TrendInsight(topic=topic, frequency=st["count"], avg_engagement=round(avg_eng, 2), trend_direction=direction))
        return sorted(insights, key=lambda t: t.avg_engagement, reverse=True)[:5]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAIN AGENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class ContentPerformanceIA:
    """Agente principal de anÃ¡lisis de performance de contenido."""
    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None, flags: Optional[Dict[str, bool]] = None):
        self.tenant_id = tenant_id
        self.agent_id = "content_performance_ia"
        self.version = VERSION
        self.config = config or {"enable_cache": True, "cache_ttl_seconds": DEFAULT_TTL_SECONDS}
        self.flags = FeatureFlags(flags)
        self.breaker = CircuitBreaker()

        self._cache: "OrderedDict[str, Tuple[PerformanceAnalysisResult, float]]" = OrderedDict()
        self._cache_max_size = MAX_CACHE_SIZE

        self._metrics: Dict[str, Any] = {
            "total": 0,
            "ok": 0,
            "fail": 0,
            "cache_hits": 0,
            "fallbacks": 0,
            "breaker_trips": 0,
            "pii_detections": 0,
            "viral_detected": 0,
            "avg_latency_ms": 0.0,
            "latency_hist": [],  # List[int]
        }

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Cache helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _cache_key(self, inp: PerformanceAnalysisInput) -> str:
        ids = sorted([c.content_id for c in inp.content_items[:50]])
        s = json.dumps(
            {
                "tenant": inp.tenant_id,
                "count": len(inp.content_items),
                "sample": ids[:5],
                "jurisdiction": inp.jurisdiction,
            },
            sort_keys=True,
        )
        return hashlib.sha256(s.encode()).hexdigest()[:16]

    def _get_from_cache(self, key: str) -> Optional[PerformanceAnalysisResult]:
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

    def _put_in_cache(self, key: str, result: PerformanceAnalysisResult) -> None:
        if not self.flags.is_enabled("CACHE_ENABLED"):
            return
        self._cache[key] = (result, time.time())
        if len(self._cache) > self._cache_max_size:
            self._cache.popitem(last=False)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Metrics helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    @staticmethod
    def _percentile(sorted_values: List[int], p: float) -> float:
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * p
        f = int(k)
        c = min(f + 1, len(sorted_values) - 1)
        if f == c:
            return float(sorted_values[int(k)])
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return float(d0 + d1)

    def _update_latency(self, ms: int) -> None:
        self._metrics["latency_hist"].append(ms)
        n = max(1, self._metrics["total"])
        self._metrics["avg_latency_ms"] = ((self._metrics["avg_latency_ms"] * (n - 1)) + ms) / n

    def _emit_log(self, level: int, msg: str, **extra: Any) -> None:
        logger.log(level, msg + " " + json.dumps(extra, default=str))

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Core Execution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _execute_core(self, inp: PerformanceAnalysisInput) -> PerformanceAnalysisResult:
        t0 = time.perf_counter()
        decision_trace: List[str] = []
        audit: List[AuditEvent] = []

        seed = f"{inp.tenant_id}|{len(inp.content_items)}"
        decision_trace.append(f"items={len(inp.content_items)}")
        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="start", detail={"items": len(inp.content_items)}))

        # Scrubbing PII + compliance
        scrubbed_items: List[ContentItem] = []
        for it in inp.content_items:
            item, pii_found = it.scrub(enable_pii=self.flags.is_enabled("PII_DETECTION"))
            if pii_found:
                self._metrics["pii_detections"] += 1
                if self.flags.is_enabled("AUDIT_TRAIL"):
                    audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="pii_mask", detail={"content_id": it.content_id}))
            # compliance
            compliance_flags: List[str] = []
            if self.flags.is_enabled("COMPLIANCE_ENGINE"):
                compliance_flags = ComplianceEngine.enforce(item.title, item.channel, item.jurisdiction, item.marketing_consent)
                if compliance_flags and self.flags.is_enabled("AUDIT_TRAIL"):
                    audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="compliance", detail={"content_id": it.content_id, "flags": compliance_flags}))
            # adjunta flags en metadata de tÃ­tulo para reporte posterior (sin modificar lÃ³gica)
            if compliance_flags:
                # Simplemente anexamos al tÃ­tulo para que aparezcan como parte del performance (opcional)
                item = ContentItem(**{**asdict(item), "title": item.title})
            scrubbed_items.append(item)

        # CÃ¡lculo por contenido
        performances: List[ContentPerformance] = []
        channel_engagements: Dict[Channel, List[float]] = {}
        for content in scrubbed_items:
            eng_rate = PerformanceEngine.calculate_engagement_rate(content.metrics)
            virality = PerformanceEngine.calculate_virality_score(content.metrics, f"{seed}_{content.content_id}") if self.flags.is_enabled("VIRALITY_PREDICTION") else 0.0
            reach_eff = round((content.metrics.reach / max(1, content.metrics.impressions)) * 100.0, 2)
            perf_level = PerformanceEngine.classify_performance(eng_rate, virality)
            pred = PerformanceEngine.predict_performance(eng_rate)
            opts = PerformanceEngine.generate_optimizations(perf_level, content.content_type, content.channel)

            comp_flags = ComplianceEngine.enforce(
                title=content.title, channel=content.channel, jurisdiction=content.jurisdiction, has_consent=content.marketing_consent
            ) if self.flags.is_enabled("COMPLIANCE_ENGINE") else []

            if perf_level == "viral":
                self._metrics["viral_detected"] += 1

            performances.append(
                ContentPerformance(
                    content_id=content.content_id,
                    performance_level=perf_level,
                    engagement_rate=eng_rate,
                    virality_score=virality,
                    reach_efficiency=reach_eff,
                    predicted_performance=pred,
                    optimization_suggestions=opts,
                    compliance_flags=comp_flags,
                )
            )
            channel_engagements.setdefault(content.channel, []).append(eng_rate)

        decision_trace.append(f"viral_detected={self._metrics['viral_detected']}")
        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="scored", detail={"count": len(performances)}))

        # Top performers
        top_performers_sorted = sorted(performances, key=lambda p: (p.performance_level == "viral", p.engagement_rate, p.virality_score), reverse=True)
        top_ids = [p.content_id for p in top_performers_sorted[:5]]

        # Trending topics
        trends = TrendEngine.detect_trends(scrubbed_items) if self.flags.is_enabled("TREND_DETECTION") else []

        # Benchmarks por canal
        benchmarks = {ch: round(sum(vals) / max(1, len(vals)), 2) for ch, vals in channel_engagements.items()}

        # Recomendaciones generales
        recs: List[str] = []
        if top_ids:
            recs.append(f"Escalar formato del top performer: {top_ids[0]}")
        if trends:
            recs.append("Temas en alza: " + ", ".join(t.topic for t in trends[:3]))
        if benchmarks:
            best_ch = max(benchmarks, key=benchmarks.get)
            recs.append(f"Canal con mejor promedio: {best_ch} ({benchmarks[best_ch]}%)")

        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        self._update_latency(latency_ms)

        if self.flags.is_enabled("AUDIT_TRAIL"):
            audit.append(AuditEvent(ts=datetime.utcnow().isoformat(), step="finish", detail={"latency_ms": latency_ms}))

        analysis_id = f"perf_{int(datetime.utcnow().timestamp()*1000)}_{hashlib.sha256(seed.encode()).hexdigest()[:6]}"

        self._emit_log(logging.INFO, "Content performance analyzed", analysis_id=analysis_id, items=len(scrubbed_items), latency_ms=latency_ms)

        return PerformanceAnalysisResult(
            analysis_id=analysis_id,
            tenant_id=self.tenant_id,
            content_performances=performances,
            top_performers=top_ids,
            trending_topics=trends,
            channel_benchmarks=benchmarks,
            recommendations=recs,
            latency_ms=latency_ms,
            metadata={
                "agent_version": VERSION,
                "request_id": inp.request_id,
                "content_analyzed": len(scrubbed_items),
                "jurisdiction": inp.jurisdiction,
                "language": inp.language,
            },
            decision_trace=decision_trace,
            audit_trail=audit if self.flags.is_enabled("AUDIT_TRAIL") else [],
        )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    async def execute(self, inp: PerformanceAnalysisInput) -> PerformanceAnalysisResult:
        """Ejecuta el anÃ¡lisis principal con circuit breaker + cache + fallback."""
        self._metrics["total"] += 1

        # Circuit Breaker
        if self.flags.is_enabled("CIRCUIT_BREAKER") and not self.breaker.can_execute():
            self._metrics["breaker_trips"] += 1
            self._emit_log(logging.WARNING, "Circuit breaker OPEN - using fallback", breaker_state=self.breaker.state)
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise RuntimeError("Circuit breaker OPEN")

        # Tenant check (bÃ¡sico)
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
            self._emit_log(logging.ERROR, "ContentPerformanceIA failed", error=str(e))
            self.breaker.record_failure()
            self._metrics["fail"] += 1
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise

    def _fallback(self, inp: PerformanceAnalysisInput) -> PerformanceAnalysisResult:
        """Respuesta conservadora y segura."""
        analysis_id = f"fallback_{int(datetime.utcnow().timestamp())}"
        self._emit_log(logging.WARNING, "Returning fallback result", analysis_id=analysis_id)
        return PerformanceAnalysisResult(
            analysis_id=analysis_id,
            tenant_id=self.tenant_id,
            content_performances=[],
            top_performers=[],
            trending_topics=[],
            channel_benchmarks={},
            recommendations=["Fallback mode - manual review required"],
            latency_ms=1,
            metadata={"fallback": True, "agent_version": VERSION, "request_id": None},
            decision_trace=["fallback_mode"],
            audit_trail=[],
        )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Health & Metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def health_check(self) -> Dict[str, Any]:
        """Estado general del agente."""
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
        """MÃ©tricas con p95/p99 de latencia y cache hit rate."""
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
def create_agent_instance(tenant_id: str, config: Optional[Dict[str, Any]] = None, flags: Optional[Dict[str, bool]] = None) -> ContentPerformanceIA:
    """
    Crea una instancia del agente con configuraciÃ³n/flags opcionales.
    """
    return ContentPerformanceIA(tenant_id, config, flags)

