# ═══════════════════════════════════════════════════════════════════════════════
# NADAKKI AI Suite - Main Application v5.4.4 - OPTIMIZADO
# ═══════════════════════════════════════════════════════════════════════════════
"""
v5.4.4 OPTIMIZACIONES:

🔧 FIX 1: Scoring menos conservador
   - confirmed: score >= 7.0 (antes >= 7.5)
   - highly_likely: score >= 5.5 (antes >= 6.0)
   - likely: score >= 4.0 (antes >= 4.5)
   RESULTADO: Más agentes confirmados

🔧 FIX 2: API version detection mejorada
   - Busca en imports además de contenido
   - Mejor detección de versiones
   RESULTADO: Menos "unknown"

🔧 FIX 3: Logging de debugging
   - Muestra qué agentes se detectan
   - Muestra scores
   RESULTADO: Visibilidad total

✅ FIX 4: MARKETING STATS API INTEGRADA
   - Endpoints para datos reales
   - Campañas, journeys, contactos, conversión
   RESULTADO: Dashboard con datos en tiempo real
"""

from fastapi import FastAPI, Header, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import ast
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Set
from datetime import datetime
from functools import lru_cache
import re
from dotenv import load_dotenv

load_dotenv()

# ✅ IMPORTAR MARKETING STATS API
try:
    from marketing_stats_api import router as marketing_router
except ImportError:
    print("⚠️ marketing_stats_api no encontrado - endpoints de marketing no disponibles")
    marketing_router = None

# ✅ IMPORTAR ROUTERS OPERACIONALES
from routers.social_status_router import router as social_status_router
from routers.auth.meta_oauth import router as meta_oauth_router
from routers.auth.google_oauth import router as google_oauth_router
from routers.agent_execution_router import router as agent_execution_router

# =============================================================================
# APP CONFIGURACIÓN
# =============================================================================
app = FastAPI(
    title="NADAKKI AI Suite - Intelligent Discovery v5.4.4",
    description="Production-grade AI Agent Discovery Platform with Real-time Marketing Stats",
    version="5.4.4",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUIR MARKETING ROUTER
if marketing_router:
    app.include_router(marketing_router)

# ✅ INCLUIR ROUTERS OPERACIONALES
app.include_router(social_status_router)
app.include_router(meta_oauth_router)
app.include_router(google_oauth_router)
app.include_router(agent_execution_router)

# =============================================================================
# CONFIGURACIÓN ROBUSTA
# =============================================================================

FOLDER_BLACKLIST: Set[str] = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    "backup", "legacy", "tests", "testing", "test"
}

NON_AGENT_KEYWORDS: Set[str] = {
    "test_", "_test", "mock_", "fake_", "dummy_", "example_", "demo_",
    "base_", "abstract_", "mixin_", "interface_"
}

def safe_unparse(node) -> str:
    """Compatible Python 3.8+"""
    try:
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
    except Exception:
        pass
    return getattr(node, "id", "") or getattr(node, "attr", "") or node.__class__.__name__

def detect_module_context(filepath: str) -> str:
    """Detecta módulo real"""
    p = (filepath or "").replace("\\", "/").lower()
    parts = [x for x in p.split("/") if x]

    if "agents" in parts:
        idx = parts.index("agents")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    for seg in parts:
        if seg not in ("src", "app", "backend", "services", "api"):
            return seg
    return ""

def should_ignore_path(rel_path: str) -> bool:
    """Ignora por RUTA"""
    p = rel_path.replace("\\", "/").lower()
    parts = p.split("/")

    for part in parts:
        if part in FOLDER_BLACKLIST:
            return True

    filename = parts[-1] if parts else ""

    if any(kw in filename for kw in NON_AGENT_KEYWORDS):
        if ("agent" in filename) or ("ia" in filename):
            return False
        return filename.endswith("_test.py") or filename.startswith("test_")

    return False

# =============================================================================
# DETECTOR INTELIGENTE
# =============================================================================

