"""
ContentGeneratorIA v3.2.0 - Enterprise Multi-Tenant Marketing Content Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
READY FOR PRODUCTION

Cambios clave vs 3.1.0:
- ✅ Scores por variante (CTR/brand) dependientes de variant_idx
- ✅ Cache LRU con TTL real (evicción por tiempo + LRU)
- ✅ Auto-remediación de compliance (professional → backup seguro)
- ✅ PII detectada → enmascarada en salida (emails, phones, SSN/CURP/CPF)
- ✅ Circuit Breaker get_status() sin efectos secundarios
- ✅ Compliance alinea verificación de longitud al límite por tipo
- ✅ Feature flags gobiernan ramas críticas (STRICT_COMPLIANCE, BACKUP_TEMPLATES, etc.)
- ✅ Métricas: autofix_ratio, fallback_activations, breaker_trips, p95/p99

Author: Nadakki AI Suite
License: Enterprise
Version: 3.2.0
"""

from __future__ import annotations
import hashlib
import logging
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Literal, Any, Tuple
import json

# ═══════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTS & ENUMS
# ═══════════════════════════════════════════════════════════════════════

VERSION = "3.2.0"
MAX_CACHE_SIZE = 1000
DEFAULT_TIMEOUT_MS = 5000
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds

ContentType = Literal["ad_copy", "email_subject", "email_body", "landing_headline", "social_post", "sms"]
AudienceSegment = Literal["high_value", "mid_value", "low_value", "prospect", "dormant"]
BrandTone = Literal["professional", "friendly", "premium", "urgent", "educational"]
Language = Literal["es", "en", "pt"]
Jurisdiction = Literal["US", "MX", "BR", "CO", "EU", "DO"]

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════════════════════

class FeatureFlags:
    """Feature flags para rollout y control fino."""
    def __init__(self, initial: Optional[Dict[str, bool]] = None):
        self.flags = {
            "STRICT_COMPLIANCE": True,   # compliance >=0.8 & sin flags
            "PII_DETECTION": True,       # detectar y enmascarar PII
            "CACHE_ENABLED": True,
            "AUDIT_TRAIL": True,
            "CIRCUIT_BREAKER": True,
            "FALLBACK_MODE": True,
            "ADVANCED_METRICS": True,
            "MULTI_REGION": False,
            "BACKUP_TEMPLATES": True
        }
        if initial:
            self.flags.update(initial)

    def is_enabled(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)

    def set_flag(self, flag_name: str, enabled: bool):
        self.flags[flag_name] = enabled
        logger.info(f"Feature flag {flag_name} set to {enabled}")

# ═══════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════════════

class CircuitBreaker:
    """Patrón Circuit Breaker con estados CLOSED/OPEN/HALF_OPEN."""
    def __init__(self, failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                 timeout: int = CIRCUIT_BREAKER_TIMEOUT):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if (time.time() - (self.last_failure_time or 0)) > self.timeout:
                # transición a HALF_OPEN (solo en ejecución real, no en get_status)
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        return True

    def record_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = None

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPEN after {self.failures} failures")

    def get_status(self) -> Dict[str, Any]:
        # ⚠️ Sin efectos secundarios: no invocar can_execute() aquí
        if self.state == "OPEN":
            can_exec = (time.time() - (self.last_failure_time or 0)) > self.timeout
        else:
            can_exec = True
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure_time": self.last_failure_time,
            "can_execute": can_exec
        }

# ═══════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class PersonalizationData:
    first_name: Optional[str] = None
    product_name: Optional[str] = None
    value: Optional[float] = None
    def __post_init__(self):
        if self.first_name:
            self.first_name = re.sub(r"[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]", "", self.first_name)[:50]
        if self.product_name:
            self.product_name = re.sub(r"[<>{}]", "", self.product_name)[:100]

@dataclass
class ContentGenerationInput:
    tenant_id: str
    content_type: ContentType
    audience_segment: AudienceSegment
    brand_tone: BrandTone
    key_message: str
    language: Language = "es"
    jurisdiction: Jurisdiction = "MX"
    personalization_data: Optional[PersonalizationData] = None
    variant_count: int = 2
    request_id: Optional[str] = None
    def __post_init__(self):
        if not re.match(r"^tn_[a-z0-9_]{8,32}$", self.tenant_id):
            raise ValueError(f"Invalid tenant_id format: {self.tenant_id}")
        if not 10 <= len(self.key_message) <= 500:
            raise ValueError(f"key_message length must be 10-500 chars, got {len(self.key_message)}")
        if not 1 <= self.variant_count <= 5:
            raise ValueError(f"variant_count must be 1-5, got {self.variant_count}")
        if self.request_id and not re.match(r"^req_[a-z0-9]{16}$", self.request_id):
            raise ValueError(f"Invalid request_id format: {self.request_id}")

