"""
Agent Runner - Carga y ejecucion segura de agentes por file_path
Usa importlib.util.spec_from_file_location porque file_path es ruta de archivo, no modulo Python.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# Raiz del proyecto (donde esta main.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_AGENTS_ROOT = _PROJECT_ROOT / "agents"


class AgentLoadError(Exception):
    """Error al cargar un agente."""
    pass


def _validate_path(file_path: str) -> Path:
    """Valida que file_path sea seguro y exista dentro de agents/."""
    # Rechazar traversal
    if ".." in file_path or file_path.startswith("/") or ":" in file_path:
        raise AgentLoadError(f"Path inseguro: {file_path}")

    resolved = (_AGENTS_ROOT / file_path).resolve()

    # Verificar que no escapa de agents/
    if not str(resolved).startswith(str(_AGENTS_ROOT.resolve())):
        raise AgentLoadError(f"Path escapa de agents/: {file_path}")

    if not resolved.exists():
        raise AgentLoadError(f"Archivo no encontrado: {file_path}")

    if not resolved.suffix == ".py":
        raise AgentLoadError(f"No es archivo Python: {file_path}")

    return resolved


def safe_load(file_path: str, class_name: str) -> Any:
    """
    Carga dinamica de un agente desde file_path (relativo a agents/).

    Args:
        file_path: Ruta relativa a agents/ (ej: "marketing/abtestingia.py")
        class_name: Nombre de la clase a instanciar (ej: "ABTestingAgentOperative")

    Returns:
        Instancia de la clase del agente

    Raises:
        AgentLoadError: Si el path es inseguro, el archivo no existe,
                        o la clase no se encuentra.
    """
    resolved = _validate_path(file_path)

    module_name = f"_agent_runner_.{file_path.replace('/', '.').replace('.py', '')}"

    try:
        spec = importlib.util.spec_from_file_location(module_name, str(resolved))
        if spec is None or spec.loader is None:
            raise AgentLoadError(f"No se pudo crear spec para: {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except AgentLoadError:
        raise
    except Exception as e:
        raise AgentLoadError(f"Error cargando modulo {file_path}: {e}")

    cls = getattr(module, class_name, None)
    if cls is None:
        raise AgentLoadError(
            f"Clase '{class_name}' no encontrada en {file_path}"
        )

    try:
        return cls()
    except Exception as e:
        raise AgentLoadError(f"Error instanciando {class_name}: {e}")


def execute_agent(
    file_path: str,
    class_name: str,
    payload: Dict[str, Any],
    dry_run: bool = True,
    tenant_id: str = "default",
) -> Dict[str, Any]:
    """
    Carga y ejecuta un agente.

    Args:
        file_path: Ruta relativa a agents/
        class_name: Nombre de la clase
        payload: Datos de entrada para el agente
        dry_run: Si True, agrega flag dry_run al payload
        tenant_id: ID del tenant

    Returns:
        Resultado de la ejecucion del agente
    """
    instance = safe_load(file_path, class_name)

    if not hasattr(instance, "execute"):
        raise AgentLoadError(
            f"{class_name} no tiene metodo execute()"
        )

    if dry_run:
        payload = {**payload, "dry_run": True}

    return instance.execute(payload, tenant_id=tenant_id)