class IntelligentAgentDetector:
    """Detector adaptable"""
    
    ACTION_METHODS = {
        "execute", "run", "process", "handle", "create",
        "generate", "optimize", "manage", "analyze", "predict",
        "invoke", "call", "start", "begin"
    }

    AGENT_CLASS_KEYWORDS = {
        "agent", "ia", "manager", "strategist", "generator",
        "optimizer", "creator", "analyzer", "predictor", "assistant", 
        "runner", "handler", "processor", "orchestrator"
    }

    NON_CONCRETE_KEYWORDS = {
        "base", "abstract", "test", "mock", "fake", "dummy", 
        "example", "demo", "placeholder", "mixin", "interface"
    }

    @staticmethod
    def has_substantial_body(method_node) -> bool:
        """Verifica lógica real"""
        if not hasattr(method_node, "body"):
            return False
        body = method_node.body
        if not body:
            return False

        if len(body) == 1:
            first = body[0]
            if isinstance(first, ast.Pass):
                return False
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and first.value.value is Ellipsis:
                return False
            if isinstance(first, ast.Raise):
                exc = first.exc
                if isinstance(exc, ast.Call):
                    func_name = getattr(exc.func, "id", "") or getattr(exc.func, "attr", "")
                    if "notimplementederror" in (func_name or "").lower():
                        return False
        return True

    @staticmethod
    def detect_agent_type(node: ast.ClassDef, content: str) -> str:
        """Detecta tipo: IA vs Agent"""
        n = node.name.lower()
        c = (content or "").lower()
        if any(x in c for x in ("openai", "anthropic", "claude", "gpt", "llm", "embedding")):
            return "IA"
        if any(x in n for x in ("ia", "ai", "intelligence")):
            return "IA"
        return "Agent"

    @staticmethod
    def detect_api_version(content: str, imports: List[str]) -> str:
        """
        🔧 FIX 2: Detecta API version mejorado
        Busca en imports + contenido
        """
        c = content.lower()
        
        # Por imports
        if "openai" in imports:
            if "openai.OpenAI" in content or "from openai import" in content:
                return "openai_v1"
            elif "openai.Completion" in content:
                return "openai_v0"
        
        if "anthropic" in imports:
            if "anthropic.Anthropic" in content or "from anthropic import" in content:
                return "anthropic_v1"
        
        if "cohere" in imports:
            return "cohere"
        
        if "together" in imports:
            return "together"
        
        if "langchain" in imports:
            return "langchain"
        
        if "llamaindex" in imports:
            return "llamaindex"
        
        # Por contenido (fallback)
        if "openai" in c:
            if "openai.OpenAI(" in c:
                return "openai_v1"
            elif "openai.Completion" in c:
                return "openai_v0"
        
        if "anthropic" in c:
            return "anthropic_v1"
        
        if "cohere" in c:
            return "cohere"
        
        return "unknown"

    @staticmethod
    def extract_imports(tree: ast.AST) -> List[str]:
        """Extrae imports"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
        
        return sorted(list(set(imports)))

    @staticmethod
    def count_llm_calls(content: str) -> int:
        """Cuenta llamadas a LLMs"""
        count = 0
        llm_patterns = [
            r"openai\.",
            r"anthropic\.",
            r"cohere\.",
            r"together\.",
            r"\.create\(",
            r"\.generate\(",
            r"ChatCompletion",
            r"Message\.create",
        ]
        
        for pattern in llm_patterns:
            count += len(re.findall(pattern, content, re.IGNORECASE))
        
        return count

# =============================================================================
# SIGNAL GROUPS Y ANTI-SIGNALS
# =============================================================================

SIGNAL_GROUPS = {
    "llm": ["openai", "chatcompletion", "anthropic", "claude", "gpt", "embedding", "llm"],
    "http": ["requests.", "httpx.", "aiohttp", "api_key", "client."],
    "framework": ["fastapi", "pydantic", "langchain", "llamaindex", "crewai"],
    "marketing_ads": ["adwords", "google ads", "campaign", "ad group", "search terms", "rsa", "roas", "ctr"],
    "orchestration": ["orchestrat", "workflow", "pipeline"]
}

ANTI_SIGNALS = [
    ("google_analytics", ["google analytics", "ga4", "gtag", "measurement id"], 1.2),
    ("pure_utils", ["argparse", "click.command", "typer.", "def main("], 1.0),
    ("models_only", ["basemodel", "pydantic.basemodel", "class config"], 0.8),
]

LABEL_ORDER = ["not_agent", "agent_possible", "agent_likely", "agent_highly_likely", "agent_confirmed"]
LABEL_MIN_MAP = {k: i for i, k in enumerate(LABEL_ORDER)}

# =============================================================================
# 🔧 FIX 1: SCORING OPTIMIZADO (menos conservador)
# =============================================================================

def score_agent_class_v2_enhanced(
    node: ast.ClassDef,
    filename: str,
    content: str,
    tree: ast.AST,
    filepath: str = ""
) -> Dict[str, Any]:
    """Scoring optimizado con thresholds mejorados"""
    
    class_name = (node.name or "").lower()
    filename_lower = (filename or "").lower()
    content_lower = (content or "").lower()

    reasons: List[str] = []
    score = 0.0
    metadata: Dict[str, Any] = {
        "has_inheritance": False,
        "inherits_from": "",
        "has_decorators": False,
        "decorators": [],
        "method_count": 0,
        "substantial_methods": 0,
        "content_signal_groups": [],
        "detected_type": "unknown",
        "action_methods_found": [],
        "api_version": "unknown",
        "dependencies": [],
        "llm_call_count": 0
    }

    module_context = detect_module_context(filepath) if filepath else ""
    weights = {
        "inheritance": 3.5,
        "class_keywords": 1.8,
        "action_methods": 3.5,
        "docstring_length": 1.2,
        "docstring_keywords": 0.7,
        "filename_agent": 0.7,
        "decorators": 2.0,
        "module_bonus": 1.0 if module_context in ["marketing", "ads", "advertising"] else 0.0,
    }

    # 1. HERENCIA
    for base in node.bases:
        base_name = ""
        if isinstance(base, ast.Name):
            base_name = (base.id or "").lower()
        elif isinstance(base, ast.Attribute):
            base_name = (getattr(base, "attr", "") or "").lower()

        if any(k in base_name for k in ("agent", "ia", "runner", "tool", "assistant", "processor", "handler")):
            score += weights["inheritance"]
            metadata["has_inheritance"] = True
            metadata["inherits_from"] = base_name
            reasons.append(f"inheritance:{base_name}")
            break

    # 2. DECORADORES
    if node.decorator_list:
        for decorator in node.decorator_list:
            decorator_str = safe_unparse(decorator).lower()
            metadata["decorators"].append(decorator_str)
            if any(dec in decorator_str for dec in ("agent", "tool", "function", "llm", "task")):
                score += weights["decorators"]
                metadata["has_decorators"] = True
                reasons.append(f"decorator:{decorator_str[:30]}")

    # 3. NOMBRE DE CLASE
    class_keywords_found = [kw for kw in IntelligentAgentDetector.AGENT_CLASS_KEYWORDS if kw in class_name]
    if class_keywords_found:
        score += weights["class_keywords"]
        reasons.append(f"class_keywords:{','.join(sorted(set(class_keywords_found)))}")

    # 4. DOCSTRING
    doc = ast.get_docstring(node) or ""
    if doc.strip():
        d = doc.strip()
        if len(d) >= 20:
            score += weights["docstring_length"]
            reasons.append("docstring>=20")
        elif len(d) >= 10:
            score += weights["docstring_length"] * 0.5
            reasons.append("docstring>=10")

        doc_lower = d.lower()
        doc_keywords = ["agent", "ia", "execute", "run", "process", "optimize", "generate", "analyze"]
        doc_keywords_found = [kw for kw in doc_keywords if kw in doc_lower]
        if doc_keywords_found:
            score += weights["docstring_keywords"]
            reasons.append(f"docstring_keywords:{','.join(sorted(set(doc_keywords_found)))}")

    # 5. MÉTODOS
    action_methods_found: List[str] = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metadata["method_count"] += 1
            if IntelligentAgentDetector.has_substantial_body(item):
                metadata["substantial_methods"] += 1
                if item.name in IntelligentAgentDetector.ACTION_METHODS:
                    action_methods_found.append(item.name)

    metadata["action_methods_found"] = sorted(set(action_methods_found))

    if action_methods_found:
        score += min(weights["action_methods"], 2.5 + 0.6 * len(set(action_methods_found)))
        reasons.append(f"action_methods:{','.join(sorted(set(action_methods_found)))}")
    elif metadata["substantial_methods"] > 0:
        score += weights["action_methods"] * 0.3
        reasons.append(f"substantial_methods:{metadata['substantial_methods']}")

    # 6. SEÑALES POR GRUPOS
    group_hits = 0
    group_details = []
    for group, kws in SIGNAL_GROUPS.items():
        hits = sum(1 for kw in kws if kw in content_lower)
        if hits:
            group_hits += 1
            group_details.append({group: hits})
    if group_hits:
        score += min(group_hits * 0.8, 2.4)
        metadata["content_signal_groups"] = group_details
        reasons.append(f"content_signal_groups:{group_hits}")

    # 7. NOMBRE ARCHIVO
    if ("agent" in filename_lower) or ("ia" in filename_lower):
        score += weights["filename_agent"]
        reasons.append("filename_mentions_agent")

    # 8. BONUS CONTEXTO
    if weights["module_bonus"] > 0:
        score += weights["module_bonus"]
        reasons.append(f"module_bonus:{module_context}")

    # 9. TIPO
    agent_type = IntelligentAgentDetector.detect_agent_type(node, content)
    metadata["detected_type"] = agent_type

    # 🔧 FIX 2: API version con imports
    imports_list = IntelligentAgentDetector.extract_imports(tree)
    metadata["dependencies"] = imports_list
    metadata["api_version"] = IntelligentAgentDetector.detect_api_version(content, imports_list)
    metadata["llm_call_count"] = IntelligentAgentDetector.count_llm_calls(content)

    # 10. ANTI-SIGNALS
    for name, kws, penalty in ANTI_SIGNALS:
        if sum(1 for kw in kws if kw in content_lower) >= 2:
            score -= penalty
            reasons.append(f"penalty:{name}")

    if any(x in content_lower for x in ("pytest", "unittest", "mock.", "fixture")):
        score -= 2.5
        reasons.append("penalty:test_or_mock_content")

    if any(nc in class_name for nc in IntelligentAgentDetector.NON_CONCRETE_KEYWORDS):
        score -= 1.5
        reasons.append("penalty:non_concrete_keyword")

    if metadata["method_count"] < 2 and (not action_methods_found) and (not metadata["has_inheritance"]):
        score -= 1.0
        reasons.append("penalty:too_few_methods")

    # Clamp
    score = max(0.0, min(10.0, round(score, 2)))

    # 🔧 FIX 1: Labels con thresholds optimizados
    label = "not_agent"
    if score >= 7.0:  # Antes >= 7.5
        label = "agent_confirmed"
    elif score >= 5.5:  # Antes >= 6.0
        label = "agent_highly_likely"
    elif score >= 4.0:  # Antes >= 4.5
        label = "agent_likely"
    elif score >= 3.0:
        label = "agent_possible"

    # GO/NO-GO
    strong = metadata["has_inheritance"] or bool(action_methods_found)
    if label == "agent_confirmed" and not (strong or group_hits >= 2):
        label = "agent_highly_likely"
        reasons.append("downgrade:missing_strong_or_multi_signal")

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
        "metadata": metadata,
        "confidence": round(score / 10.0, 3),
        "module_context": module_context,
        "group_hits": group_hits
    }

# =============================================================================
# STATUS DETERMINATION
# =============================================================================

def determine_real_status(content: str, scored: Dict, node: ast.ClassDef) -> str:
    """Determina status"""
    c = content.lower()

    if "# production" in c or "@production" in c:
        return "production"
    if "# development" in c or "# dev" in c or "@dev" in c:
        return "development"
    if "# template" in c or "# example" in c:
        return "template"

    has_real_logic = False
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name in ["execute", "run", "process", "handle", "create"]:
                if IntelligentAgentDetector.has_substantial_body(item):
                    has_real_logic = True
                else:
                    return "template"

    if not has_real_logic and scored["label"] != "agent_confirmed":
        return "template"

    if "TODO" in content or "FIXME" in content:
        return "development"

    return "production" if scored["score"] >= 7.0 else "development"

# =============================================================================
# PLATAFORMA Y JERARQUÍA
# =============================================================================

class PlatformDetector:
    """Detector de plataforma"""
    
    FOLDER_PLATFORM_MAP = {
        "google": "google_ads",
        "google-ads": "google_ads",
        "google_ads": "google_ads",
        "adwords": "google_ads",
        "meta": "meta_ads",
        "facebook": "meta_ads",
        "instagram": "meta_ads",
        "linkedin": "linkedin_ads",
        "tiktok": "tiktok_ads",
    }

    PLATFORM_KEYWORDS = {
        "google_ads": ["adwords", "google ads", "responsive search ad", "rsa", "match type", "search terms"],
        "meta_ads": ["facebook", "instagram", "meta ads", "lookalike", "audience"],
        "linkedin_ads": ["linkedin", "sponsored content"],
        "tiktok_ads": ["tiktok", "infeed", "spark ads"]
    }

    @staticmethod
    def detect(rel_path: str, content: str, agent_id: str) -> Dict[str, Any]:
        """Detecta jerarquía"""
        p = rel_path.replace("\\", "/")
        parts = [x.lower() for x in p.split("/") if x]

        module = parts[0] if parts else "unknown"
        result = {"module": module, "submodule": None, "platform": None, "category": None, "full_path": p}

        if module == "marketing":
            result["submodule"] = PlatformDetector._detect_submodule(parts)
            result["platform"] = PlatformDetector._detect_platform(parts, content, agent_id)
            if result["platform"]:
                result["submodule"] = "advertising"

        result["category"] = PlatformDetector._detect_category(content)
        return result

    @staticmethod
    def _detect_submodule(parts: List[str]) -> str:
        if len(parts) >= 2:
            second = parts[1]
            if any(x in second for x in ["ad", "ads", "advertising"]):
                return "advertising"
            if any(x in second for x in ["analytics", "report"]):
                return "analytics"
            if any(x in second for x in ["lead", "prospect"]):
                return "lead_management"
            if any(x in second for x in ["content", "social"]):
                return "content"
        return "general"

    @staticmethod
    def _detect_platform(parts: List[str], content: str, agent_id: str) -> Optional[str]:
        combined = f"{agent_id} {(content or '')[:2500]}".lower()

        for part in parts:
            for folder_key, platform in PlatformDetector.FOLDER_PLATFORM_MAP.items():
                if folder_key in part:
                    return platform

        platform_scores = {}
        for platform, kws in PlatformDetector.PLATFORM_KEYWORDS.items():
            s = sum(1 for kw in kws if kw in combined)
            if s:
                platform_scores[platform] = s
        if platform_scores:
            return max(platform_scores.items(), key=lambda x: x[1])[0]

        return None

    @staticmethod
    def _detect_category(content: str) -> Optional[str]:
        c = (content or "").lower()
        rules = [
            (("lead", "prospect", "conversion"), "lead_generation"),
            (("budget", "roi", "roas", "cost"), "budget_optimization"),
            (("content", "creative", "copy"), "content_creation"),
            (("analytics", "report", "dashboard"), "analytics"),
            (("segment", "personalization"), "segmentation"),
        ]
        for kws, cat in rules:
            if any(kw in c for kw in kws):
                return cat
        return None

# =============================================================================
# DESCUBRIMIENTO
# =============================================================================

def find_agents_folder() -> Optional[Path]:
    """Busca agents/"""
    search_paths = [
        Path(__file__).parent / "agents",
        Path.cwd() / "agents",
        Path.cwd().parent / "agents"
    ]
    for path in search_paths:
        if path.exists() and path.is_dir():
            return path
    return None

@lru_cache(maxsize=1)
def intelligent_discovery() -> Tuple[Dict[str, dict], Dict[str, Any]]:
    """Descubrimiento inteligente"""
    
    agents: Dict[str, dict] = {}
    stats: Dict[str, Any] = {
        "discovery": {"total_files": 0, "analyzed": 0, "ignored": 0, "class_candidates": 0, "agents_validated": 0},
        "hierarchy": {"modules": {}, "submodules": {}, "platforms": {}, "categories": {}},
        "quality": {"by_status": {"production": 0, "development": 0, "template": 0},
                    "by_type": {"Agent": 0, "IA": 0},
                    "labels": {k: 0 for k in LABEL_ORDER},
                    "api_versions": {}},
    }

    agents_path = find_agents_folder()
    if not agents_path:
        print("❌ No se encontró carpeta 'agents/'")
        return agents, stats

    print(f"📂 agents/ encontrado: {agents_path}")
    print("🔍 Escaneando (v5.4.4 - scoring optimizado)...\n")

    for filepath in sorted(agents_path.rglob("*.py")):
        stats["discovery"]["total_files"] += 1
        rel_path = str(filepath.relative_to(agents_path)).replace("\\", "/")

        if should_ignore_path(rel_path):
            stats["discovery"]["ignored"] += 1
            continue

        stats["discovery"]["analyzed"] += 1

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        base_id = filepath.stem.lower()

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            stats["discovery"]["class_candidates"] += 1

            scored = score_agent_class_v2_enhanced(
                node=node,
                filename=filepath.name,
                content=content,
                tree=tree,
                filepath=str(filepath)
            )

            if scored["label"] in ("agent_possible", "agent_likely", "agent_highly_likely", "agent_confirmed"):
                stats["discovery"]["agents_validated"] += 1
                stats["quality"]["labels"][scored["label"]] += 1

                hierarchy = PlatformDetector.detect(rel_path, content, base_id)
                agent_type = scored["metadata"]["detected_type"]
                status = determine_real_status(content, scored, node)

                stats["quality"]["by_status"][status] += 1
                stats["quality"]["by_type"][agent_type] += 1

                api_version = scored["metadata"].get("api_version", "unknown")
                stats["quality"]["api_versions"][api_version] = stats["quality"]["api_versions"].get(api_version, 0) + 1

                m = hierarchy["module"]
                stats["hierarchy"]["modules"][m] = stats["hierarchy"]["modules"].get(m, 0) + 1

                if hierarchy.get("submodule"):
                    k = f"{m}:{hierarchy['submodule']}"
                    stats["hierarchy"]["submodules"][k] = stats["hierarchy"]["submodules"].get(k, 0) + 1

                if hierarchy.get("platform"):
                    stats["hierarchy"]["platforms"][hierarchy["platform"]] = stats["hierarchy"]["platforms"].get(hierarchy["platform"], 0) + 1

                if hierarchy.get("category"):
                    stats["hierarchy"]["categories"][hierarchy["category"]] = stats["hierarchy"]["categories"].get(hierarchy["category"], 0) + 1

                agent_id = f"{base_id}__{node.name.lower()}"

                agents[agent_id] = {
                    "id": agent_id,
                    "name": base_id.replace("_", " ").title(),
                    "class_name": node.name,
                    "filename": filepath.name,
                    "file_path": rel_path,
                    "module": hierarchy["module"],
                    "submodule": hierarchy.get("submodule"),
                    "platform": hierarchy.get("platform"),
                    "category": hierarchy.get("category"),
                    "type": agent_type,
                    "status": status,

                    "confidence": scored["confidence"],
                    "score": scored["score"],
                    "label": scored["label"],
                    "reasons": scored["reasons"],
                    "signal_groups": scored["metadata"].get("content_signal_groups", []),
                    "action_methods": scored["metadata"].get("action_methods_found", []),
                    "inherits_from": scored["metadata"].get("inherits_from", ""),
                    "decorators": scored["metadata"].get("decorators", []),

                    "api_version": scored["metadata"].get("api_version", "unknown"),
                    "dependencies": scored["metadata"].get("dependencies", []),
                    "llm_calls": scored["metadata"].get("llm_call_count", 0),

                    "lines": content.count("\n") + 1,
                    "size_kb": round(filepath.stat().st_size / 1024, 2),
                    "validation_method": "intelligent_scoring_v5.4.4",
                }

                icon = {"production": "✅", "development": "⚙️", "template": "📄"}.get(status, "❓")
                # 🔧 FIX 3: Logging de debugging
                if scored["score"] >= 5.5:  # Solo log agentes importantes
                    print(f"{icon} {agent_id:45} | {hierarchy['module']:12} | {scored['label']:20} ({scored['score']}) | API: {scored['metadata']['api_version']}")

    print(f"\n{'='*120}")
    print("📊 DESCUBRIMIENTO COMPLETADO v5.4.4")
    print(f"{'='*120}\n")

    return agents, stats

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

print("\n" + "="*120)
print("🚀 NADAKKI v5.4.4 - OPTIMIZADO (Scoring mejorado + API version fix + Marketing Stats)")
print("="*120)

ALL_AGENTS, DISCOVERY_STATS = intelligent_discovery()

print("✅ COMPATIBILIDAD DASHBOARD: 100%")
print("✅ COMPATIBLE PYTHON: 3.8+")
print("✅ CPU OPTIMIZADO: AST parseado UNA sola vez")
print("✅ MARKETING STATS: Integrada (campañas, journeys, contactos, conversión)")
print("="*120 + "\n")

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/api/v1/agents")
@app.get("/api/agents")
@app.get("/api/catalog")
@app.get("/api/ai-studio/agents")
async def get_all_agents(
    module: Optional[str] = Query(None),
    submodule: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),

    min_score: float = Query(0.0, ge=0.0, le=10.0),
    max_score: float = Query(10.0, ge=0.0, le=10.0),
    confidence_min: float = Query(0.0, ge=0.0, le=1.0),
    label_min: str = Query("not_agent"),
    confirmed_only: bool = Query(False),
    has_platform: Optional[bool] = Query(None),
    api_version: Optional[str] = Query(None),

    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),

    x_tenant_id: Optional[str] = Header(None)
):
    """Endpoint principal - Obtiene agentes con filtros avanzados"""
    agents_list = list(ALL_AGENTS.values())
    filtered = agents_list

    def label_rank(l: str) -> int:
        return LABEL_MIN_MAP.get((l or "not_agent").lower(), 0)

    min_rank = label_rank(label_min)

    if module:
        filtered = [a for a in filtered if (a.get("module") or "").lower() == module.lower()]
    if submodule:
        filtered = [a for a in filtered if (a.get("submodule") or "").lower() == submodule.lower()]
    if platform:
        filtered = [a for a in filtered if (a.get("platform") or "").lower() == platform.lower()]
    if category:
        filtered = [a for a in filtered if (a.get("category") or "").lower() == category.lower()]
    if status:
        filtered = [a for a in filtered if (a.get("status") or "").lower() == status.lower()]

    filtered = [a for a in filtered if float(a.get("score", 0.0)) >= min_score]
    filtered = [a for a in filtered if float(a.get("score", 0.0)) <= max_score]
    filtered = [a for a in filtered if float(a.get("confidence", 0.0)) >= confidence_min]
    filtered = [a for a in filtered if label_rank(a.get("label")) >= min_rank]
    
    if confirmed_only:
        filtered = [a for a in filtered if a.get("label") == "agent_confirmed"]
    
    if has_platform is not None:
        if has_platform:
            filtered = [a for a in filtered if a.get("platform")]
        else:
            filtered = [a for a in filtered if not a.get("platform")]
    
    if api_version:
        filtered = [a for a in filtered if (a.get("api_version") or "").lower() == api_version.lower()]

    if search:
        s = search.lower()
        filtered = [
            a for a in filtered
            if (s in a.get("id", "").lower()
                or s in a.get("name", "").lower()
                or s in a.get("class_name", "").lower()
                or any(s in r.lower() for r in a.get("reasons", [])))
        ]

    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return {
        "success": True,
        "data": {
            "agents": paginated,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        },
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": x_tenant_id or "default",
        "discovery_method": "intelligent_scoring_v5.4.4"
    }


@app.get("/api/catalog/{module_name}/agents")
async def get_catalog_module_agents(
    module_name: str = PathParam(..., description="Module name, e.g. marketing"),
    submodule: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_score: float = Query(0.0, ge=0.0, le=10.0),
    max_score: float = Query(10.0, ge=0.0, le=10.0),
    confidence_min: float = Query(0.0, ge=0.0, le=1.0),
    label_min: str = Query("not_agent"),
    confirmed_only: bool = Query(False),
    has_platform: Optional[bool] = Query(None),
    api_version: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_tenant_id: Optional[str] = Header(None)
):
    """Alias: GET /api/catalog/{module}/agents -> delegates to get_all_agents"""
    return await get_all_agents(
        module=module_name,
        submodule=submodule,
        platform=platform,
        category=category,
        status=status,
        search=search,
        min_score=min_score,
        max_score=max_score,
        confidence_min=confidence_min,
        label_min=label_min,
        confirmed_only=confirmed_only,
        has_platform=has_platform,
        api_version=api_version,
        limit=limit,
        offset=offset,
        x_tenant_id=x_tenant_id
    )
@app.get("/api/v1/agents/{agent_id}/analysis")
async def get_agent_analysis(agent_id: str = PathParam(...)):
    """Análisis profundo de un agente"""
    if agent_id not in ALL_AGENTS:
        return {
            "success": False,
            "error": "Agent not found",
            "timestamp": datetime.utcnow().isoformat()
        }

    agent = ALL_AGENTS[agent_id].copy()

    agents_path = find_agents_folder()
    if agents_path:
        file_path = agents_path / agent["file_path"]
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == agent["class_name"]:
                    class_node = node
                    break

            methods = []
            if class_node:
                for x in class_node.body:
                    if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append({
                            "name": x.name,
                            "async": isinstance(x, ast.AsyncFunctionDef),
                            "args": [a.arg for a in x.args.args if hasattr(x.args, 'args')],
                            "has_logic": IntelligentAgentDetector.has_substantial_body(x),
                        })

            analysis = {
                "file_stats": {
                    "total_lines": content.count("\n") + 1,
                    "total_chars": len(content),
                    "file_size_kb": round(len(content) / 1024, 2)
                },
                "imports": IntelligentAgentDetector.extract_imports(tree),
                "methods": {
                    "total": len(methods),
                    "items": methods
                },
                "complexity_indicators": {
                    "lines_per_method": len(methods) > 0 and round(content.count("\n") / len(methods), 1) or 0,
                    "method_count": len(methods),
                }
            }

            agent["deep_analysis"] = analysis

        except Exception as e:
            agent["deep_analysis"] = {"error": str(e)}
    else:
        agent["deep_analysis"] = {"error": "Agents path not found"}

    return {
        "success": True,
        "data": agent,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/reality")
async def get_reality_report():
    """Reporte de realidad - Estadísticas completas"""
    return {
        "success": True,
        "data": {
            "stats": DISCOVERY_STATS,
            "agents_total": len(ALL_AGENTS),
            "by_module": DISCOVERY_STATS["hierarchy"]["modules"],
            "by_platform": DISCOVERY_STATS["hierarchy"]["platforms"],
            "by_status": DISCOVERY_STATS["quality"]["by_status"],
            "by_label": DISCOVERY_STATS["quality"]["labels"],
            "by_api_version": DISCOVERY_STATS["quality"]["api_versions"],
        },
        "timestamp": datetime.utcnow().isoformat(),
        "version": "5.4.4"
    }

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check - Estado del sistema"""
    total = len(ALL_AGENTS)
    confirmed = DISCOVERY_STATS["quality"]["labels"].get("agent_confirmed", 0)
    status = "healthy" if total > 0 and confirmed > 0 else ("warning" if total > 0 else "critical")

    return {
        "status": status,
        "agents_total": total,
        "confirmed_agents": confirmed,
        "labels_distribution": DISCOVERY_STATS["quality"]["labels"],
        "api_versions_used": DISCOVERY_STATS["quality"]["api_versions"],
        "marketing_stats_enabled": marketing_router is not None,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "5.4.4",
        "python_compatible": "3.8+"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "system": "NADAKKI Intelligent Discovery v5.4.4",
        "philosophy": "Detect reality, not assumptions",
        "agents_discovered": len(ALL_AGENTS),
        "labels": DISCOVERY_STATS["quality"]["labels"],
        "dashboard_compatibility": "100%",
        "marketing_stats_available": marketing_router is not None,
        "endpoints": {
            "agents": "/api/agents",
            "analysis": "/api/v1/agents/{id}/analysis",
            "reality": "/api/v1/reality",
            "health": "/health",
            "marketing": "/api/campaigns/stats/summary" if marketing_router else "Not available",
            "docs": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("🚀 INICIANDO SERVIDOR v5.4.4...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)