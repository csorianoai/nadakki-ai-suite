"""
NADAKKI AI SUITE - SAFETY FILTER
Filtro de seguridad robusto para contenido y acciones.
Protección multi-capa contra contenido dañino.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field

# Importar tipos locales
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class SafetyLevel(Enum):
    """Niveles de seguridad para contenido/acciones"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass
class SafetyResult:
    """Resultado de verificación de seguridad"""
    is_safe: bool
    safety_level: SafetyLevel
    score: float
    issues: List[str] = field(default_factory=list)
    modified_content: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CONTENT CATEGORIES
# ============================================================================

class ContentCategory:
    """Categorías de contenido para filtrado"""
    FINANCIAL = "financial"
    MARKETING = "marketing"
    PERSONAL = "personal"
    LEGAL = "legal"
    MEDICAL = "medical"
    GENERAL = "general"


# ============================================================================
# BLOCKED PATTERNS
# ============================================================================

# Patrones potencialmente dañinos (expresiones regulares)
HARMFUL_PATTERNS = {
    "phishing": [
        r"(?i)(verify|confirm|update)\s+(your|account)\s+(password|credentials)",
        r"(?i)click\s+here\s+to\s+(verify|confirm|unlock)",
        r"(?i)your\s+account\s+(has been|will be)\s+(suspended|locked)"
    ],
    "financial_fraud": [
        r"(?i)(guaranteed|100%)\s+(return|profit|roi)",
        r"(?i)get\s+rich\s+quick",
        r"(?i)double\s+your\s+(money|investment)",
        r"(?i)no\s+risk\s+(investment|opportunity)"
    ],
    "sensitive_data": [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
        r"(?i)(password|contraseña|clave)\s*[:=]\s*\S+"
    ],
    "manipulation": [
        r"(?i)(urgent|immediate)\s+(action|response)\s+required",
        r"(?i)limited\s+time\s+(offer|opportunity)",
        r"(?i)act\s+now\s+or\s+miss\s+out"
    ],
    "hate_speech": [
        r"(?i)\b(kill|murder|attack)\s+(all|every)\s+\w+",
        # Patrones adicionales según necesidad
    ]
}

# Palabras bloqueadas por categoría
BLOCKED_WORDS = {
    "profanity": {"fuck", "shit", "damn", "ass", "bitch"},
    "violence": {"kill", "murder", "attack", "bomb", "weapon"},
    "discrimination": {"racist", "sexist", "homophobic"},
    "illegal": {"hack", "crack", "pirate", "steal"}
}

# Dominios sospechosos
SUSPICIOUS_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl",  # URL shorteners
    # Añadir más según necesidad
}


# ============================================================================
# SAFETY FILTER
# ============================================================================

