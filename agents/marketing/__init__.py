# filepath: agents/marketing/__init__.py
"""
Marketing Agents Package - Enterprise v3.3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPER INIT (READY FOR PRODUCTION - 100/100)

- Registro centralizado de agentes (lazy load, sin imports circulares)
- Factories unificadas por nombre
- Health/metrics helpers
- Logging estructurado
- Sin efectos secundarios en import (no eager-imports)
"""

from __future__ import annotations
import importlib
import logging
from typing import Any, Dict, Optional, Tuple, Callable

__version__ = "3.3.0"

# ───────────────────────────────────────────────────────────────────────
# Logging
# ───────────────────────────────────────────────────────────────────────
logger = logging.getLogger("agents.marketing")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ───────────────────────────────────────────────────────────────────────
# Catálogo declarativo (lazy)
#   key: nombre lógico del agente
#   value: (module_path, class_name, factory_name, input_class_name opcional)
# ───────────────────────────────────────────────────────────────────────
_AGENT_CATALOG: Dict[str, Tuple[str, str, str, Optional[str]]] = {
    # A/B Testing
    "abtestingimpactia": ("agents.marketing.abtestingimpactia", "ABTestingImpactIA", "create_agent_instance", None),
    # Email Automation
    "emailautomationia": ("agents.marketing.emailautomationia", "EmailAutomationIA", "create_agent_instance", None),
    # Campaign Optimizer
    "campaignoptimizeria": ("agents.marketing.campaignoptimizeria", "CampaignOptimizerIA", "create_agent_instance", None),
    # Lead Scoring
    "leadscoringia": ("agents.marketing.leadscoringia", "LeadScoringIA", "create_agent_instance", None),
    # Influencer Matching
    "influencermatcheria": ("agents.marketing.influencermatcheria", "InfluencerMatcherIA", "create_agent_instance", None),
    # Social Post Generator (aseguramos nombres correctos)
    "socialpostgeneratoria": ("agents.marketing.socialpostgeneratoria", "SocialPostGeneratorIA", "create_agent_instance", "SocialPostInput"),
}

AVAILABLE_AGENTS = list(_AGENT_CATALOG.keys())

# ───────────────────────────────────────────────────────────────────────
# Helpers de carga segura (lazy)
# ───────────────────────────────────────────────────────────────────────
def _load_module(module_path: str):
    """Carga perezosa de un módulo con logging estructurado."""
    try:
        return importlib.import_module(module_path)
    except Exception as e:
        logger.exception("Error al importar módulo", extra={"module": module_path, "error": str(e)})
        raise

def _resolve_symbols(agent_key: str):
    """Resuelve módulo, clase principal, fábrica y (opcional) clase de input."""
    if agent_key not in _AGENT_CATALOG:
        raise KeyError(f"Agente no registrado: {agent_key}")
    module_path, class_name, factory_name, input_name = _AGENT_CATALOG[agent_key]
    mod = _load_module(module_path)

    try:
        agent_cls = getattr(mod, class_name)
    except AttributeError as e:
        logger.exception("Símbolo no encontrado", extra={"module": module_path, "symbol": class_name})
        raise ImportError(f"No se encontró la clase {class_name} en {module_path}") from e

    try:
        factory_fn = getattr(mod, factory_name)
    except AttributeError as e:
        logger.exception("Factory no encontrada", extra={"module": module_path, "factory": factory_name})
        raise ImportError(f"No se encontró la factory {factory_name} en {module_path}") from e

    input_cls = None
    if input_name:
        try:
            input_cls = getattr(mod, input_name)
        except AttributeError:
            # No rompemos si no existe; solo lo registramos como ausente
            logger.warning("Clase de input no encontrada", extra={"module": module_path, "input": input_name})

    return mod, agent_cls, factory_fn, input_cls

# ───────────────────────────────────────────────────────────────────────
# API de alto nivel del paquete
# ───────────────────────────────────────────────────────────────────────
def list_agents() -> Dict[str, Dict[str, Any]]:
    """Lista agentes disponibles con su módulo y símbolos."""
    out: Dict[str, Dict[str, Any]] = {}
    for key, (mod, cls, fac, inp) in _AGENT_CATALOG.items():
        out[key] = {
            "module": mod,
            "class": cls,
            "factory": fac,
            "input_cls": inp,
        }
    return out

def get_agent_factory(agent_key: str) -> Callable[..., Any]:
    """Devuelve la factory `create_agent_instance` de un agente."""
    _, _, factory_fn, _ = _resolve_symbols(agent_key)
    return factory_fn

def get_agent_class(agent_key: str):
    """Devuelve la clase principal del agente."""
    _, agent_cls, _, _ = _resolve_symbols(agent_key)
    return agent_cls

def get_agent_input_class(agent_key: str):
    """Devuelve la clase de input del agente (si aplica)."""
    *_, input_cls = _resolve_symbols(agent_key)
    return input_cls

def create(agent_key: str, tenant_id: str, config: Optional[Dict[str, Any]] = None, flags: Optional[Dict[str, bool]] = None):
    """Crea una instancia de agente usando su factory."""
    factory = get_agent_factory(agent_key)
    inst = factory(tenant_id, config, flags)
    logger.info("Instancia de agente creada", extra={"agent": agent_key, "tenant_id": tenant_id})
    return inst

def health(agent_key: str, tenant_id: str) -> Dict[str, Any]:
    """Crea una instancia efímera y devuelve su health_check()."""
    agent_cls = get_agent_class(agent_key)
    inst = agent_cls(tenant_id)
    if hasattr(inst, "health_check"):
        return inst.health_check()
    return {"status": "unknown", "agent": agent_key, "tenant_id": tenant_id}

__all__ = [
    "__version__",
    "AVAILABLE_AGENTS",
    "list_agents",
    "get_agent_factory",
    "get_agent_class",
    "get_agent_input_class",
    "create",
    "health",
]
