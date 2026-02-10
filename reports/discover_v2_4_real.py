#!/usr/bin/env python3
"""
NADAKKI AI Suite - Total Agent Discovery v2.4 (REAL-WORLD MAPPING)
- Mapeo real de carpetas encontradas
- Excluye backups/archived/wrappers/layers
- Reglas precisas por módulo
"""
import json, ast, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

AGENTS_ROOT = Path.cwd() / "agents"
REPORTS_DIR = Path.cwd() / "reports_v2_4"
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# MAPEO REAL DE CARPETAS (basado en tu estructura real)
# ============================================================================

# Carpetas que DEBEN ser excluidas (no agentes)
HARD_BLACKLIST_DIRS = {
    "_archived", "backup_", "backup_placeholders_", "_backup", "archive",
    "wrappers", "layers", "helpers", "utils", "common", "lib", "libs",
    "temp", "tmp", "old", "legacy", "deprecated"
}

# Mapeo REAL de carpetas a módulos
REAL_MODULE_MAP = {
    # Módulos principales
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
    "originacion": "originacion",
    
    # Subcarpetas de marketing que SÍ son marketing
    "advertising": "marketing",
    "orchestrator": "marketing",
    "operative": "marketing",
    "executors": "marketing",
    
    # Carpetas especiales (detectadas en "otros")
    "shared_layers": "core",
    "decision": "coordinadores",
    "fortaleza": "core",
    "orchestration": "coordinadores",
    "compliance": "regtech",  # Ya existe módulo regtech
    "operacional": "coordinadores",
    "vigilancia": "originacion",  # Sentinel está en originacion
    "inteligencia": "core",
    "experiencia": "core",
}

# EXPECTED ajustado con módulos REALES
REAL_EXPECTED = {
    "marketing": 44,
    "legal": 33,
    "contabilidad": 21,
    "logistica": 23,
    "presupuesto": 13,
    "rrhh": 10,
    "educacion": 9,
    "investigacion": 9,
    "ventascrm": 9,
    "regtech": 12,  # 8 original + 4 de compliance
    "recuperacion": 5,
    "originacion": 13,  # 10 original + 3 de vigilancia
    "coordinadores": 12,  # decision(5) + orchestration(4) + operacional(3)
    "core": 16,  # shared_layers(10) + fortaleza(4) + inteligencia(2)
    "otros": 5  # Lo que realmente no mapea
}

# ============================================================================
# REGLAS POR TIPO DE MÓDULO
# ============================================================================

def is_blacklisted_path(rel_path):
    """Verifica si el path está en blacklist"""
    parts = rel_path.lower().split('/')
    for part in parts:
        for black in HARD_BLACKLIST_DIRS:
            if black in part:
                return True
    return False

def detect_module_from_path(rel_path):
    """Módulo basado en mapeo REAL"""
    parts = rel_path.lower().split('/')
    
    # Primera carpeta
    if parts and parts[0] in REAL_MODULE_MAP:
        return REAL_MODULE_MAP[parts[0]]
    
    # Segunda carpeta (para subcarpetas)
    if len(parts) > 1 and parts[1] in REAL_MODULE_MAP:
        return REAL_MODULE_MAP[parts[1]]
    
    # Carpeta no mapeada → "otros"
    return "otros"

def is_marketing_agent(tree, content, filename):
    """Marketing: reglas MUY estrictas"""
    content_lower = content.lower()
    
    # 1. Nombre del archivo debe terminar en IA.py o Agent.py
    if not (filename.endswith('IA.py') or filename.endswith('Agent.py')):
        # Solo excepción si tiene execute/run EXPLÍCITO
        if not has_explicit_execute(tree):
            return False, "filename_not_ia_agent"
    
    # 2. Debe tener clase con nombre de agente
    if not has_agent_class(tree):
        return False, "no_agent_class"
    
    # 3. Debe tener AI keywords o imports
    ai_keywords = ["openai", "anthropic", "gpt", "llm", "langchain", "crewai"]
    if not any(kw in content_lower for kw in ai_keywords):
        return False, "no_ai_keywords"
    
    # 4. Tamaño mínimo
    lines = content.count('\n') + 1
    if lines < 50:
        return False, "too_small"
    
    return True, "valid_marketing_agent"

