#!/usr/bin/env python3
"""
NADAKKI AI Suite — Agent Discovery v2.5 (BALANCED)
OBJETIVO:
- Corregir drift entre ejecuciones (marketing=0 / otros inflado)
- Mapeo real de carpetas encontradas en tu repo
- Reglas balanceadas: filtra soporte/backups pero NO mata agentes reales

OUTPUTS:
- reports_v2_5/agents_inventory.raw.json
- reports_v2_5/agents_frontend.json
- reports_v2_5/agents_validation.json
"""

import ast
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

AGENTS_ROOT = Path.cwd() / "agents"
REPORTS_DIR = Path.cwd() / "reports_v2_5"
REPORTS_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------------------
# 1) BLACKLIST (carpetas/artefactos NO agentes)
# ------------------------------------------------------------------------------
# Match por substring (muy efectivo para backups/versionados)
HARD_BLACKLIST_SUBSTR = [
    "__pycache__", ".git", ".venv", "venv", "node_modules", ".pytest_cache",
    ".idea", ".vscode",
    "_archived", "archived", "archive",
    "backup", "backups", "backup_placeholders", "registry_backup",
    "legacy", "deprecated", "old", "tmp", "temp",
    "wrappers", "wrapper",
    "layers", "layer",
    "helpers", "helper", "utils", "util",
    "schemas", "schema", "types",
    "constants", "const",
    "fixtures", "samples", "sample",
]

def is_blacklisted(rel_path: str) -> bool:
    p = rel_path.lower()
    return any(s in p for s in HARD_BLACKLIST_SUBSTR)

# ------------------------------------------------------------------------------
# 2) MAPEO REAL de carpetas "otros" → módulos estables
# ------------------------------------------------------------------------------
# Basado en tu output: shared_layers, decision, fortaleza, orchestration, compliance, etc.
REAL_FOLDER_TO_MODULE = {
    # principales
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

    # folders detectados como "otros"
    "shared_layers": "core",
    "fortaleza": "core",
    "inteligencia": "core",
    "experiencia": "core",

    "decision": "coordinacion",
    "orchestration": "coordinacion",
    "operacional": "coordinacion",

    "compliance": "regtech",
    "vigilancia": "originacion",
}

# Marketing subfolders reales (tu output)
MARKETING_SUBFOLDERS_AS_MARKETING = {"advertising", "orchestrator", "operative", "executors"}

def detect_module(rel_path: str) -> str:
    parts = rel_path.split("/")
    # 1ra carpeta
    if parts and parts[0].lower() in REAL_FOLDER_TO_MODULE:
        return REAL_FOLDER_TO_MODULE[parts[0].lower()]
    # 2da carpeta (cuando hay estructura tipo marketing/advertising/...)
    if len(parts) > 1 and parts[1].lower() in REAL_FOLDER_TO_MODULE:
        return REAL_FOLDER_TO_MODULE[parts[1].lower()]
    # marketing subfolder
    if parts and parts[0].lower() == "marketing" and len(parts) > 1:
        if parts[1].lower() in MARKETING_SUBFOLDERS_AS_MARKETING:
            return "marketing"
    return "otros"

# ------------------------------------------------------------------------------
# 3) Señales / heurísticas balanceadas
# ------------------------------------------------------------------------------
AI_IMPORTS = ["openai", "anthropic", "langchain", "llamaindex", "crewai", "fastapi", "pydantic"]
AI_KEYWORDS = [
    "gpt", "llm", "embedding", "chatcompletion", "completion",
    "scoring", "risk", "decision", "underwrite", "workflow", "orchestr",
    "optimiz", "analy", "classif", "predict"
]
AGENT_CLASS_HINTS = [
    "agent", "ia", "assistant", "orchestrator", "coordinator", "manager",
    "optimizer", "strategist", "controller", "sentinel", "profiler",
    "oracle", "tester", "pathway", "recovery", "collection", "analyzer"
]

def safe_read(fp: Path) -> str:
    for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
        try:
            return fp.read_text(encoding=enc)
        except Exception:
            pass
    return ""