@dataclass
class VariantScores:
    compliance: float
    brand_alignment: float
    estimated_ctr: float
    readability: float

@dataclass
class ContentVariant:
    variant_id: str
    content: str
    length: int
    scores: VariantScores
    risk_flags: List[str] = field(default_factory=list)
    pii_detected: bool = False
    def to_dict(self) -> Dict:
        return {**asdict(self), "scores": asdict(self.scores)}

@dataclass
class ComplianceSummary:
    passed: bool
    jurisdiction_rules_applied: List[str]
    warnings: List[str] = field(default_factory=list)

@dataclass
class AuditTrail:
    template_version: str
    config_hash: str
    decision_trace: List[str]
    reason_codes: List[str]

@dataclass
class ContentGenerationOutput:
    tenant_id: str
    generation_id: str
    variants: List[ContentVariant]
    recommended_variant: str
    compliance_summary: ComplianceSummary
    audit_trail: AuditTrail
    metadata: Dict[str, Any]
    def to_dict(self) -> Dict:
        return {
            "tenant_id": self.tenant_id,
            "generation_id": self.generation_id,
            "variants": [v.to_dict() for v in self.variants],
            "recommended_variant": self.recommended_variant,
            "compliance_summary": asdict(self.compliance_summary),
            "audit_trail": asdict(self.audit_trail),
            "metadata": self.metadata,
        }

# ═══════════════════════════════════════════════════════════════════════
# COMPLIANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════

class ComplianceEngine:
    PROHIBITED_TERMS = {
        "US": [
            r"\b(guaranteed|guarantee)\s+(approval|loan|credit)\b",
            r"\brisk[\s-]?free\b",
            r"\binstant\s+approval\b",
            r"\beasy\s+money\b",
            r"\b100%\s+(guaranteed|approved|safe)\b",
        ],
        "MX": [
            r"\bgarantizad[oa]s?\s+(préstamo|crédito|aprobación)\b",
            r"\bsin\s+riesgo\b",
            r"\baprobación\s+inmediata\b",
            r"\bdinero\s+fácil\b",
            r"\b100%\s+(garantizado|seguro)\b",
            r"\bsin\s+verificación\b",
        ],
        "BR": [
            r"\bgarantid[oa]\b",
            r"\bsem\s+risco\b",
            r"\baprovação\s+imediata\b",
            r"\bdinheiro\s+fácil\b",
        ],
        "EU": [
            r"\bguaranteed\b",
            r"\brisk[\s-]?free\b",
            r"\bno\s+credit\s+check\b",
        ],
        "CO": [
            r"\bgarantizad[oa]\b",
            r"\bsin\s+verificación\b",
            r"\bdinero\s+rápido\b",
        ],
        "DO": [
            r"\bgarantizad[oa]\b",
            r"\bsin\s+buro\b",
            r"\baprobación\s+automática\b",
        ],
    }
    UNVERIFIABLE_CLAIMS = {
        "ALL": [
            r"\b(mejor|best|melhor)\s+(opción|option|opção)\b",
            r"\b(más\s+barato|cheapest|mais\s+barato)\b",
            r"\b(#1|número\s+1|number\s+one)\b",
            r"\b(el\s+único|the\s+only|o\s+único)\b",
        ]
    }
    PII_PATTERNS = [
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
        (r"\b[A-Z]{4}\d{6}[HM]\w{5}\b", "CURP"),
        (r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "CPF"),
        (r"\b\d{10}\b", "PHONE"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "EMAIL"),
    ]

    @classmethod
    def check_compliance(cls, content: str, jurisdiction: Jurisdiction,
                         max_length_limit: int) -> Tuple[float, List[str]]:
        score = 1.0
        flags: List[str] = []
        for pattern in cls.PROHIBITED_TERMS.get(jurisdiction, []):
            if re.search(pattern, content, re.IGNORECASE):
                flags.append(f"prohibited_term:{pattern[:30]}")
                score -= 0.30
        for pattern in cls.UNVERIFIABLE_CLAIMS["ALL"]:
            if re.search(pattern, content, re.IGNORECASE):
                flags.append(f"unverifiable_claim:{pattern[:30]}")
                score -= 0.20
        if len(content) > max_length_limit:
            flags.append("exceeds_max_length")
            score -= 0.10
        return max(0.0, score), flags

    @classmethod
    def detect_pii(cls, content: str) -> Tuple[bool, List[str]]:
        found: List[str] = []
        for pattern, ptype in cls.PII_PATTERNS:
            if re.search(pattern, content):
                found.append(ptype)
        return len(found) > 0, found

