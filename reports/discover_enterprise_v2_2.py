#!/usr/bin/env python3
"""
NADAKKI AI Suite - Total Agent Discovery ENTERPRISE v2.2
Fixes:
- Marketing: sin regla por tamaño (solo execute/run + clase autónoma + AI imports)
- Marketing: excluye carpetas de soporte (helpers, schemas, utils, etc.)
- Domain signals fortalecidos para Legal/Logística/Contabilidad
- Dos outputs: raw (todos) + frontend (active+configured)
"""
import json, ast, hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

AGENTS_ROOT = Path.cwd() / "agents"
REPORTS_DIR = Path.cwd() / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

FOLDER_BLACKLIST = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    "backup", "legacy", "tests", "testing", "test", ".pytest_cache",
    ".idea", ".vscode"
}

# Subcarpetas de SOPORTE (no agentes) en Marketing
SUPPORT_DIR_HINTS = {
    "utils", "util", "helpers", "helper", "common", "shared", "core",
    "schemas", "schema", "types", "constants", "config", "configs",
    "templates", "template", "prompts", "prompt", "clients", "client",
    "integrations", "integration", "services", "service", "lib", "base",
    "wrappers", "wrapper", "decorators", "decorator", "middleware"
}

AI_KEYWORDS = [
    "openai","anthropic","claude","gpt","llm","embedding","chatcompletion",
    "pydantic","fastapi","langchain","llamaindex","crewai",
    "predict","classification","scoring","risk","decision","automation","orchestrat","pipeline","analyze"
]

AUTONOMOUS_CLASS_HINTS = [
    "agent","ia","assistant","orchestrator","coordinator","manager",
    "optimizer","strategist","controller","sentinel","profiler","oracle",
    "tester","pathway","recovery","collection","analyzer","router"
]

AGENT_IMPORTS = ["openai","anthropic","langchain","llamaindex","crewai","fastapi","pydantic"]

UTILS_ANTI = ["argparse","click","typer","logging",'if __name__ == "__main__"']

PLATFORM_RULES = {
    "google_ads": ["googleads","google ads","adwords","gads","rsa","search terms","budget pacing"],
    "meta_ads": ["facebook ads","instagram ads","meta ads","lookalike","pixel","capi"],
    "linkedin_ads": ["linkedin ads","sponsored content","campaign manager"],
    "tiktok_ads": ["tiktok ads","spark ads","ttads"],
}

CATEGORY_RULES = [
    (("penal","procesal","constitucional","civil","laboral","tribut","comercial"), "legal"),
    (("campaign","keyword","roas","ctr","conversion","creative","audience"), "marketing_ads"),
    (("factur","fiscal","reconcili","contab","flujo","balance"), "accounting"),
    (("logistic","invent","warehouse","rutas","transporte"), "logistics"),
    (("rrhh","nomina","cv","talent","seleccion"), "hr"),
    (("presupuesto","forecast","budget"), "budgeting"),
    (("investig","tendencia","innovacion"), "research"),
    (("ventas","crm","pipeline","cliente"), "sales"),
    (("aml","regtech","compliance","kyc"), "compliance"),
    (("recovery","recuper","cobro","collection"), "recovery"),
    (("originacion","underwrite","sentinel"), "origination"),
]

MODULE_MAP = {
    "marketing":"marketing", "legal":"legal", "contabilidad":"contabilidad",
    "logistica":"logistica", "presupuesto":"presupuesto", "rrhh":"rrhh",
    "educacion":"educacion", "investigacion":"investigacion", "ventascrm":"ventascrm",
    "regtech":"regtech", "recuperacion":"recuperacion", "originacion":"originacion"
}

# DOMAIN HINTS para mejorar detección en Legal/Logística/Contabilidad
DOMAIN_HINTS = {
    "legal": ["penal","procesal","constitucional","civil","laboral","tribut","comercial","notarial","marit"],
    "contabilidad": ["dgii","itbis","606","607","fiscal","factur","contab","reconcili"],
    "logistica": ["invent","almacen","rutas","transporte","trazabil","demanda","proveedor"],
    "rrhh": ["nomina","cv","seleccion","talento","capacit","performance"],
    "presupuesto": ["presupuesto","forecast","budget","planificacion"],
    "regtech": ["aml","kyc","compliance","ofac","pep","transaction"],
}

EXPECTED = {
    "marketing": 44, "legal": 33, "contabilidad": 21, "logistica": 23,
    "presupuesto": 13, "rrhh": 10, "educacion": 9, "investigacion": 9,
    "ventascrm": 9, "regtech": 8, "recuperacion": 5, "originacion": 10, "otros": 20
}

def safe_read(fp):
    for enc in ["utf-8","latin-1","cp1252","iso-8859-1"]:
        try:
            return fp.read_text(encoding=enc)
        except:
            pass
    return ""

def parse_ast(content):
    try:
        return ast.parse(content)
    except:
        return ast.Module(body=[], type_ignores=[])

def has_top_fn(tree, names):
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names:
            return True
    return False

def class_has_method(tree, names):
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)) and b.name in names:
                    return True
    return False