def parse_ast(content: str):
    try:
        return ast.parse(content)
    except Exception:
        return ast.Module(body=[], type_ignores=[])

def has_execute_or_run(tree) -> bool:
    # top-level functions
    for n in getattr(tree, "body", []):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in ("execute", "run"):
            return True
    # class methods
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)) and b.name in ("execute", "run"):
                    return True
    return False

def has_agent_class(tree) -> bool:
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            nm = (n.name or "").lower()
            if any(h in nm for h in AGENT_CLASS_HINTS):
                return True
    return False

def has_ai_signals(content_lower: str) -> bool:
    imports_hit = any(imp in content_lower for imp in AI_IMPORTS)
    kw_count = sum(1 for k in AI_KEYWORDS if k in content_lower)
    return imports_hit or kw_count >= 2

def filename_agentish(fp: Path) -> bool:
    # FIX: case-insensitive ia/agent
    name = fp.name.lower()
    return name.endswith("ia.py") or name.endswith("agent.py") or "agent" in name

def is_support_like(module: str, rel_path: str) -> bool:
    # soporte típico; si trae execute/run se acepta igual
    p = rel_path.lower()
    # para marketing, es común tener soporte y wrappers, ya filtrados por blacklist.
    # aquí bloqueamos cosas residuales tipo clients/config/schemas si quedaron.
    support_hints = ["client", "clients", "config", "configs", "schema", "schemas", "types", "constants"]
    if any(h in p for h in support_hints) and module == "marketing":
        return True
    return False

def classify_status(tree, content_lower: str) -> str:
    if has_execute_or_run(tree):
        return "active"
    if has_agent_class(tree) or has_ai_signals(content_lower):
        return "configured"
    return "template"

def is_agent_balanced(module: str, fp: Path, rel_path: str, content: str, tree) -> (bool, str):
    cl = content.lower()
    lines = content.count("\n") + 1

    # regla dura: support-like sin execute/run => no
    if is_support_like(module, rel_path) and not has_execute_or_run(tree):
        return False, "support_like_no_execute"

    # --- MARKETING (balanceado, NO ultra-estricto, para evitar marketing=0)
    if module == "marketing":
        # aceptar si:
        #  - execute/run (siempre)
        #  - o (agent class y señales AI) y tamaño mínimo
        if has_execute_or_run(tree):
            return True, "marketing_execute"
        if (filename_agentish(fp) or has_agent_class(tree)) and has_ai_signals(cl) and lines >= 40:
            return True, "marketing_balanced"
        return False, "marketing_filtered"

    # --- OTROS (muy estricto para bajar inflado)
    if module == "otros":
        if has_execute_or_run(tree) and (has_ai_signals(cl) or has_agent_class(tree)) and lines >= 60:
            return True, "otros_strict_execute_ai"
        if has_agent_class(tree) and has_ai_signals(cl) and lines >= 220:
            return True, "otros_strict_big_ai"
        return False, "otros_filtered"

    # --- DOMINIOS (balanceado)
    # aceptar si:
    # - execute/run
    # - o agent class + (AI signals o tamaño)
    # - o archivos grandes con AI signals
    if has_execute_or_run(tree):
        return True, "domain_execute"
    if has_agent_class(tree) and (has_ai_signals(cl) or lines >= 120):
        return True, "domain_agent_class"
    if has_ai_signals(cl) and lines >= 180:
        return True, "domain_large_ai"
    return False, "domain_filtered"

# ------------------------------------------------------------------------------
# 4) EXPECTED (mantén tu base original + nuevos módulos por mapeo)
# ------------------------------------------------------------------------------
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
    "core": 0,          # no te lo contamos contra expected (informativo)
    "coordinacion": 0,  # idem
    "otros": 20
}