class SafetyFilter:
    """
    Filtro de seguridad multi-capa.
    
    Capas de protección:
    1. Detección de patrones dañinos
    2. Filtrado de palabras bloqueadas
    3. Verificación de URLs
    4. Análisis de contexto
    5. Compliance regulatorio
    
    Configurable por tenant e industria.
    """
    
    def __init__(
        self,
        tenant_id: str = "default",
        strictness: float = 0.7,
        enabled_checks: Set[str] = None
    ):
        self.tenant_id = tenant_id
        self.strictness = max(0.0, min(1.0, strictness))
        
        # Checks habilitados
        self.enabled_checks = enabled_checks or {
            "harmful_patterns",
            "blocked_words",
            "url_verification",
            "pii_detection",
            "compliance"
        }
        
        # Estadísticas
        self.stats = {
            "total_checks": 0,
            "blocks": 0,
            "warnings": 0,
            "passes": 0,
            "by_category": {}
        }
        
        # Cache de resultados
        self._cache: Dict[str, SafetyResult] = {}
        
        # Whitelist personalizada
        self.whitelist: Set[str] = set()
        
        # Reglas personalizadas por tenant
        self.custom_rules: Dict[str, List[str]] = {}
    
    def check_content(
        self,
        content: str,
        content_type: str = "general",
        agent_id: str = "",
        context: Dict[str, Any] = None
    ) -> SafetyResult:
        """
        Verifica contenido contra todas las capas de seguridad.
        
        Args:
            content: Contenido a verificar
            content_type: Tipo de contenido
            agent_id: ID del agente que genera
            context: Contexto adicional
        
        Returns:
            SafetyResult con resultado de verificación
        """
        self.stats["total_checks"] += 1
        
        # Verificar cache
        content_hash = hash(content[:500])
        if content_hash in self._cache:
            return self._cache[content_hash]
        
        issues: List[str] = []
        modified_content = content
        total_score = 1.0
        
        # Capa 1: Patrones dañinos
        if "harmful_patterns" in self.enabled_checks:
            pattern_issues, score = self._check_harmful_patterns(content)
            issues.extend(pattern_issues)
            total_score *= score
        
        # Capa 2: Palabras bloqueadas
        if "blocked_words" in self.enabled_checks:
            word_issues, modified, score = self._check_blocked_words(content)
            issues.extend(word_issues)
            modified_content = modified
            total_score *= score
        
        # Capa 3: URLs
        if "url_verification" in self.enabled_checks:
            url_issues, score = self._check_urls(content)
            issues.extend(url_issues)
            total_score *= score
        
        # Capa 4: PII
        if "pii_detection" in self.enabled_checks:
            pii_issues, modified, score = self._check_pii(modified_content)
            issues.extend(pii_issues)
            modified_content = modified
            total_score *= score
        
        # Capa 5: Compliance
        if "compliance" in self.enabled_checks:
            compliance_issues, score = self._check_compliance(
                content, content_type, context
            )
            issues.extend(compliance_issues)
            total_score *= score
        
        # Determinar nivel de seguridad
        safety_level = self._determine_safety_level(total_score, len(issues))
        is_safe = safety_level in [SafetyLevel.SAFE, SafetyLevel.LOW_RISK]
        
        # Actualizar estadísticas
        if not is_safe:
            self.stats["blocks"] += 1
        elif issues:
            self.stats["warnings"] += 1
        else:
            self.stats["passes"] += 1
        
        result = SafetyResult(
            is_safe=is_safe,
            safety_level=safety_level,
            score=round(total_score, 3),
            issues=issues,
            modified_content=modified_content if modified_content != content else None,
            details={
                "content_type": content_type,
                "agent_id": agent_id,
                "checks_performed": list(self.enabled_checks),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Guardar en cache
        self._cache[content_hash] = result
        
        return result
    
    def _check_harmful_patterns(
        self, 
        content: str
    ) -> Tuple[List[str], float]:
        """Verifica patrones dañinos"""
        issues = []
        score = 1.0
        
        for category, patterns in HARMFUL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    issues.append(f"Harmful pattern detected: {category}")
                    score *= 0.7
                    break  # Una vez detectada la categoría
        
        return issues, max(0.1, score)
    
    def _check_blocked_words(
        self, 
        content: str
    ) -> Tuple[List[str], str, float]:
        """Verifica y reemplaza palabras bloqueadas"""
        issues = []
        modified = content
        score = 1.0
        
        content_lower = content.lower()
        
        for category, words in BLOCKED_WORDS.items():
            for word in words:
                if word in content_lower and word not in self.whitelist:
                    issues.append(f"Blocked word ({category}): {word}")
                    # Reemplazar con asteriscos
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    modified = pattern.sub("*" * len(word), modified)
                    score *= 0.8
        
        return issues, modified, max(0.3, score)
    
    def _check_urls(self, content: str) -> Tuple[List[str], float]:
        """Verifica URLs sospechosas"""
        issues = []
        score = 1.0
        
        # Encontrar URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            # Verificar dominios sospechosos
            for suspicious in SUSPICIOUS_DOMAINS:
                if suspicious in url.lower():
                    issues.append(f"Suspicious URL shortener: {url[:50]}")
                    score *= 0.7
                    break
            
            # Verificar URLs sin HTTPS
            if url.startswith("http://"):
                issues.append(f"Insecure URL (no HTTPS): {url[:50]}")
                score *= 0.9
        
        return issues, max(0.5, score)
    
    def _check_pii(
        self, 
        content: str
    ) -> Tuple[List[str], str, float]:
        """Detecta y enmascara PII"""
        issues = []
        modified = content
        score = 1.0
        
        # Patrones de PII
        pii_patterns = {
            "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", "XXX-XX-XXXX"),
            "credit_card": (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "XXXX-XXXX-XXXX-XXXX"),
            "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
            "phone": (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]")
        }
        
        for pii_type, (pattern, replacement) in pii_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"PII detected ({pii_type}): {len(matches)} instance(s)")
                modified = re.sub(pattern, replacement, modified)
                score *= 0.6
        
        return issues, modified, max(0.3, score)
    
    def _check_compliance(
        self,
        content: str,
        content_type: str,
        context: Dict = None
    ) -> Tuple[List[str], float]:
        """Verifica compliance regulatorio"""
        issues = []
        score = 1.0
        context = context or {}
        
        # Reglas específicas por tipo de contenido
        if content_type == "financial":
            # Verificar disclaimers requeridos
            required_disclaimers = [
                "past performance",
                "not guaranteed",
                "risk"
            ]
            content_lower = content.lower()
            
            has_guarantees = any(
                phrase in content_lower 
                for phrase in ["guaranteed returns", "100% safe", "no risk"]
            )
            
            if has_guarantees:
                missing = [d for d in required_disclaimers if d not in content_lower]
                if missing:
                    issues.append(f"Missing financial disclaimers: {missing}")
                    score *= 0.5
        
        if content_type == "marketing":
            # Verificar requisitos de marketing
            if "email" in content_type.lower():
                if "unsubscribe" not in content.lower():
                    issues.append("Missing unsubscribe option (CAN-SPAM)")
                    score *= 0.8
        
        # Verificar reglas personalizadas del tenant
        for rule_name, patterns in self.custom_rules.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Custom rule violation: {rule_name}")
                    score *= 0.7
        
        return issues, max(0.3, score)
    
    def _determine_safety_level(
        self, 
        score: float, 
        num_issues: int
    ) -> SafetyLevel:
        """Determina nivel de seguridad final"""
        adjusted_score = score * (1 - (num_issues * 0.05))
        
        if adjusted_score >= 0.9 and num_issues == 0:
            return SafetyLevel.SAFE
        elif adjusted_score >= 0.7:
            return SafetyLevel.LOW_RISK
        elif adjusted_score >= 0.5:
            return SafetyLevel.MEDIUM_RISK
        elif adjusted_score >= 0.3:
            return SafetyLevel.HIGH_RISK
        else:
            return SafetyLevel.BLOCKED
    
    def add_to_whitelist(self, words: List[str]):
        """Añade palabras a whitelist"""
        self.whitelist.update(word.lower() for word in words)
    
    def add_custom_rule(self, rule_name: str, patterns: List[str]):
        """Añade regla personalizada"""
        self.custom_rules[rule_name] = patterns
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del filtro"""
        return {
            "tenant_id": self.tenant_id,
            "strictness": self.strictness,
            "enabled_checks": list(self.enabled_checks),
            "stats": self.stats,
            "whitelist_size": len(self.whitelist),
            "custom_rules": len(self.custom_rules),
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self):
        """Limpia cache de resultados"""
        self._cache.clear()
    
    def quick_check(self, content: str) -> bool:
        """
        Verificación rápida - solo retorna True/False.
        Útil para validaciones inline.
        """
        result = self.check_content(content, "general")
        return result.is_safe
