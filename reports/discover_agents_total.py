#!/usr/bin/env python3
"""
NADAKKI AI Suite - Total Agent Discovery v2.1 (FIXED)
- Encoding UTF-8 explícito
- Platform rules más precisos
- Heurísticas mejoradas para >50 líneas
- Sin depender de patrones de nombre
"""
import os
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

AGENTS_ROOT = Path.cwd() / "agents"

FOLDER_BLACKLIST = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    "backup", "legacy", "tests", "testing", "test", ".pytest_cache"
}

# Señales AI/Decisioning
AI_KEYWORDS = [
    "openai", "anthropic", "claude", "gpt", "llm", "embedding", "chatcompletion",
    "pydantic", "fastapi", "langchain", "llamaindex", "crewai",
    "predict", "classification", "scoring", "risk", "decision",
    "automation", "orchestrat", "workflow", "pipeline", "analyze"
]

# Clases con comportamiento autónomo
AUTONOMOUS_CLASS_HINTS = [
    "agent", "ia", "assistant", "orchestrator", "coordinator", "manager",
    "optimizer", "strategist", "controller", "sentinel", "profiler", "oracle",
    "tester", "pathway", "recovery", "collection", "analyzer"
]

# Imports que indican agente
AGENT_IMPORTS = [
    "openai", "anthropic", "langchain", "llamaindex", "crewai",
    "fastapi", "pydantic"
]

# Anticipo: utilitarios puros
UTILS_ANTI = [
    "argparse", "click", "typer", "logging",
    'if __name__ == "__main__"'
]

# PLATAFORMAS - PRECISAS (NO GENÉRICAS)
PLATFORM_RULES = {
    "google_ads": [
        "googleads", "google ads", "adwords", "gads",
        "rsa", "search terms", "match type", "keyword planner",
        "google_ads", "google ads strategist", "budget pacing"
    ],
    "meta_ads": [
        "facebook ads", "instagram ads", "meta ads",
        "lookalike", "pixel", "business manager", "meta_ads",
        "facebook_ads", "instagram_ads", "capi"
    ],
    "linkedin_ads": [
        "linkedin ads", "sponsored content", "campaign manager",
        "linkedin_ads", "linkedIn"
    ],
    "tiktok_ads": [
        "tiktok ads", "spark ads", "in-feed", "ttads",
        "tiktok_ads"
    ],
}

# Categorías por palabras clave
CATEGORY_RULES = [
    (("penal", "procesal", "constitucional", "civil", "laboral", "tribut", "comercial"), "legal"),
    (("campaign", "keyword", "roas", "ctr", "conversion", "creative", "audience"), "marketing_ads"),
    (("factur", "fiscal", "reconcili", "contab", "flujo", "balance", "auditor"), "accounting"),
    (("logistic", "invent", "warehouse", "rutas", "transporte", "demanda"), "logistics"),
    (("rrhh", "nomina", "cv", "talent", "seleccion"), "hr"),
    (("presupuesto", "forecast", "budget"), "budgeting"),
    (("investig", "tendencia", "innovacion"), "research"),
    (("ventas", "crm", "pipeline", "cliente", "lifecycle"), "sales"),
    (("aml", "regtech", "compliance", "kyc"), "compliance"),
    (("recovery", "recuper", "cobro", "collection"), "recovery"),
    (("originacion", "underwrite", "sentinel"), "origination"),
    (("coordinador", "orchestrator"), "coordination"),
]

# Mapeo módulos (por carpeta)
MODULE_MAP = {
    "marketing": "marketing",
    "legal": "legal",
    "contabilidad": "contabilidad",
    "logistica": "logistica",
    "presupuesto": "presupuesto",
    "rrhh": "rrhh",
    "educacion": "educacion",
    "investigacion": "investigacion",
    "ventascrm": "ventascrm",
    "regtech": "regtech",
    "recuperacion": "recuperacion",
    "originacion": "originacion"
}

# Inventario esperado (confirmado)
EXPECTED = {
    "marketing": 44,
    "legal": 33,
    "contabilidad": 21,
    "logistica": 23,
    "presupuesto": 13,
    "rrhh": 10,
    "educacion": 9,
    "investigacion": 9,
    "ventascrm": 9,
    "regtech": 8,
    "recuperacion": 5,
    "originacion": 10,
    "otros": 20
}

