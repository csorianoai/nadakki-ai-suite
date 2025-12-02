# scripts/validate_agent_registry.py
import json
from pathlib import Path

def validate_agent_registry():
    """Valida que el registry solo contenga agentes de negocio válidos"""
    agents_dir = Path("agents")
    valid_ecosystems = [
        'compliance', 'contabilidad', 'decision', 'educacion', 'experiencia',
        'fortaleza', 'inteligencia', 'investigacion', 'legal', 'logistica',
        'marketing', 'operacional', 'orchestration', 'originacion', 'presupuesto',
        'recuperacion', 'regtech', 'rrhh', 'ventascrm', 'vigilancia'
    ]
    
    try:
        with open('agent_registry.json', 'r') as f:
            registry = json.load(f)
    except FileNotFoundError:
        print("❌ Registry no encontrado")
        return False
    
    # Validar cada agente en el registry
    invalid_agents = []
    for agent_name, agent_data in registry.items():
        agent_path = Path(agent_data.get('file_path', ''))
        
        # Verificar que el archivo existe
        if not agent_path.exists():
            invalid_agents.append(agent_name)
            continue
            
        # Verificar que pertenezca a un ecosistema válido
        if agent_data.get('ecosystem') not in valid_ecosystems:
            invalid_agents.append(agent_name)
            continue
    
    if invalid_agents:
        print(f"❌ Se encontraron {len(invalid_agents)} agentes inválidos en el registry")
        return False
    else:
        print(f"✅ Registry válido: {len(registry)} agentes de negocio")
        return True

if __name__ == "__main__":
    validate_agent_registry()
