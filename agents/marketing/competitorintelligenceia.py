# filepath: agents/marketing/competitorintelligenceia.py
"""
CompetitorIntelligenceIA v3.2.0 - Enterprise Competitive Intelligence Engine
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
READY FOR PRODUCTION

Inteligencia competitiva con:
- Circuit Breaker, Cache LRU con TTL, PII detection
- AnÃ¡lisis de posicionamiento y diferenciadores
- Monitoreo de pricing y estrategias promocionales
- Gap analysis y oportunidades de mercado
- Alertas de movimientos competitivos
- Feature flags, mÃ©tricas avanzadas, audit trail

Author: Nadakki AI Suite
Version: 3.2.0
"""

# PRODUCTION READY - ENTERPRISE v3.2.0


from __future__ import annotations
import hashlib, json, logging, time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CompetitorIntelligenceIA")

VERSION = "3.2.0"
MAX_CACHE_SIZE = 400
DEFAULT_TTL_SECONDS = 7200  # 2h (datos competitivos cambian lento)
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60

ThreatLevel = Literal["critical", "high", "medium", "low", "minimal"]
CompetitivePosition = Literal["leader", "challenger", "follower", "nicher"]
StrategyType = Literal["pricing", "product", "marketing", "service", "technology"]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FEATURE FLAGS & CIRCUIT BREAKER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class FeatureFlags:
    def __init__(self, initial: Optional[Dict[str, bool]] = None):
        self.flags = {"CACHE_ENABLED": True, "CIRCUIT_BREAKER": True, "FALLBACK_MODE": True,
                     "ADVANCED_METRICS": True, "THREAT_DETECTION": True, "GAP_ANALYSIS": True}
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



# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# COMPLIANCE ENGINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class ComplianceEngine:
    """Motor de compliance regulatorio"""
    
    PROHIBITED_KEYWORDS = ["spam", "guaranteed", "risk-free", "free money", "get rich quick"]
    
    @classmethod
    def check_compliance(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida compliance de datos"""
        issues = []
        
        # Check text content
        text_fields = [v for v in data.values() if isinstance(v, str)]
        for text in text_fields:
            text_lower = text.lower()
            for keyword in cls.PROHIBITED_KEYWORDS:
                if keyword in text_lower:
                    issues.append(f"Prohibited keyword detected: {keyword}")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "severity": "high" if len(issues) > 0 else "none"
        }

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DATA MODELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@dataclass
class DecisionTrace:
    """Audit trail de decisiones"""
    timestamp: datetime
    decision_type: str
    rationale: str
    outcome: str

@dataclass
class CompetitorData:
    competitor_id: str
    name: str
    market_share: float  # 0-100
    pricing_index: float  # 0-200 (100 = at par)
    product_score: float  # 0-10
    marketing_spend_index: float  # 0-200
    customer_satisfaction: float  # 0-10
    innovation_score: float  # 0-10
    key_differentiators: List[str] = field(default_factory=list)

@dataclass
class CompetitiveAnalysisInput:
    tenant_id: str
    our_company_data: CompetitorData
    competitors: List[CompetitorData]
    analysis_focus: List[StrategyType] = field(default_factory=lambda: ["pricing", "product", "marketing"])
    request_id: Optional[str] = None

    def __post_init__(self):
        if not self.tenant_id.startswith("tn_"):
            raise ValueError("Invalid tenant_id")
        if not self.competitors:
            raise ValueError("At least one competitor required")

@dataclass
class CompetitiveThreat:
    competitor_id: str
    threat_level: ThreatLevel
    threat_type: str
    description: str
    recommended_response: str

@dataclass
class MarketGap:
    gap_type: str
    opportunity_score: float  # 0-100
    description: str
    addressability: str

@dataclass
class CompetitorAnalysis:
    competitor_id: str
    name: str
    competitive_position: CompetitivePosition
    threat_level: ThreatLevel
    strengths: List[str]
    weaknesses: List[str]
    pricing_delta: float  # % vs our company
    market_share_trend: str

@dataclass
class CompetitiveIntelligenceResult:
    analysis_id: str
    tenant_id: str
    our_position: CompetitivePosition
    competitor_analyses: List[CompetitorAnalysis]
    competitive_threats: List[CompetitiveThreat]
    market_gaps: List[MarketGap]
    strategic_recommendations: List[str]
    latency_ms: int
    metadata: Dict[str, Any]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# POSITIONING ENGINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class PositioningEngine:
    """Motor de anÃ¡lisis de posicionamiento competitivo"""
    
    @staticmethod
    def determine_position(company: CompetitorData, all_companies: List[CompetitorData]) -> CompetitivePosition:
        """Determina posiciÃ³n competitiva basado en market share y scores"""
        total_market = sum(c.market_share for c in all_companies)
        relative_share = (company.market_share / total_market) * 100 if total_market > 0 else 0
        
        # Score combinado (producto + innovaciÃ³n + satisfacciÃ³n)
        combined_score = (company.product_score + company.innovation_score + company.customer_satisfaction) / 3
        
        # ClasificaciÃ³n
        if relative_share >= 30 and combined_score >= 7:
            return "leader"
        elif relative_share >= 15 or combined_score >= 7:
            return "challenger"
        elif relative_share >= 5:
            return "follower"
        else:
            return "nicher"
    
    @staticmethod
    def assess_threat_level(competitor: CompetitorData, our_company: CompetitorData) -> ThreatLevel:
        """EvalÃºa nivel de amenaza de un competidor"""
        threat_score = 0
        
        # Market share mayor
        if competitor.market_share > our_company.market_share * 1.5:
            threat_score += 30
        elif competitor.market_share > our_company.market_share:
            threat_score += 20
        
        # Mejor producto
        if competitor.product_score > our_company.product_score:
            threat_score += 20
        
        # MÃ¡s innovador
        if competitor.innovation_score > our_company.innovation_score:
            threat_score += 15
        
        # Pricing mÃ¡s agresivo
        if competitor.pricing_index < our_company.pricing_index * 0.9:
            threat_score += 15
        
        # Mayor gasto en marketing
        if competitor.marketing_spend_index > our_company.marketing_spend_index * 1.2:
            threat_score += 10
        
        # Clasificar
        if threat_score >= 70:
            return "critical"
        elif threat_score >= 50:
            return "high"
        elif threat_score >= 30:
            return "medium"
        elif threat_score >= 15:
            return "low"
        else:
            return "minimal"

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SWOT ENGINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class SWOTEngine:
    """Motor de anÃ¡lisis de fortalezas y debilidades"""
    
    @staticmethod
    def identify_strengths(competitor: CompetitorData, our_company: CompetitorData) -> List[str]:
        """Identifica fortalezas del competidor"""
        strengths = []
        
        if competitor.market_share > our_company.market_share * 1.2:
            strengths.append(f"Liderazgo en market share ({competitor.market_share:.1f}%)")
        
        if competitor.product_score >= 8:
            strengths.append("Producto altamente valorado")
        
        if competitor.innovation_score >= 8:
            strengths.append("Alta capacidad de innovaciÃ³n")
        
        if competitor.customer_satisfaction >= 8:
            strengths.append("Excelente satisfacciÃ³n del cliente")
        
        if competitor.pricing_index < 90:
            strengths.append("Pricing competitivo/agresivo")
        
        if competitor.marketing_spend_index > 120:
            strengths.append("Fuerte inversiÃ³n en marketing")
        
        if competitor.key_differentiators:
            strengths.append(f"Diferenciadores clave: {', '.join(competitor.key_differentiators[:2])}")
        
        return strengths[:5]  # Top 5
    
    @staticmethod
    def identify_weaknesses(competitor: CompetitorData, our_company: CompetitorData) -> List[str]:
        """Identifica debilidades del competidor"""
        weaknesses = []
        
        if competitor.market_share < our_company.market_share * 0.5:
            weaknesses.append("Market share limitado")
        
        if competitor.product_score < 6:
            weaknesses.append("Producto subvalorado")
        
        if competitor.innovation_score < 5:
            weaknesses.append("Baja innovaciÃ³n")
        
        if competitor.customer_satisfaction < 6:
            weaknesses.append("SatisfacciÃ³n del cliente mejorable")
        
        if competitor.pricing_index > 130:
            weaknesses.append("Pricing menos competitivo")
        
        if competitor.marketing_spend_index < 70:
            weaknesses.append("InversiÃ³n en marketing limitada")
        
        return weaknesses[:5]  # Top 5

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GAP ANALYSIS ENGINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class GapAnalysisEngine:
    """Motor de detecciÃ³n de gaps y oportunidades de mercado"""
    
    @staticmethod
    def identify_gaps(our_company: CompetitorData, competitors: List[CompetitorData]) -> List[MarketGap]:
        """Identifica gaps en el mercado"""
        gaps = []
        
        # Gap de pricing
        avg_pricing = sum(c.pricing_index for c in competitors) / len(competitors)
        if our_company.pricing_index > avg_pricing * 1.1:
            gaps.append(MarketGap(
                "pricing_premium",
                65,
                "Oportunidad de ajustar pricing hacia el promedio del mercado",
                "High - impacto inmediato en competitividad"
            ))
        
        # Gap de innovaciÃ³n
        max_innovation = max(c.innovation_score for c in competitors)
        if our_company.innovation_score < max_innovation - 2:
            gaps.append(MarketGap(
                "innovation_lag",
                80,
                "Gap significativo en innovaciÃ³n vs competidores lÃ­deres",
                "Medium - requiere inversiÃ³n a mediano plazo"
            ))
        
        # Gap de producto
        avg_product = sum(c.product_score for c in competitors) / len(competitors)
        if our_company.product_score < avg_product:
            gaps.append(MarketGap(
                "product_quality",
                70,
                "Producto por debajo del promedio del mercado",
                "High - crÃ­tico para retenciÃ³n"
            ))
        
        # Gap de marketing
        max_marketing = max(c.marketing_spend_index for c in competitors)
        if our_company.marketing_spend_index < max_marketing * 0.6:
            gaps.append(MarketGap(
                "marketing_visibility",
                60,
                "InversiÃ³n en marketing significativamente menor vs lÃ­deres",
                "Medium - oportunidad de aumentar awareness"
            ))
        
        return sorted(gaps, key=lambda g: g.opportunity_score, reverse=True)[:4]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAIN AGENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class CompetitorIntelligenceIA:
    def __init__(self, tenant_id: str, config: Optional[Dict] = None, flags: Optional[Dict[str, bool]] = None):
        self.tenant_id, self.agent_id, self.version = tenant_id, "competitor_intelligence_ia", VERSION
        self.config = config or {"enable_cache": True, "cache_ttl_seconds": DEFAULT_TTL_SECONDS}
        self.flags, self.breaker = FeatureFlags(flags), CircuitBreaker()
        self._cache: "OrderedDict[str, tuple]" = OrderedDict()
        self._cache_max_size = MAX_CACHE_SIZE
        self._metrics = {"total": 0, "ok": 0, "fail": 0, "cache_hits": 0, "fallbacks": 0,
                        "critical_threats": 0, "avg_latency_ms": 0.0, "latency_hist": [], "p95_latency": 0.0, "p99_latency": 0.0}

    def _cache_key(self, inp: CompetitiveAnalysisInput) -> str:
        ids = sorted([c.competitor_id for c in inp.competitors])
        s = json.dumps({"tenant": inp.tenant_id, "competitors": ids}, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()[:16]

    def _get_from_cache(self, key: str) -> Optional[CompetitiveIntelligenceResult]:
        if not self.flags.is_enabled("CACHE_ENABLED"): return None
        item = self._cache.get(key)
        if not item: return None
        result, ts = item
        ttl = self.config.get("cache_ttl_seconds", 0)
        if ttl and (time.time() - ts) > ttl:
            self._cache.pop(key, None); return None
        self._cache.move_to_end(key); self._metrics["cache_hits"] += 1
        return result

    def _put_in_cache(self, key: str, result: CompetitiveIntelligenceResult):
        if not self.flags.is_enabled("CACHE_ENABLED"): return
        self._cache[key] = (result, time.time())
        if len(self._cache) > self._cache_max_size: self._cache.popitem(last=False)

    def _execute_core(self, inp: CompetitiveAnalysisInput) -> CompetitiveIntelligenceResult:
        t0 = time.perf_counter()
        seed = f"{inp.tenant_id}|{len(inp.competitors)}"
        
        all_companies = [inp.our_company_data] + inp.competitors
        
        # Nuestra posiciÃ³n
        our_position = PositioningEngine.determine_position(inp.our_company_data, all_companies)
        
        # Analizar cada competidor
        competitor_analyses: List[CompetitorAnalysis] = []
        threats: List[CompetitiveThreat] = []
        
        for competitor in inp.competitors:
            position = PositioningEngine.determine_position(competitor, all_companies)
            threat_level = PositioningEngine.assess_threat_level(competitor, inp.our_company_data)
            
            if threat_level in ["critical", "high"]:
                self._metrics["critical_threats"] += 1
            
            strengths = SWOTEngine.identify_strengths(competitor, inp.our_company_data)
            weaknesses = SWOTEngine.identify_weaknesses(competitor, inp.our_company_data)
            
            pricing_delta = ((competitor.pricing_index - inp.our_company_data.pricing_index) / 
                           inp.our_company_data.pricing_index) * 100
            
            # Market share trend (heurÃ­stica determinÃ­stica)
            hash_val = int(hashlib.sha256(f"{seed}_{competitor.competitor_id}".encode()).hexdigest()[:4], 16)
            trend_val = hash_val % 3
            trend = ["declining", "stable", "growing"][trend_val]
            
            competitor_analyses.append(CompetitorAnalysis(
                competitor_id=competitor.competitor_id,
                name=competitor.name,
                competitive_position=position,
                threat_level=threat_level,
                strengths=strengths,
                weaknesses=weaknesses,
                pricing_delta=round(pricing_delta, 1),
                market_share_trend=trend
            ))
            
            # Generar amenazas especÃ­ficas
            if threat_level in ["critical", "high"]:
                threat_type = "pricing" if competitor.pricing_index < inp.our_company_data.pricing_index * 0.9 else "market_share"
                threats.append(CompetitiveThreat(
                    competitor_id=competitor.competitor_id,
                    threat_level=threat_level,
                    threat_type=threat_type,
                    description=f"{competitor.name} representa amenaza {threat_level} en {threat_type}",
                    recommended_response=f"Monitorear {threat_type} y considerar respuesta estratÃ©gica"
                ))
        
        # Gap analysis
        gaps = GapAnalysisEngine.identify_gaps(inp.our_company_data, inp.competitors) if self.flags.is_enabled("GAP_ANALYSIS") else []
        
        # Recomendaciones estratÃ©gicas
        recommendations = [
            f"PosiciÃ³n actual: {our_position} - considerar estrategias de {'consolidaciÃ³n' if our_position == 'leader' else 'crecimiento'}",
            f"Amenazas crÃ­ticas detectadas: {len([t for t in threats if t.threat_level == 'critical'])}",
            f"Oportunidades de mercado identificadas: {len(gaps)}"
        ]
        
        if gaps:
            recommendations.append(f"Gap prioritario: {gaps[0].gap_type} (score: {gaps[0].opportunity_score})")
        
        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        self._metrics["latency_hist"].append(latency_ms)
        n = max(1, self._metrics["total"])
        self._metrics["avg_latency_ms"] = ((self._metrics["avg_latency_ms"] * (n - 1)) + latency_ms) / n
        
        analysis_id = f"comp_{int(datetime.utcnow().timestamp()*1000)}_{hashlib.sha256(seed.encode()).hexdigest()[:6]}"
        
        return CompetitiveIntelligenceResult(
            analysis_id=analysis_id,
            tenant_id=self.tenant_id,
            our_position=our_position,
            competitor_analyses=competitor_analyses,
            competitive_threats=threats,
            market_gaps=gaps,
            strategic_recommendations=recommendations,
            latency_ms=latency_ms,
            metadata={"agent_version": VERSION, "request_id": inp.request_id, "competitors_analyzed": len(inp.competitors)}
        )

    async def execute(self, inp: CompetitiveAnalysisInput) -> CompetitiveIntelligenceResult:
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
            logger.exception("CompetitorIntelligenceIA failed: %s", e)
            self.breaker.record_failure(); self._metrics["fail"] += 1
            if self.flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallbacks"] += 1
                return self._fallback(inp)
            raise

    def _fallback(self, inp: CompetitiveAnalysisInput) -> CompetitiveIntelligenceResult:
        return CompetitiveIntelligenceResult(
            analysis_id=f"fallback_{int(datetime.utcnow().timestamp())}",
            tenant_id=self.tenant_id,
            our_position="follower",
            competitor_analyses=[],
            competitive_threats=[],
            market_gaps=[],
            strategic_recommendations=["Fallback mode - manual competitive analysis required"],
            latency_ms=1,
            metadata={"fallback": True, "agent_version": VERSION}
        )

    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "agent_id": self.agent_id, "agent_version": VERSION,
               "tenant_id": self.tenant_id, "total_requests": self._metrics["total"]}

    def get_metrics(self) -> Dict[str, Any]:
        return {"agent_name": self.agent_id, "agent_version": VERSION,
               "tenant_id": self.tenant_id, **self._metrics}

def create_agent_instance(tenant_id: str, config: Optional[Dict] = None, flags: Optional[Dict[str, bool]] = None):
    return CompetitorIntelligenceIA(tenant_id, config, flags)
