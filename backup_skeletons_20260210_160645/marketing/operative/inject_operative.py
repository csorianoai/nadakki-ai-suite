"""
═══════════════════════════════════════════════════════════════════════════════════════════════════
SCRIPT DE INYECCIÓN - CONVIERTE AGENTES ANALISTAS A OPERATIVOS
═══════════════════════════════════════════════════════════════════════════════════════════════════

Este script añade la función execute_operative() a cada agente que lo necesita.
Se ejecuta UNA VEZ para actualizar los archivos de los agentes.

IMPORTANTE: Hacer backup antes de ejecutar.

Uso:
    python agents/marketing/operative/inject_operative.py

═══════════════════════════════════════════════════════════════════════════════════════════════════
"""

import os
import re
import shutil
from datetime import datetime
from typing import List, Tuple

# Agentes a convertir (en orden de prioridad)
AGENTS_TO_CONVERT = [
    ("contentgeneratoria.py", "ContentGeneratorIA", "PUBLISH_CONTENT"),
    ("socialpostgeneratoria.py", "SocialPostGeneratorIA", "POST_SOCIAL"),
    ("sociallisteningia.py", "SocialListeningIA", "REPLY_COMMENT"),
    ("emailautomationia.py", "EmailAutomationIA", "SEND_EMAIL"),
    ("campaignoptimizeria.py", "CampaignOptimizerIA", "UPDATE_CAMPAIGN"),
    ("personalizationengineia.py", "PersonalizationEngineIA", "PERSONALIZE"),
    ("marketingorchestratorea.py", "MarketingOrchestratorEA", "ORCHESTRATE"),
    ("campaignstrategyorchestratoria.py", "CampaignStrategyOrchestratorIA", "ORCHESTRATE"),
]

# Código a inyectar al final de cada archivo
OPERATIVE_CODE_TEMPLATE = '''

# ═══════════════════════════════════════════════════════════════════════════════════════════════════
# MODO OPERATIVO - Añadido por NADAKKI Plan Turbo
# Fecha: {timestamp}
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

from typing import Dict, Any, Optional
import asyncio

# Importar componentes operativos
try:
    from agents.marketing.wrappers.operative_wrapper import (
        OperativeWrapper, ActionType, AutonomyLevel, 
        create_operative_agent, load_tenant_config
    )
    from agents.marketing.executors.meta_executor import MetaExecutor, MockMetaExecutor
    from agents.marketing.executors.email_executor import EmailExecutor, MockEmailExecutor
    OPERATIVE_IMPORTS_OK = True
except ImportError as e:
    OPERATIVE_IMPORTS_OK = False
    print(f"Warning: Could not import operative modules: {{e}}")


async def execute_operative(
    input_data: Dict[str, Any],
    tenant_id: str = "default",
    action_type: str = "{action_type}",
    auto_execute: bool = False,
    use_mock: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Ejecuta el agente en modo OPERATIVO - puede realizar acciones reales.
    
    Args:
        input_data: Datos de entrada para el agente
        tenant_id: ID del tenant (institución financiera)
        action_type: Tipo de acción (PUBLISH_CONTENT, SEND_EMAIL, etc.)
        auto_execute: Si True, ejecuta sin pedir aprobación (según autonomía)
        use_mock: Si True, usa executor mock (para testing)
        context: Contexto adicional
    
    Returns:
        Dict con:
            - status: success|failed|pending_approval|blocked_safety|blocked_circuit
            - analysis: Resultado del análisis del agente base
            - execution_result: Resultado de la acción real (si se ejecutó)
            - audit_hash: Hash de auditoría
            - confidence: Nivel de confianza (0-1)
            - error: Mensaje de error (si aplica)
    
    Ejemplo:
        result = await execute_operative(
            input_data={{"topic": "Promoción de préstamos", "platform": "facebook"}},
            tenant_id="banco_abc",
            auto_execute=True
        )
        
        if result["status"] == "success":
            print(f"Publicado: {{result['execution_result']['url']}}")
    """
    if not OPERATIVE_IMPORTS_OK:
        return {{
            "status": "failed",
            "error": "Operative modules not available",
            "analysis": None
        }}
    
    # Seleccionar executor según tipo de acción
    action = ActionType(action_type) if isinstance(action_type, str) else action_type
    
    if action in [ActionType.PUBLISH_CONTENT, ActionType.POST_SOCIAL, ActionType.REPLY_COMMENT]:
        executor = MockMetaExecutor(tenant_id) if use_mock else MetaExecutor(tenant_id)
    elif action == ActionType.SEND_EMAIL:
        executor = MockEmailExecutor(tenant_id) if use_mock else EmailExecutor(tenant_id)
    else:
        # Usar mock como fallback para otros tipos
        executor = MockMetaExecutor(tenant_id)
    
    # Crear wrapper operativo
    # Nota: Se asume que existe una instancia del agente base disponible
    # En producción, esto vendría del registro de agentes
    try:
        # Intentar obtener instancia del módulo actual
        import sys
        current_module = sys.modules[__name__]
        agent_class = getattr(current_module, '{agent_class}', None)
        
        if agent_class:
            base_agent = agent_class()
        else:
            # Fallback: crear objeto dummy con execute
            class DummyAgent:
                def execute(self, data, ctx):
                    return {{"generated_content": data.get("content", ""), "confidence": 0.8}}
            base_agent = DummyAgent()
    except Exception as e:
        return {{"status": "failed", "error": f"Could not instantiate agent: {{e}}"}}
    
    # Crear y ejecutar wrapper
    wrapper = create_operative_agent(
        base_agent=base_agent,
        executor=executor,
        tenant_id=tenant_id
    )
    
    result = await wrapper.execute_operative(
        input_data=input_data,
        action_type=action,
        force_execute=auto_execute,
        context=context
    )
    
    # Convertir resultado a dict
    return {{
        "status": result.status.value,
        "action_type": result.action_type.value,
        "analysis": result.analysis,
        "execution_result": result.execution_result,
        "confidence": result.confidence,
        "risk_level": result.risk_level,
        "requires_approval": result.requires_approval,
        "audit_hash": result.audit_hash,
        "error": result.error,
        "tenant_id": result.tenant_id,
        "execution_time_ms": result.execution_time_ms,
        "timestamp": result.timestamp
    }}


# Función síncrona para compatibilidad
def execute_operative_sync(
    input_data: Dict[str, Any],
    tenant_id: str = "default",
    action_type: str = "{action_type}",
    auto_execute: bool = False,
    use_mock: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Versión síncrona de execute_operative (usa asyncio.run internamente)"""
    return asyncio.run(execute_operative(
        input_data=input_data,
        tenant_id=tenant_id,
        action_type=action_type,
        auto_execute=auto_execute,
        use_mock=use_mock,
        context=context
    ))


# ═══════════════════════════════════════════════════════════════════════════════════════════════════
# FIN MODO OPERATIVO
# ═══════════════════════════════════════════════════════════════════════════════════════════════════
'''


