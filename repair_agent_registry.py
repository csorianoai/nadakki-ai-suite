# repair_agent_registry.py
import json
import importlib
import sys
from pathlib import Path

def repair_agent_registry():
    """Repara el registry para incluir solo agentes de negocio válidos"""
    
    valid_agents = {}
    agents_dir = Path("agents")
    
    # Definir ecosistemas válidos (basado en la auditoría)
    ecosystems = [
        'compliance', 'contabilidad', 'decision', 'educacion', 'experiencia',
        'fortaleza', 'inteligencia', 'investigacion', 'legal', 'logistica',
        'marketing', 'operacional', 'orchestration', 'originacion', 'presupuesto',
        'recuperacion', 'regtech', 'rrhh', 'ventascrm', 'vigilancia'
    ]
    
    for ecosystem in ecosystems:
        ecosystem_path = agents_dir / ecosystem
        if ecosystem_path.exists():
            for agent_file in ecosystem_path.glob("*.py"):
                if agent_file.name != "__init__.py":
                    agent_name = agent_file.stem
                    # Contar líneas de código
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                    
                    valid_agents[agent_name] = {
                        "ecosystem": ecosystem,
                        "file_path": str(agent_file),
                        "status": "active",
                        "line_count": line_count,
                        "registered": True
                    }
    
    # Guardar nuevo registry
    with open('agent_registry.json', 'w', encoding='utf-8') as f:
        json.dump(valid_agents, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Registry reparado: {len(valid_agents)} agentes válidos registrados")
    return valid_agents

if __name__ == "__main__":
    repair_agent_registry()