# ═══════════════════════════════════════════════════════════════════════
# TEMPLATE ENGINE
# ═══════════════════════════════════════════════════════════════════════

class TemplateEngine:
    TEMPLATES = {
        "es": {
            "professional": {
                "adjectives": ["confiable", "seguro", "eficiente", "profesional", "transparente"],
                "cta_patterns": ["Solicite información", "Conozca más detalles", "Descubra cómo calificar",
                                 "Consulte con un experto", "Evalúe sus opciones"],
                "structure": "{hook} {benefit}. {cta}."
            },
            "friendly": {
                "adjectives": ["sencillo", "cercano", "práctico", "ágil", "accesible"],
                "cta_patterns": ["Hablemos", "Te ayudamos", "Comencemos juntos", "Conversemos", "Estamos para ti"],
                "structure": "{hook}. {benefit}. {cta}."
            },
            "premium": {
                "adjectives": ["exclusivo", "premium", "privilegiado", "personalizado", "elite"],
                "cta_patterns": ["Acceda ahora", "Experimente la diferencia", "Únase al selecto grupo",
                                 "Descubra su oferta exclusiva", "Aproveche su estatus"],
                "structure": "{hook} — {benefit}. {cta}."
            },
            "urgent": {
                "adjectives": ["limitado", "urgente", "oportuno", "inmediato", "temporal"],
                "cta_patterns": ["Actúe ahora", "Oferta por tiempo limitado", "No espere más",
                                 "Aproveche hoy", "Última oportunidad"],
                "structure": "¡{hook}! {benefit}. {cta}."
            },
            "educational": {
                "adjectives": ["informativo", "claro", "educativo", "guiado", "explicado"],
                "cta_patterns": ["Aprenda más", "Descubra cómo funciona", "Conozca los detalles",
                                 "Infórmese mejor", "Entienda sus opciones"],
                "structure": "{hook}. {benefit}. {cta}."
            },
        },
        "en": {
            "professional": {
                "adjectives": ["reliable", "secure", "efficient", "professional", "transparent"],
                "cta_patterns": ["Request information", "Learn more", "Discover how to qualify",
                                 "Consult an expert", "Evaluate your options"],
                "structure": "{hook} {benefit}. {cta}."
            },
            "friendly": {
                "adjectives": ["simple", "friendly", "practical", "quick", "accessible"],
                "cta_patterns": ["Let's talk", "We'll help you", "Let's get started",
                                 "Chat with us", "We're here for you"],
                "structure": "{hook}. {benefit}. {cta}."
            },
        },
        "pt": {
            "professional": {
                "adjectives": ["confiável", "seguro", "eficiente", "profissional", "transparente"],
                "cta_patterns": ["Solicite informações", "Saiba mais", "Descubra como qualificar",
                                 "Consulte um especialista", "Avalie suas opções"],
                "structure": "{hook} {benefit}. {cta}."
            },
        },
    }

    BACKUP_TEMPLATES = {
        "es": {
            "ad_copy": "Soluciones financieras confiables. Contacte a un especialista.",
            "email_subject": "Información sobre servicios financieros",
            "landing_headline": "Opciones financieras seguras para usted",
            "social_post": "💼 Conozca nuestras opciones financieras. ¡Estamos para ayudarle!",
            "sms": "Información de servicios financieros. Contáctenos."
        },
        "en": {
            "ad_copy": "Discover our financial solutions. Speak with an expert.",
            "email_subject": "Information about our financial services",
            "landing_headline": "Reliable financial solutions for you",
            "social_post": "💼 Learn about our financial options. We're here to help!",
            "sms": "Info about financial services. Contact us."
        }
    }

    MAX_LENGTHS = {
        "ad_copy": 110,
        "email_subject": 60,
        "email_body": 500,
        "landing_headline": 80,
        "social_post": 280,
        "sms": 160,
    }

    @classmethod
    def get_template(cls, language: Language, tone: BrandTone) -> Dict:
        lang_templates = cls.TEMPLATES.get(language, cls.TEMPLATES["es"])
        return lang_templates.get(tone, lang_templates["professional"])

    @classmethod
    def get_backup_template(cls, language: Language, content_type: ContentType) -> str:
        lang_templates = cls.BACKUP_TEMPLATES.get(language, cls.BACKUP_TEMPLATES["es"])
        return lang_templates.get(content_type, "Solución financiera confiable. Contáctenos.")

    @classmethod
    def get_max_length(cls, content_type: ContentType) -> int:
        return cls.MAX_LENGTHS.get(content_type, 140)