def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("\n" + "="*100)
    print("NADAKKI — DISCOVERY v2.5 (BALANCED)")
    print("="*100 + "\n")

    if not AGENTS_ROOT.exists():
        raise SystemExit(f"ERROR: {AGENTS_ROOT} no existe")

    agents_raw = []
    agents_frontend = []
    by_module_raw = defaultdict(int)
    by_module_frontend = defaultdict(int)

    files_total = 0
    files_skipped = 0

    for fp in sorted(AGENTS_ROOT.rglob("*.py")):
        files_total += 1
        rel_path = fp.relative_to(AGENTS_ROOT).as_posix()

        if is_blacklisted(rel_path):
            files_skipped += 1
            continue

        content = safe_read(fp)
        if not content.strip():
            continue

        tree = parse_ast(content)
        module = detect_module(rel_path)

        ok, reason = is_agent_balanced(module, fp, rel_path, content, tree)
        if not ok:
            continue

        cl = content.lower()
        lines = content.count("\n") + 1
        status = classify_status(tree, cl)

        h = hashlib.md5(rel_path.encode()).hexdigest()[:6]
        aid = Path(fp.name).stem.lower().replace("-", "_") + f"_{h}"

        row = {
            "agent_id": aid,
            "filename": fp.name,
            "file_path": rel_path,
            "module": module,
            "status": status,
            "lines": lines,
            "reason_detected": reason
        }

        agents_raw.append(row)
        by_module_raw[module] += 1

        # Frontend: solo active/configured
        if status in ("active", "configured"):
            agents_frontend.append(row)
            by_module_frontend[module] += 1

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    inventory_raw = {
        "generated_at": now,
        "discovery_version": "v2.5_balanced",
        "total_agents": len(agents_raw),
        "by_module": dict(sorted(by_module_raw.items())),
        "agents": agents_raw,
        "statistics": {
            "files_total": files_total,
            "files_skipped": files_skipped,
        }
    }

    inventory_frontend = {
        "generated_at": now,
        "discovery_version": "v2.5_balanced",
        "total_agents": len(agents_frontend),
        "by_module": dict(sorted(by_module_frontend.items())),
        "agents": agents_frontend,
        "statistics": {
            "files_total": files_total,
            "files_skipped": files_skipped,
        }
    }

    # Validation vs expected (solo módulos con expected > 0; core/coordinacion informativos)
    comparison = {}
    total_expected = sum(v for k, v in EXPECTED.items() if v and v > 0)
    total_found = len(agents_frontend)

    for mod, exp in EXPECTED.items():
        if exp <= 0:
            # informativo
            comparison[mod] = {
                "expected": exp,
                "found": by_module_frontend.get(mod, 0),
                "missing": 0,
                "extra": 0,
                "status": "info"
            }
            continue

        found = by_module_frontend.get(mod, 0)
        missing = max(exp - found, 0)
        extra = max(found - exp, 0)

        if found >= exp:
            st = "ok"
        elif found > 0:
            st = "warn"
        else:
            st = "critical"

        comparison[mod] = {
            "expected": exp,
            "found": found,
            "missing": missing,
            "extra": extra,
            "status": st
        }

    validation = {
        "summary": {
            "total_expected": total_expected,
            "total_found": total_found,
            "difference": total_found - total_expected,
        },
        "expected": EXPECTED,
        "found": dict(sorted(by_module_frontend.items())),
        "comparison": comparison
    }

    save_json(REPORTS_DIR / "agents_inventory.raw.json", inventory_raw)
    save_json(REPORTS_DIR / "agents_frontend.json", inventory_frontend)
    save_json(REPORTS_DIR / "agents_validation.json", validation)

    print("="*100)
    print(f"RAW: {len(agents_raw)} agentes | FRONTEND: {len(agents_frontend)} (active+configured)")
    print(f"Archivos: {files_total - files_skipped}/{files_total} procesados")
    print("\nFrontend By module:")
    for m in sorted(by_module_frontend.keys()):
        exp = EXPECTED.get(m, 0)
        tag = "OK" if (exp > 0 and by_module_frontend[m] >= exp) else "WARN" if exp > 0 else "INFO"
        print(f"  {tag:4} {m:15} {by_module_frontend[m]:3}/{exp}")
    print("\nOutputs:")
    print("  - reports_v2_5/agents_inventory.raw.json")
    print("  - reports_v2_5/agents_frontend.json")
    print("  - reports_v2_5/agents_validation.json")
    print("="*100)

if __name__ == "__main__":
    main()