def is_domain_agent(module, tree, content, lines):
    """Reglas para dominios (legal, logística, etc.)"""
    content_lower = content.lower()
    
    # 1. Execute/run siempre vale
    if has_explicit_execute(tree):
        return True, "has_execute"
    
    # 2. Clase con sufijo de agente
    if has_agent_class(tree):
        return True, "has_agent_class"
    
    # 3. Para archivos grandes (>150 líneas) con lógica compleja
    if lines > 150 and has_complex_logic(content_lower):
        return True, "large_complex_file"
    
    # 4. Archivos MUY grandes de dominio (>250 líneas)
    if lines > 250 and not is_pure_utils(content_lower, lines):
        return True, "very_large_domain_file"
    
    # 5. Para legal/contabilidad: archivos con keywords de dominio
    if module in ["legal", "contabilidad", "logistica"] and lines > 100:
        domain_keywords = {
            "legal": ["penal", "procesal", "constitucional", "derecho", "ley"],
            "contabilidad": ["contab", "fiscal", "dgii", "itbis", "balance"],
            "logistica": ["logistic", "invent", "almacen", "transporte", "ruta"]
        }
        if any(kw in content_lower for kw in domain_keywords.get(module, [])):
            return True, "domain_keywords_large"
    
    return False, ""

def has_explicit_execute(tree):
    """Tiene función o método execute/run"""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in ["execute", "run", "process", "analyze"]:
                return True
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ["execute", "run"]:
                    return True
    return False

def has_agent_class(tree):
    """Tiene clase con nombre de agente"""
    agent_suffixes = ["agent", "ia", "orchestrator", "coordinator", "manager", 
                     "optimizer", "strategist", "controller", "analyzer"]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name.lower()
            for suffix in agent_suffixes:
                if suffix in class_name or class_name.endswith(suffix):
                    return True
    return False

def has_complex_logic(content_lower):
    """Contiene lógica compleja (ifs, loops, returns)"""
    logic_patterns = ["if ", "for ", "while ", "return ", "def ", "class "]
    return sum(1 for pattern in logic_patterns if pattern in content_lower) >= 3

def is_pure_utils(content_lower, lines):
    """Es puro código utilitario"""
    if lines < 30:
        utils_indicators = ["import os", "import sys", "def main()", "argparse", "logging"]
        if sum(1 for ind in utils_indicators if ind in content_lower) >= 2:
            return True
    return False

# ============================================================================
# ESCANEO PRINCIPAL
# ============================================================================