def has_auto_class(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            nm = (n.name or "").lower()
            if any(h in nm for h in AUTONOMOUS_CLASS_HINTS):
                return True
    return False

def has_ai_imports(cl):
    return any(imp in cl for imp in AGENT_IMPORTS)

def has_ai_logic(cl):
    return sum(1 for kw in AI_KEYWORDS if kw in cl) >= 2

def det_module(parts):
    if not parts:
        return "otros"
    return MODULE_MAP.get(parts[0].lower(), "otros")

def is_support_subdir(rel_parts):
    """Detecta si está en subcarpeta de soporte"""
    # rel_parts = ["marketing", "subfolder", "subsubfolder", ...]
    if not rel_parts or rel_parts[0].lower() != "marketing":
        return False
    subs = [p.lower() for p in rel_parts[1:3]]
    return any(s in SUPPORT_DIR_HINTS for s in subs)

def det_platform(module, rel, cl):
    if module != "marketing":
        return None
    scope = rel.lower() + " " + cl
    for plat, kws in PLATFORM_RULES.items():
        if sum(1 for k in kws if k in scope) >= 2:
            return plat
    return None

def det_category(cl, parts):
    scope = cl + " " + " ".join(parts)
    for kws, cat in CATEGORY_RULES:
        if any(k in scope for k in kws):
            return cat
    return "general"

def det_status(tree, cl):
    if has_top_fn(tree, {"execute","run"}) or class_has_method(tree, {"execute","run"}):
        return "active"
    if has_ai_logic(cl) or has_auto_class(tree) or has_ai_imports(cl):
        return "configured"
    return "template"

agents = []
by_module = defaultdict(int)
files_total = 0
files_ignored = 0

print("\n" + "="*100)
print("NADAKKI — DISCOVERY ENTERPRISE v2.2")
print("="*100 + "\n")

if not AGENTS_ROOT.exists():
    raise SystemExit(f"ERROR: {AGENTS_ROOT}")

for fp in sorted(AGENTS_ROOT.rglob("*.py")):
    files_total += 1

    if any(p.lower() in FOLDER_BLACKLIST for p in fp.parts):
        files_ignored += 1
        continue

    content = safe_read(fp)
    if not content.strip():
        continue

    rel = fp.relative_to(AGENTS_ROOT).as_posix()
    parts = rel.split("/")[:-1]
    module = det_module(parts)

    lines = content.count("\n") + 1
    cl = content.lower()
    tree = parse_ast(content)

    # REGLAS FUERTES
    rule1 = has_top_fn(tree, {"execute","run"})
    rule2 = class_has_method(tree, {"execute","run"})
    rule3 = has_auto_class(tree)
    rule4 = has_ai_logic(cl) or has_ai_imports(cl)

    # FIX: Marketing excluye soporte salvo execute/run
    if module == "marketing" and is_support_subdir(parts) and not (rule1 or rule2):
        continue

    # FIX: Domain signals para otros módulos
    has_domain = any(k in cl for k in DOMAIN_HINTS.get(module, []))
    rule5 = has_domain and lines > 80 and (has_auto_class(tree) or has_ai_imports(cl))

    is_agent = rule1 or rule2 or rule3 or rule4 or rule5

    if not is_agent:
        continue

    reasons = []
    if rule1: reasons.append("execute_function")
    if rule2: reasons.append("class_method")
    if rule3: reasons.append("autonomous_class")
    if rule4: reasons.append("ai_signals")
    if rule5: reasons.append("domain_signals")

    h = hashlib.md5(rel.encode()).hexdigest()[:6]
    aid = Path(fp.name).stem.lower() + f"_{h}"

    agents.append({
        "agent_id": aid,
        "filename": fp.name,
        "file_path": rel,
        "module": module,
        "platform": det_platform(module, rel, cl),
        "category": det_category(cl, parts),
        "status": det_status(tree, cl),
        "lines": lines,
        "reason_detected": " | ".join(reasons[:3])
    })

    by_module[module] += 1

# Frontend: solo active + configured
agents_ui = [a for a in agents if a["status"] in ("active", "configured")]
by_module_ui = defaultdict(int)
for a in agents_ui:
    by_module_ui[a["module"]] += 1

inventory_raw = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "discovery_method": "semantic_v2.2_enterprise",
    "total_agents_found": len(agents),
    "by_module": dict(sorted(by_module.items())),
    "agents": agents
}

inventory_ui = {
    "generated_at": inventory_raw["generated_at"],
    "total_agents_ui": len(agents_ui),
    "by_module_ui": dict(sorted(by_module_ui.items())),
    "agents": agents_ui
}

validation = {
    "expected": EXPECTED,
    "found_raw": inventory_raw["by_module"],
    "found_ui": inventory_ui["by_module_ui"],
    "comparison": {},
    "summary": {
        "files_total": files_total,
        "files_ignored": files_ignored,
        "agents_raw": len(agents),
        "agents_ui": len(agents_ui)
    }
}

for m, exp in EXPECTED.items():
    found = by_module_ui.get(m, 0)
    validation["comparison"][m] = {
        "expected": exp,
        "found_ui": found,
        "missing": max(exp - found, 0),
        "status": "ok" if found >= exp else "warn" if found > 0 else "critical"
    }

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

save_json(REPORTS_DIR / "agents_inventory.raw.json", inventory_raw)
save_json(REPORTS_DIR / "agents_inventory.frontend.json", inventory_ui)
save_json(REPORTS_DIR / "agents_validation.json", validation)

print("="*100)
print(f"RAW: {len(agents)} agentes | UI: {len(agents_ui)} (active+configured)")
print(f"Archivos: {files_total - files_ignored}/{files_total} procesados")
print("\nUI By module:")
for m in sorted(by_module_ui.keys()):
    exp = EXPECTED.get(m, 0)
    found = by_module_ui[m]
    tag = "OK" if found >= exp else "WARN"
    print(f"  {tag} {m:15} {found:3}/{exp}")

print("\nOutputs:")
print("  - agents_inventory.raw.json")
print("  - agents_inventory.frontend.json   <-- USA EL FRONTEND")
print("  - agents_validation.json")
print("="*100)