def backup_file(filepath: str) -> str:
    """Crea backup del archivo antes de modificarlo"""
    backup_dir = "agents/marketing/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/{filename}.{timestamp}.bak"
    
    shutil.copy2(filepath, backup_path)
    return backup_path


def has_execute_operative(content: str) -> bool:
    """Verifica si el archivo ya tiene execute_operative"""
    return "def execute_operative" in content or "async def execute_operative" in content


def inject_operative_code(filepath: str, agent_class: str, action_type: str) -> Tuple[bool, str]:
    """
    Inyecta el código operativo en un archivo de agente.
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene execute_operative
    if has_execute_operative(content):
        return True, "Already has execute_operative (skipped)"
    
    # Crear backup
    backup_path = backup_file(filepath)
    
    # Preparar código a inyectar
    code_to_inject = OPERATIVE_CODE_TEMPLATE.format(
        timestamp=datetime.now().isoformat(),
        action_type=action_type,
        agent_class=agent_class
    )
    
    # Añadir al final del archivo
    new_content = content.rstrip() + "\n" + code_to_inject
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"Injected successfully (backup: {backup_path})"


def main():
    """Ejecuta la inyección en todos los agentes"""
    print("\n" + "=" * 80)
    print("NADAKKI AI SUITE - INYECCIÓN DE CÓDIGO OPERATIVO")
    print("=" * 80 + "\n")
    
    base_path = "agents/marketing"
    results = []
    
    for filename, agent_class, action_type in AGENTS_TO_CONVERT:
        filepath = f"{base_path}/{filename}"
        print(f"Processing: {filename}...", end=" ")
        
        success, message = inject_operative_code(filepath, agent_class, action_type)
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        
        results.append((filename, success, message))
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    success_count = sum(1 for _, success, _ in results if success)
    print(f"\nTotal: {len(results)} agentes")
    print(f"Exitosos: {success_count}")
    print(f"Fallidos: {len(results) - success_count}")
    
    if success_count == len(results):
        print("\n✅ ¡Todos los agentes han sido convertidos a OPERATIVOS!")
    else:
        print("\n⚠️  Algunos agentes no pudieron ser procesados. Revise los errores arriba.")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