# ═══════════════════════════════════════════════════════════════════════
# FALLBACK CONTENT GENERATOR
# ═══════════════════════════════════════════════════════════════════════

class FallbackContentGenerator:
    """Contenido seguro en modo fallback (sin PII ni claims)."""
    SAFE_TEMPLATES = TemplateEngine.BACKUP_TEMPLATES

    @classmethod
    def generate_fallback_content(cls, input_data: ContentGenerationInput) -> ContentGenerationOutput:
        language = input_data.language
        content_type = input_data.content_type
        content = cls.SAFE_TEMPLATES.get(language, cls.SAFE_TEMPLATES["es"]).get(
            content_type, cls.SAFE_TEMPLATES["es"]["ad_copy"]
        )
        variant = ContentVariant(
            variant_id="fallback_1",
            content=content,
            length=len(content),
            scores=VariantScores(compliance=1.0, brand_alignment=0.70, estimated_ctr=0.10, readability=80.0),
            risk_flags=[],
            pii_detected=False,
        )
        compliance_summary = ComplianceSummary(
            passed=True,
            jurisdiction_rules_applied=["fallback_safe_mode"],
            warnings=["Generated in fallback mode due to system issues"],
        )
        audit_trail = AuditTrail(
            template_version=f"fallback_{VERSION}",
            config_hash="fallback_mode",
            decision_trace=["fallback_activation", "safe_content_generated"],
            reason_codes=["system_failure", "fallback_activated"],
        )
        return ContentGenerationOutput(
            tenant_id=input_data.tenant_id,
            generation_id=f"fallback_{int(datetime.utcnow().timestamp())}",
            variants=[variant],
            recommended_variant="fallback_1",
            compliance_summary=compliance_summary,
            audit_trail=audit_trail,
            metadata={
                "fallback_mode": True,
                "latency_ms": 1,
                "agent_version": VERSION,
                "request_id": input_data.request_id,
                "execution_mode": "fallback"
            },
        )

# ═══════════════════════════════════════════════════════════════════════
# MAIN AGENT
# ═══════════════════════════════════════════════════════════════════════