# =============================================================================
# FUNCIONES
# =============================================================================

def safe_read(fp):
    """Lee archivo con múltiples encodings"""
    for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
        try:
            return fp.read_text(encoding=enc)
        except:
            pass
    return ""

def parse_ast(content):
    """Parse AST con manejo de errores"""
    try:
        return ast.parse(content)
    except:
        return ast.Module(body=[], type_ignores=[])

def has_fn(tree, names):
    """Detecta función en nivel top"""
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names:
            return True
    return False

def has_method(tree, names):
    """Detecta método en clase"""
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)) and b.name in names:
                    return True
    return False

def has_auto_class(tree):
    """Detecta clase con nombre autónomo"""
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            nm = (n.name or "").lower()
            if any(h in nm for h in AUTONOMOUS_CLASS_HINTS):
                return True
    return False

def has_ai_imports(content_lower):
    """Detecta imports AI/ML"""
    return sum(1 for imp in AGENT_IMPORTS if imp in content_lower) >= 1

def has_ai_logic(content_lower):
    """Detecta lógica AI/ML/Decisioning"""
    return sum(1 for kw in AI_KEYWORDS if kw in content_lower) >= 2

def is_pure_utils(content_lower, lines):
    """Determina si es puro utils"""
    if lines < 40:
        utils_signals = sum(1 for u in UTILS_ANTI if u in content_lower)
        if utils_signals >= 2:
            return True
    return False

def passes_substantial_size_rule(tree, content_lower, lines):
    """REGLA MEJORADA para >50 líneas"""
    if lines <= 50:
        return False
    
    if is_pure_utils(content_lower, lines):
        return False
    
    has_class = has_auto_class(tree)
    has_import = has_ai_imports(content_lower)
    has_kw = any(kw in content_lower for kw in ["scoring", "decision", "risk", "workflow", "optimize"])
    
    return has_class or has_import or has_kw

def det_module(parts):
    """Detecta módulo por carpeta"""
    if not parts:
        return "otros"
    return MODULE_MAP.get(parts[0].lower(), "otros")

def det_platform(mod, rel_path, content_lower):
    """DETECTA PLATAFORMA SOLO EN MARKETING"""
    if mod != "marketing":
        return None
    
    scope = rel_path.lower() + " " + content_lower
    
    for platform, keywords in PLATFORM_RULES.items():
        matches = sum(1 for kw in keywords if kw in scope)
        
        if matches >= 2:
            return platform
        if matches >= 1 and any(specific in scope for specific in ["rsa", "googleads", "adwords", "pixel", "capi"]):
            return platform
    
    return None

def det_category(content_lower, rel_parts):
    """Detecta categoría por contenido + carpeta"""
    scope = content_lower + " " + " ".join(rel_parts)
    
    for keywords, category in CATEGORY_RULES:
        if any(kw in scope for kw in keywords):
            return category
    
    return "general"

def det_status(tree, content_lower):
    """Determina status: active, configured, template"""
    if has_fn(tree, {"execute", "run"}) or has_method(tree, {"execute", "run"}):
        return "active"
    elif has_ai_logic(content_lower) or has_auto_class(tree):
        return "configured"
    return "template"

def det_reason(tree, content_lower, lines):
    """Documenta por qué fue detectado como agente"""
    reasons = []
    
    if has_fn(tree, {"execute", "run"}):
        reasons.append("execute_function")
    if has_method(tree, {"execute", "run"}):
        reasons.append("class_execute_method")
    if has_auto_class(tree):
        reasons.append("autonomous_class")
    if has_ai_logic(content_lower):
        reasons.append("ai_ml_signals")
    if has_ai_imports(content_lower):
        reasons.append("agent_framework_imports")
    if lines > 100:
        reasons.append("substantial_codebase")
    
    return " | ".join(reasons[:3]) if reasons else "heuristic"

# =============================================================================
# DESCUBRIMIENTO
# =============================================================================

agents = []
by_module = defaultdict(int)
files_total = 0
files_ignored = 0

print("\n" + "="*100)
print("Descubriendo agentes en NADAKKI...")
print("="*100 + "\n")

if not AGENTS_ROOT.exists():
    print(f"ERROR: {AGENTS_ROOT} no existe")
    exit(1)

