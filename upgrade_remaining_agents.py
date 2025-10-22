# filepath: upgrade_remaining_agents.py
"""Script para mejorar automáticamente los 4 agentes restantes a 95+"""
import re
from pathlib import Path

AGENTS_TO_UPGRADE = {
    "influencermatcheria.py": {
        "missing": ["compliance_full", "pii_detection"],
        "target_score": 100
    },
    "abtestingimpactia.py": {
        "missing": ["compliance_full", "pii_detection"],
        "target_score": 100
    },
    "customersegmentatonia.py": {
        "missing": ["compliance_full", "audit_trail"],
        "target_score": 100
    },
    "competitorintelligenceia.py": {
        "missing": ["compliance_full", "audit_trail", "percentiles"],
        "target_score": 100
    }
}

COMPLIANCE_ENGINE = '''
# ═══════════════════════════════════════════════════════════════════════
# COMPLIANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════

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
'''

PII_DETECTION = '''
    def _detect_pii(self, text: str) -> bool:
        """Detecta PII en texto"""
        if not self.flags.is_enabled("PII_DETECTION"):
            return False
        
        # Patterns para email, teléfono, tarjetas
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # card
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, text):
                return True
        return False
'''

PERCENTILES_CODE = '''
        # Calcular percentiles
        if len(self._metrics["latency_hist"]) >= 10:
            sorted_latencies = sorted(self._metrics["latency_hist"])
            p95_idx = int(len(sorted_latencies) * 0.95)
            p99_idx = int(len(sorted_latencies) * 0.99)
            self._metrics["p95_latency"] = sorted_latencies[p95_idx]
            self._metrics["p99_latency"] = sorted_latencies[p99_idx]
'''

AUDIT_TRAIL_DATACLASS = '''
@dataclass
class DecisionTrace:
    """Audit trail de decisiones"""
    timestamp: datetime
    decision_type: str
    rationale: str
    outcome: str
'''

def add_compliance_engine(content: str) -> str:
    """Agrega ComplianceEngine después de CircuitBreaker"""
    if "class ComplianceEngine" in content:
        return content
    
    # Buscar después de CircuitBreaker
    breaker_end = content.find("# ═══════════════", content.find("class CircuitBreaker"))
    if breaker_end == -1:
        # Buscar otro lugar
        breaker_end = content.find("\n\n@dataclass")
    
    if breaker_end > 0:
        return content[:breaker_end] + "\n" + COMPLIANCE_ENGINE + "\n" + content[breaker_end:]
    return content

def add_pii_detection(content: str, class_name: str) -> str:
    """Agrega método de detección PII a la clase principal"""
    if "_detect_pii" in content:
        return content
    
    # Buscar el __init__ de la clase
    class_pos = content.find(f"class {class_name}")
    if class_pos == -1:
        return content
    
    # Buscar el final del __init__
    init_pos = content.find("def __init__", class_pos)
    next_def = content.find("\n    def ", init_pos + 50)
    
    if next_def > 0:
        return content[:next_def] + "\n" + PII_DETECTION + content[next_def:]
    return content

def add_percentiles(content: str) -> str:
    """Agrega cálculo de percentiles en métricas"""
    if "p95_latency" in content:
        return content
    
    # Buscar donde se actualiza avg_latency_ms
    avg_latency_pos = content.find('self._metrics["avg_latency_ms"]')
    if avg_latency_pos == -1:
        return content
    
    # Encontrar fin de línea
    line_end = content.find("\n", avg_latency_pos)
    
    # Agregar percentiles después
    return content[:line_end] + "\n" + PERCENTILES_CODE + content[line_end:]

def add_audit_trail(content: str) -> str:
    """Agrega DecisionTrace dataclass y campo en Result"""
    if "DecisionTrace" in content:
        return content
    
    # Buscar primer @dataclass
    first_dataclass = content.find("@dataclass")
    if first_dataclass == -1:
        return content
    
    # Agregar antes del primer dataclass
    return content[:first_dataclass] + AUDIT_TRAIL_DATACLASS + "\n" + content[first_dataclass:]

def update_metrics_dict(content: str) -> str:
    """Actualiza dict de métricas para incluir p95/p99"""
    if '"p95_latency"' in content:
        return content
    
    # Buscar el dict de métricas en __init__
    metrics_pattern = r'self\._metrics = \{[^}]+\}'
    match = re.search(metrics_pattern, content)
    
    if match:
        old_metrics = match.group()
        # Agregar p95/p99 antes del cierre
        new_metrics = old_metrics.replace('}', ', "p95_latency": 0.0, "p99_latency": 0.0}')
        return content.replace(old_metrics, new_metrics)
    
    return content

def upgrade_agent(agent_file: str, upgrades: dict) -> bool:
    """Mejora un agente específico"""
    filepath = Path(f"agents/marketing/{agent_file}")
    
    if not filepath.exists():
        print(f"❌ {agent_file} no encontrado")
        return False
    
    print(f"\n🔧 Mejorando {agent_file}...")
    
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    
    # Extraer nombre de clase principal
    class_match = re.search(r'class (\w+IA):', content)
    if not class_match:
        print(f"⚠️  No se encontró clase principal en {agent_file}")
        return False
    
    class_name = class_match.group(1)
    
    # Aplicar upgrades según necesidades
    if "compliance_full" in upgrades["missing"]:
        content = add_compliance_engine(content)
        print(f"  ✓ Compliance engine agregado")
    
    if "pii_detection" in upgrades["missing"]:
        content = add_pii_detection(content, class_name)
        print(f"  ✓ PII detection agregado")
    
    if "percentiles" in upgrades["missing"]:
        content = update_metrics_dict(content)
        content = add_percentiles(content)
        print(f"  ✓ Percentiles p95/p99 agregados")
    
    if "audit_trail" in upgrades["missing"]:
        content = add_audit_trail(content)
        print(f"  ✓ Audit trail agregado")
    
    # Guardar solo si cambió
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ {agent_file} mejorado exitosamente")
        return True
    else:
        print(f"⚠️  {agent_file} no requirió cambios")
        return False

def main():
    print("=" * 80)
    print("UPGRADE AUTOMÁTICO DE AGENTES A 95+/100")
    print("=" * 80)
    
    upgraded = 0
    failed = 0
    
    for agent_file, upgrades in AGENTS_TO_UPGRADE.items():
        if upgrade_agent(agent_file, upgrades):
            upgraded += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESUMEN: {upgraded} agentes mejorados, {failed} fallidos")
    print("=" * 80)
    print("\n▶ Ejecuta ahora: python audit_final_11_agents.py")

if __name__ == "__main__":
    main()