class ContentGeneratorIA:
    """Agente enterprise de generación de contenido marketing para instituciones financieras"""

    def __init__(self, tenant_id: str, config: Optional[Dict[str, Any]] = None,
                 flags: Optional[Dict[str, bool]] = None):
        self.tenant_id = tenant_id
        self.agent_id = "content_generator_ia"
        self.version = VERSION
        self.config = config or self._load_default_config()
        self.feature_flags = FeatureFlags(flags)

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker()

        # Cache LRU con TTL
        # Dict[str, Tuple[ContentGenerationOutput, float(timestamp)]]
        self._cache: "OrderedDict[str, Tuple[ContentGenerationOutput, float]]" = OrderedDict()
        self._cache_max_size = MAX_CACHE_SIZE

        # Métricas internas
        self._metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "compliance_failures": 0,
            "pii_detections": 0,
            "fallback_activations": 0,
            "circuit_breaker_trips": 0,
            "latency_history": [],
            "avg_latency_ms": 0.0,
            "autofix_count": 0
        }

        logger.info(
            f"ContentGeneratorIA initialized: tenant={tenant_id}, version={VERSION}",
            extra={"tenant_id": tenant_id, "agent_version": VERSION},
        )

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "enable_cache": True,
            "cache_ttl_seconds": 3600,
            "max_retries": 2,
            "timeout_ms": DEFAULT_TIMEOUT_MS,
            "default_language": "es",
            "default_jurisdiction": "MX",
            "audit_all_generations": True,
            "strict_compliance": True,
            "enable_circuit_breaker": True,
            "enable_fallback": True,
        }

    # --------------- Cache helpers (TTL + LRU) ---------------
    def _generate_cache_key(self, input_data: ContentGenerationInput) -> str:
        key_components = [
            self.tenant_id,
            input_data.content_type,
            input_data.audience_segment,
            input_data.brand_tone,
            input_data.key_message,
            input_data.language,
            input_data.jurisdiction,
            str(input_data.variant_count),
        ]
        key_str = "|".join(key_components)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def _get_from_cache(self, cache_key: str) -> Optional[ContentGenerationOutput]:
        if not (self.config.get("enable_cache", True) and self.feature_flags.is_enabled("CACHE_ENABLED")):
            return None
        item = self._cache.get(cache_key)
        if not item:
            return None
        output, ts = item
        ttl = self.config.get("cache_ttl_seconds", 0)
        if ttl and (time.time() - ts) > ttl:
            # expirado
            self._cache.pop(cache_key, None)
            return None
        self._cache.move_to_end(cache_key)
        self._metrics["cache_hits"] += 1
        return output

    def _put_in_cache(self, cache_key: str, output: ContentGenerationOutput):
        if not (self.config.get("enable_cache", True) and self.feature_flags.is_enabled("CACHE_ENABLED")):
            return
        self._cache[cache_key] = (output, time.time())
        if len(self._cache) > self._cache_max_size:
            self._cache.popitem(last=False)

    # --------------- Utils ---------------
    def _deterministic_hash(self, seed: str, max_val: int) -> int:
        hash_bytes = hashlib.sha256(f"{self.tenant_id}|{seed}".encode()).digest()
        return int.from_bytes(hash_bytes[:4], "big") % max_val

    def _select_template_elements(self, template: Dict, seed: str, variant_idx: int) -> Tuple[str, str]:
        adjectives = template["adjectives"]
        cta_patterns = template["cta_patterns"]
        hash_seed = f"{seed}_v{variant_idx}"
        adj_idx = self._deterministic_hash(hash_seed, len(adjectives))
        cta_idx = self._deterministic_hash(hash_seed + "_cta", len(cta_patterns))
        return adjectives[adj_idx], cta_patterns[cta_idx]

    def _build_content(
        self,
        template: Dict,
        adjective: str,
        cta: str,
        key_message: str,
        personalization: Optional[PersonalizationData],
        content_type: ContentType,
    ) -> str:
        hook = key_message
        if personalization and personalization.first_name:
            hook = f"{personalization.first_name}, {key_message.lower()}"
        benefit = f"solución {adjective}"
        if personalization and personalization.product_name:
            benefit = f"{personalization.product_name} {adjective}"
        structure = template.get("structure", "{hook}. {benefit}. {cta}.")
        content = structure.format(hook=hook, benefit=benefit, cta=cta)
        max_length = TemplateEngine.get_max_length(content_type)
        if len(content) > max_length:
            content = content[: max_length - 1] + "…"
        return content

    def _calculate_readability(self, content: str) -> float:
        words = len(content.split())
        sentences = max(1, content.count(".") + content.count("!") + content.count("?"))
        vowels = "aeiouáéíóúAEIOUÁÉÍÓÚ"
        syllables = 0
        for w in content.split():
            prev = False
            cnt = 0
            for ch in w:
                is_v = ch in vowels
                if is_v and not prev:
                    cnt += 1
                prev = is_v
            syllables += max(1, cnt)
        if words == 0:
            return 0.0
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0.0, min(100.0, score))

    # --- PII masking simple ---
    def _mask_pii_text(self, text: str) -> str:
        # Emails
        text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email_masked]", text)
        # Phones
        text = re.sub(r"\b(\+?\d[\d\-\s]{7,}\d)\b", "[phone_masked]", text)
        # SSN/CURP/CPF
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[ssn_masked]", text)
        text = re.sub(r"\b[A-Z]{4}\d{6}[HM]\w{5}\b", "[curp_masked]", text)
        text = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[cpf_masked]", text)
        return text

    # --------------- Variant Generation ---------------
    def _generate_variant(
        self,
        input_data: ContentGenerationInput,
        variant_idx: int,
        seed: str,
        template: Dict,
        decision_trace: List[str],
        reason_codes: List[str],
    ) -> ContentVariant:
        adjective, cta = self._select_template_elements(template, seed, variant_idx)
        content = self._build_content(
            template=template,
            adjective=adjective,
            cta=cta,
            key_message=input_data.key_message,
            personalization=input_data.personalization_data,
            content_type=input_data.content_type,
        )

        # Compliance inicial
        max_len = TemplateEngine.get_max_length(input_data.content_type)
        compliance_score, compliance_flags = ComplianceEngine.check_compliance(
            content, input_data.jurisdiction, max_len
        )

        # PII detection + masking
        has_pii, pii_types = ComplianceEngine.detect_pii(content)
        if has_pii and self.feature_flags.is_enabled("PII_DETECTION"):
            self._metrics["pii_detections"] += 1
            reason_codes.append(f"pii_detected:{','.join(pii_types)}")
            content = self._mask_pii_text(content)
            # Re-evaluar compliance tras masking
            compliance_score, compliance_flags = ComplianceEngine.check_compliance(
                content, input_data.jurisdiction, max_len
            )

        # Auto-remediación si es requerido
        autofixed_here = False
        if self.feature_flags.is_enabled("STRICT_COMPLIANCE"):
            must_fix = compliance_score < 0.8 or bool(compliance_flags)
            if must_fix:
                # 1) degradar a professional
                safe_tpl = TemplateEngine.get_template(input_data.language, "professional")
                content2 = self._build_content(
                    template=safe_tpl,
                    adjective=adjective,
                    cta=cta,
                    key_message=input_data.key_message,
                    personalization=input_data.personalization_data,
                    content_type=input_data.content_type,
                )
                c2, f2 = ComplianceEngine.check_compliance(content2, input_data.jurisdiction, max_len)
                if c2 >= 0.8 and not f2:
                    content, compliance_score, compliance_flags = content2, c2, f2
                    decision_trace.append(f"var_{variant_idx+1}.fallback=professional")
                    reason_codes.append("autofix:professional")
                    autofixed_here = True
                elif self.feature_flags.is_enabled("BACKUP_TEMPLATES"):
                    # 2) último recurso: backup seguro
                    safe_text = TemplateEngine.get_backup_template(input_data.language, input_data.content_type)
                    content, compliance_score, compliance_flags = safe_text, 1.0, []
                    decision_trace.append(f"var_{variant_idx+1}.fallback=backup_template")
                    reason_codes.append("autofix:backup_template")
                    autofixed_here = True

        if autofixed_here:
            self._metrics["autofix_count"] += 1

        # Scores VARIANT-DEPENDENT (semilla incluye variant_idx)
        seed_v = f"{seed}|v{variant_idx}"
        brand_alignment = round(0.75 + (self._deterministic_hash(f"{seed_v}_brand", 100) / 400), 3)
        estimated_ctr = round(0.10 + (self._deterministic_hash(f"{seed_v}_ctr", 100) / 500), 3)
        readability = self._calculate_readability(content)

        # Track compliance failures (post-fix)
        if compliance_score < 0.8:
            self._metrics["compliance_failures"] += 1
            reason_codes.append(f"low_compliance:var_{variant_idx+1}")

        return ContentVariant(
            variant_id=f"var_{variant_idx+1}",
            content=content,
            length=len(content),
            scores=VariantScores(
                compliance=compliance_score,
                brand_alignment=brand_alignment,
                estimated_ctr=estimated_ctr,
                readability=readability,
            ),
            risk_flags=compliance_flags,
            pii_detected=has_pii,
        )

    # --------------- Core execution (separable para manejo de errores) ---------------
    def _execute_core(self, input_data: ContentGenerationInput, execution_mode: str = "normal") -> ContentGenerationOutput:
        start_time = time.perf_counter()

        cache_key = self._generate_cache_key(input_data)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info(f"Returning cached result: {cache_key}", extra={"tenant_id": self.tenant_id})
            return cached

        decision_trace: List[str] = [f"execution_mode:{execution_mode}"]
        reason_codes: List[str] = []

        seed = f"{input_data.tenant_id}_{input_data.content_type}_{input_data.key_message[:30]}"
        decision_trace.append(f"seed_generated:length={len(seed)}")

        template = TemplateEngine.get_template(input_data.language, input_data.brand_tone)
        decision_trace.append(f"template_selected:{input_data.language}_{input_data.brand_tone}")

        variants: List[ContentVariant] = []
        for i in range(input_data.variant_count):
            v = self._generate_variant(input_data, i, seed, template, decision_trace, reason_codes)
            variants.append(v)
            decision_trace.append(f"variant_{i+1}_generated:length={v.length},compliance={v.scores.compliance},flags={len(v.risk_flags)}")

        # Ranking: 50% compliance, 30% CTR, 20% brand
        def rank(v: ContentVariant) -> float:
            return v.scores.compliance * 0.5 + v.scores.estimated_ctr * 0.3 + v.scores.brand_alignment * 0.2

        recommended = max(variants, key=rank)
        decision_trace.append(f"recommended:{recommended.variant_id}")

        all_passed = all(v.scores.compliance >= 0.8 and not v.risk_flags for v in variants) if \
            self.feature_flags.is_enabled("STRICT_COMPLIANCE") else all(v.scores.compliance >= 0.7 for v in variants)

        jurisdiction_rules = [
            f"prohibited_terms:{input_data.jurisdiction}",
            "unverifiable_claims:ALL",
            "pii_detection:ALL",
        ]
        warnings = []
        if not all_passed:
            warnings.append("Some variants did not pass strict compliance")

        compliance_summary = ComplianceSummary(
            passed=all_passed,
            jurisdiction_rules_applied=jurisdiction_rules,
            warnings=warnings,
        )

        config_str = json.dumps(self.config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        audit_trail = AuditTrail(
            template_version=VERSION, config_hash=config_hash,
            decision_trace=decision_trace, reason_codes=reason_codes
        )

        timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
        gen_hash = hashlib.sha256(seed.encode()).hexdigest()[:8]
        generation_id = f"gen_{timestamp_ms}_{gen_hash}"

        latency_ms = max(1, int((time.perf_counter() - start_time) * 1000))
        self._metrics["latency_history"].append(latency_ms)
        # EWMA simple
        tr = max(1, self._metrics["total_requests"])
        self._metrics["avg_latency_ms"] = ((self._metrics["avg_latency_ms"] * (tr - 1)) + latency_ms) / tr

        metadata = {
            "latency_ms": latency_ms,
            "cache_hit": False,
            "agent_version": VERSION,
            "request_id": input_data.request_id,
            "execution_mode": execution_mode,
            "autofix_ratio": round(self._metrics["autofix_count"] / max(1, len(variants)), 3)
        }

        output = ContentGenerationOutput(
            tenant_id=self.tenant_id,
            generation_id=generation_id,
            variants=variants,
            recommended_variant=recommended.variant_id,
            compliance_summary=compliance_summary,
            audit_trail=audit_trail,
            metadata=metadata,
        )

        self._put_in_cache(cache_key, output)

        logger.info(
            f"Content generated: {generation_id}, variants={len(variants)}, latency={latency_ms}ms",
            extra={
                "tenant_id": self.tenant_id,
                "generation_id": generation_id,
                "latency_ms": latency_ms,
                "compliance_passed": compliance_summary.passed,
                "execution_mode": execution_mode,
            },
        )
        return output

    # --------------- Public API ---------------
    async def execute(self, input_data: ContentGenerationInput) -> ContentGenerationOutput:
        self._metrics["total_requests"] += 1

        # Circuit breaker gate
        if (self.config.get("enable_circuit_breaker", True)
                and self.feature_flags.is_enabled("CIRCUIT_BREAKER")
                and not self.circuit_breaker.can_execute()):
            self._metrics["circuit_breaker_trips"] += 1
            logger.warning(
                f"Circuit breaker OPEN, using fallback for tenant {self.tenant_id}",
                extra={"tenant_id": self.tenant_id, "circuit_breaker_state": self.circuit_breaker.state},
            )
            if self.feature_flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallback_activations"] += 1
                return FallbackContentGenerator.generate_fallback_content(input_data)
            raise RuntimeError("Circuit breaker is OPEN and fallback mode is disabled")

        try:
            if input_data.tenant_id != self.tenant_id:
                raise ValueError(f"Tenant mismatch: input={input_data.tenant_id}, agent={self.tenant_id}")

            result = self._execute_core(input_data)
            self.circuit_breaker.record_success()
            self._metrics["successful_requests"] += 1
            return result

        except ValueError as e:
            self.circuit_breaker.record_failure()
            self._metrics["failed_requests"] += 1
            logger.warning(
                f"Validation error, falling back to safe defaults: {e}",
                extra={"tenant_id": self.tenant_id, "error_type": "validation_error"},
            )
            if self.feature_flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallback_activations"] += 1
                # Safe defaults execution
                safe_input = ContentGenerationInput(
                    tenant_id=input_data.tenant_id,
                    content_type=input_data.content_type,
                    audience_segment="mid_value",
                    brand_tone="professional",
                    key_message="Soluciones financieras confiables",
                    language=input_data.language,
                    jurisdiction=input_data.jurisdiction,
                    variant_count=1,
                    request_id=input_data.request_id,
                )
                return self._execute_core(safe_input, execution_mode="safe_defaults_mode")
            raise

        except Exception as e:
            self.circuit_breaker.record_failure()
            self._metrics["failed_requests"] += 1
            logger.error(
                f"Content generation failed: {str(e)}",
                exc_info=True,
                extra={"tenant_id": self.tenant_id, "error_type": "critical_error"},
            )
            if self.feature_flags.is_enabled("FALLBACK_MODE"):
                self._metrics["fallback_activations"] += 1
                return FallbackContentGenerator.generate_fallback_content(input_data)
            raise RuntimeError(f"Content generation failed: {str(e)}") from e

    # --------------- Health & Metrics ---------------
    def health_check(self) -> Dict[str, Any]:
        base = {
            "status": "healthy",
            "agent_id": self.agent_id,
            "agent_version": VERSION,
            "tenant_id": self.tenant_id,
            "cache_size": len(self._cache),
            "total_requests": self._metrics["total_requests"],
            "success_rate": round(self._metrics["successful_requests"] / max(1, self._metrics["total_requests"]), 3),
        }
        if self.feature_flags.is_enabled("ADVANCED_METRICS"):
            base.update({
                "circuit_breaker": self.circuit_breaker.get_status(),
                "feature_flags": self.feature_flags.flags.copy(),
                "avg_latency_ms": round(self._metrics["avg_latency_ms"], 2),
                "fallback_activations": self._metrics["fallback_activations"],
            })
        return base

    def _calculate_percentile_latency(self, p: int) -> float:
        hist = self._metrics["latency_history"]
        if not hist:
            return 0.0
        s = sorted(hist)
        idx = (p / 100) * (len(s) - 1)
        if idx.is_integer():
            return s[int(idx)]
        lower = s[int(idx)]
        upper = s[int(idx) + 1]
        return lower + (upper - lower) * (idx - int(idx))

    def get_metrics(self) -> Dict[str, Any]:
        cache_hit_rate = self._metrics["cache_hits"] / max(1, self._metrics["total_requests"])
        success_rate = self._metrics["successful_requests"] / max(1, self._metrics["total_requests"])
        data = {
            "agent_name": self.agent_id,
            "agent_version": VERSION,
            "tenant_id": self.tenant_id,
            "total_requests": self._metrics["total_requests"],
            "successful_requests": self._metrics["successful_requests"],
            "failed_requests": self._metrics["failed_requests"],
            "success_rate": round(success_rate, 3),
            "cache_hits": self._metrics["cache_hits"],
            "cache_hit_rate": round(cache_hit_rate, 3),
            "compliance_failures": self._metrics["compliance_failures"],
            "pii_detections": self._metrics["pii_detections"],
            "fallback_activations": self._metrics["fallback_activations"],
            "circuit_breaker_trips": self._metrics["circuit_breaker_trips"],
            "avg_latency_ms": round(self._metrics["avg_latency_ms"], 2),
            "cache_size": len(self._cache),
            "autofix_ratio": round(self._metrics["autofix_count"] / max(1, self._metrics["total_requests"]), 3),
        }
        if self.feature_flags.is_enabled("ADVANCED_METRICS") and self._metrics["latency_history"]:
            data.update({
                "p95_latency_ms": self._calculate_percentile_latency(95),
                "p99_latency_ms": self._calculate_percentile_latency(99),
                "max_latency_ms": max(self._metrics["latency_history"]),
                "min_latency_ms": min(self._metrics["latency_history"]),
            })
        return data

    # --------------- Management ---------------
    def clear_cache(self):
        self._cache.clear()
        logger.info(f"Cache cleared for tenant {self.tenant_id}")

    def set_feature_flag(self, flag_name: str, enabled: bool):
        self.feature_flags.set_flag(flag_name, enabled)

    def get_feature_flags(self) -> Dict[str, bool]:
        return self.feature_flags.flags.copy()

# ═══════════════════════════════════════════════════════════════════════
# FACTORY & INFO
# ═══════════════════════════════════════════════════════════════════════

def create_agent_instance(tenant_id: str, config: Optional[Dict] = None,
                          flags: Optional[Dict[str, bool]] = None) -> ContentGeneratorIA:
    return ContentGeneratorIA(tenant_id=tenant_id, config=config, flags=flags)

def get_agent_info() -> Dict[str, Any]:
    return {
        "name": "ContentGeneratorIA",
        "version": VERSION,
        "description": "Enterprise Marketing Content Generation Engine",
        "features": [
            "Multi-tenant architecture",
            "Jurisdiction-specific compliance",
            "Deterministic A/B testing",
            "PII detection & masking",
            "Circuit breaker pattern",
            "Fallback content generation",
            "Advanced metrics & observability",
            "LRU caching with TTL",
            "Auto-remediation & safe backups"
        ],
        "supported_languages": ["es", "en", "pt"],
        "supported_jurisdictions": ["US", "MX", "BR", "CO", "EU", "DO"]
    }