for fp in sorted(AGENTS_ROOT.rglob("*.py")):
    files_total += 1
    
    if any(b in [p.lower() for p in fp.parts] for b in FOLDER_BLACKLIST):
        files_ignored += 1
        continue
    
    content = safe_read(fp)
    if not content.strip():
        continue
    
    lines = content.count("\n") + 1
    content_lower = content.lower()
    rel_path = str(fp.relative_to(AGENTS_ROOT)).replace("\\", "/")
    rel_parts = rel_path.split("/")[:-1]
    
    tree = parse_ast(content)
    
    # REGLA FUNDAMENTAL: ES AGENTE SI CUMPLE AL MENOS UNO
    rule1 = has_fn(tree, {"execute", "run"})
    rule2 = has_method(tree, {"execute", "run"})
    rule3 = has_auto_class(tree)
    rule4 = has_ai_logic(content_lower)
    rule5 = passes_substantial_size_rule(tree, content_lower, lines)
    
    is_agent = rule1 or rule2 or rule3 or rule4 or rule5
    
    if not is_agent:
        continue
    
    # CLASIFICACIÓN
    module = det_module(rel_parts)
    platform = det_platform(module, rel_path, content_lower)
    category = det_category(content_lower, rel_parts)
    status = det_status(tree, content_lower)
    reason = det_reason(tree, content_lower, lines)
    
    h = hashlib.md5(rel_path.encode()).hexdigest()[:4]
    agent_id = Path(fp.name).stem.lower().replace("-", "_") + f"_{h}"
    
    agents.append({
        "agent_id": agent_id,
        "filename": fp.name,
        "file_path": rel_path,
        "module": module,
        "platform": platform,
        "category": category,
        "status": status,
        "lines": lines,
        "reason_detected": reason
    })
    
    by_module[module] += 1

# =============================================================================
# REPORTE
# =============================================================================

inventory = {
    "generated_at": datetime.now().isoformat() + "Z",
    "discovery_method": "semantic_analysis_v2.1",
    "agents_path": str(AGENTS_ROOT),
    "total_agents_found": len(agents),
    "by_module": dict(sorted(by_module.items())),
    "agents": agents
}

validation = {
    "expected_inventory": EXPECTED,
    "found_inventory": dict(sorted(by_module.items())),
    "comparison": {},
    "summary": {
        "files_total": files_total,
        "files_ignored": files_ignored,
        "agents_found": len(agents)
    }
}

for mod, exp in EXPECTED.items():
    found = by_module.get(mod, 0)
    
    if found >= exp:
        match = "found_and_correct"
    elif found > 0:
        match = "found_but_mismatch"
    else:
        match = "not_found_critical"
    
    validation["comparison"][mod] = {
        "expected": exp,
        "found": found,
        "missing": max(exp - found, 0),
        "status": match
    }

# =============================================================================
# GUARDAR CON ENCODING UTF-8 EXPLÍCITO
# =============================================================================

def save_json(path, data):
    """Guarda JSON con encoding UTF-8 explícito"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

reports_dir = Path("./reports")
reports_dir.mkdir(exist_ok=True)

save_json(reports_dir / "agents_inventory.json", inventory)
save_json(reports_dir / "agents_validation.json", validation)

# =============================================================================
# MOSTRAR RESULTADOS
# =============================================================================

print("="*100)
print(f"TOTAL agentes encontrados: {len(agents)}")
print(f"Archivos procesados: {files_total - files_ignored}/{files_total}")
print(f"\nPor modulo:")

for m in sorted(by_module.keys()):
    exp = EXPECTED.get(m, 0)
    found = by_module[m]
    match = "OK" if found >= exp else f"WARN({found}/{exp})"
    print(f"  {match} {m:15} {found:3} agentes")

print(f"\nDetalle de comparacion con inventario esperado:")
for mod in sorted(EXPECTED.keys()):
    exp = EXPECTED[mod]
    found = by_module.get(mod, 0)
    status = "OK" if found >= exp else "MISMATCH" if found > 0 else "MISSING"
    print(f"  {mod:15} Esperado: {exp:2} | Encontrado: {found:2} | Status: {status}")

print("\n" + "="*100)
print(f"Reportes guardados en ./reports/")
print(f"  - agents_inventory.json")
print(f"  - agents_validation.json")
print("="*100)