def main():
    print("\n" + "="*80)
    print("NADAKKI — DISCOVERY v2.4 (REAL-WORLD MAPPING)")
    print("="*80)
    
    agents = []
    by_module = defaultdict(int)
    files_total = 0
    files_skipped = 0
    
    for fp in sorted(AGENTS_ROOT.rglob("*.py")):
        files_total += 1
        
        rel_path = fp.relative_to(AGENTS_ROOT).as_posix()
        
        # 1. Excluir por blacklist
        if is_blacklisted_path(rel_path):
            files_skipped += 1
            continue
        
        # 2. Leer contenido
        try:
            content = fp.read_text(encoding='utf-8', errors='ignore')
        except:
            continue
        
        if not content.strip():
            continue
        
        lines = content.count('\n') + 1
        filename = fp.name
        
        # 3. Determinar módulo (REAL)
        module = detect_module_from_path(rel_path)
        
        # 4. Parse AST
        try:
            tree = ast.parse(content)
        except:
            tree = ast.Module(body=[], type_ignores=[])
        
        is_agent = False
        reason = ""
        
        # 5. Aplicar reglas específicas por módulo
        if module == "marketing":
            is_agent, reason = is_marketing_agent(tree, content, filename)
        
        elif module in ["legal", "contabilidad", "logistica", "presupuesto", 
                       "rrhh", "educacion", "investigacion", "ventascrm",
                       "regtech", "recuperacion", "originacion"]:
            is_agent, reason = is_domain_agent(module, tree, content, lines)
        
        elif module in ["coordinadores", "core"]:
            # Coordinadores/core: reglas flexibles pero con tamaño
            if lines > 80 and (has_explicit_execute(tree) or has_agent_class(tree)):
                is_agent = True
                reason = "coordinator_or_core"
        
        else:  # "otros"
            # Para "otros": solo si es muy obvio que es agente
            if (has_explicit_execute(tree) or 
                (lines > 200 and has_agent_class(tree))):
                is_agent = True
                reason = "otros_strong_signal"
        
        if not is_agent:
            continue
        
        # 6. Generar registro del agente
        h = hashlib.md5(rel_path.encode()).hexdigest()[:6]
        agent_id = Path(filename).stem.lower() + f"_{h}"
        
        status = "active" if has_explicit_execute(tree) else "configured"
        
        agents.append({
            "agent_id": agent_id,
            "filename": filename,
            "file_path": rel_path,
            "module": module,
            "status": status,
            "lines": lines,
            "reason_detected": reason
        })
        
        by_module[module] += 1
    
    # ============================================================================
    # GENERAR REPORTES
    # ============================================================================
    
    # Solo agentes para frontend (active + configured)
    frontend_agents = [a for a in agents]
    frontend_by_module = defaultdict(int)
    for a in frontend_agents:
        frontend_by_module[a["module"]] += 1
    
    # Inventario para frontend
    frontend_inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "discovery_version": "v2.4_real_world",
        "total_agents": len(frontend_agents),
        "by_module": dict(sorted(frontend_by_module.items())),
        "agents": frontend_agents,
        "statistics": {
            "files_total": files_total,
            "files_skipped": files_skipped,
            "modules_detected": len(frontend_by_module)
        }
    }
    
    # Validación vs expected REAL
    validation = {
        "expected": REAL_EXPECTED,
        "found": dict(sorted(frontend_by_module.items())),
        "comparison": {},
        "summary": {
            "total_expected": sum(REAL_EXPECTED.values()),
            "total_found": len(frontend_agents),
            "difference": len(frontend_agents) - sum(REAL_EXPECTED.values())
        }
    }
    
    for mod, exp in REAL_EXPECTED.items():
        found = frontend_by_module.get(mod, 0)
        missing = max(exp - found, 0)
        extra = max(found - exp, 0)
        
        if found >= exp:
            status = "ok"
        elif found > 0:
            status = "warn"
        else:
            status = "critical"
        
        validation["comparison"][mod] = {
            "expected": exp,
            "found": found,
            "missing": missing,
            "extra": extra,
            "status": status
        }
    
    # Guardar
    reports_dir = Path("./reports_v2_4")
    reports_dir.mkdir(exist_ok=True)
    
    with open(reports_dir / "agents_frontend.json", "w", encoding="utf-8") as f:
        json.dump(frontend_inventory, f, ensure_ascii=False, indent=2)
    
    with open(reports_dir / "agents_validation.json", "w", encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)
    
    # ============================================================================
    # MOSTRAR RESULTADOS
    # ============================================================================
    
    print(f"\n📊 RESULTADOS v2.4:")
    print(f"Archivos procesados: {files_total}")
    print(f"Archivos excluidos: {files_skipped}")
    print(f"Agentes detectados: {len(frontend_agents)}")
    print(f"Módulos detectados: {len(frontend_by_module)}")
    
    print(f"\n📈 DISTRIBUCIÓN REAL:")
    for mod, count in sorted(frontend_by_module.items()):
        exp = REAL_EXPECTED.get(mod, 0)
        icon = "✅" if count >= exp else "⚠️" if count > 0 else "❌"
        diff = count - exp
        diff_str = f"(+{diff})" if diff > 0 else f"({diff})" if diff < 0 else ""
        print(f"  {icon} {mod:15} {count:3}/{exp:3} {diff_str}")
    
    total_expected = sum(REAL_EXPECTED.values())
    total_found = len(frontend_agents)
    
    print(f"\n🎯 TOTALES:")
    print(f"  Esperados: {total_expected}")
    print(f"  Encontrados: {total_found}")
    print(f"  Diferencia: {total_found - total_expected}")
    
    # Análisis de los más problemáticos
    print(f"\n🔍 ANÁLISIS DETALLADO:")
    
    # Marketing específico
    marketing_agents = [a for a in frontend_agents if a["module"] == "marketing"]
    print(f"  Marketing: {len(marketing_agents)} agentes")
    
    # Verificar si marketing tiene muchos falsos positivos
    marketing_ia_count = sum(1 for a in marketing_agents if a["filename"].endswith("IA.py"))
    print(f"    - Con IA.py: {marketing_ia_count}")
    
    # "Otros" específico
    otros_agents = [a for a in frontend_agents if a["module"] == "otros"]
    if otros_agents:
        print(f"  Otros: {len(otros_agents)} agentes (deberían ser ~5)")
        print(f"    Ejemplos: {', '.join([a['filename'] for a in otros_agents[:3]])}")
    
    print(f"\n📁 Reportes guardados en: {reports_dir}/")
    print("="*80)

if __name__ == "__main__":
    main()
