"""
Script de corrección masiva para 17 agentes
Aplica el patrón de los 7 agentes que funcionan
"""

import os
import re
from pathlib import Path

# Agentes a corregir
AGENTS_TO_FIX = [
    "leadscoringia.py",
    "campaignoptimizeria.py",
    "conversioncohortia.py",
    "contentperformanceia.py",
    "contactqualityia.py",
    "abtestingimpactia.py",
    "attributionmodelia.py",
    "creativeanalyzeria.py",
    "marketingmixmodelia.py",
    "budgetforecastia.py",
    "competitoranalyzeria.py",
    "competitorintelligenceia.py",
    "journeyoptimizeria.py",
    "personalizationengineia.py",
    "socialpostgeneratoria.py",
    "influencermatcheria.py",
    "influencermatchingia.py"
]

def fix_agent(file_path: Path):
    """Corrige un agente para usar Dict en vez de objetos"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Cambiar signature de execute para aceptar Dict
    # De: async def execute(self, lead: Lead)
    # A:  async def execute(self, data: Dict[str, Any])
    
    patterns = [
        (r'async def execute\(self, (\w+): (\w+)\)', 
         r'async def execute(self, data: Dict[str, Any])'),
        (r'def execute\(self, (\w+): (\w+)\)', 
         r'def execute(self, data: Dict[str, Any])'),
    ]
    
    for old, new in patterns:
        content = re.sub(old, new, content)
    
    # 2. Agregar import de Dict si no está
    if 'from typing import' in content and 'Dict' not in content:
        content = content.replace(
            'from typing import ',
            'from typing import Dict, '
        )
    elif 'from typing import' not in content:
        # Agregar import completo
        import_line = 'from typing import Dict, Any, List, Optional\n'
        content = import_line + content
    
    # 3. Cambiar accesos de atributos por dict.get()
    # Patrón común: obj.attr → data.get('attr')
    # Esto es complejo, mejor hacerlo manualmente o con más contexto
    
    # Solo guardar si hubo cambios
    if content != original_content:
        # Backup
        backup_path = file_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Guardar corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def main():
    agents_dir = Path("agents/marketing")
    
    print("=" * 60)
    print("CORRECCIÓN MASIVA DE AGENTES")
    print("=" * 60)
    print()
    
    fixed_count = 0
    
    for agent_file in AGENTS_TO_FIX:
        file_path = agents_dir / agent_file
        
        if not file_path.exists():
            print(f"⚠️  {agent_file} - No encontrado")
            continue
        
        print(f"→ Procesando {agent_file}...", end=" ")
        
        try:
            if fix_agent(file_path):
                print("✓ Corregido")
                fixed_count += 1
            else:
                print("○ Sin cambios")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"Agentes corregidos: {fixed_count}/{len(AGENTS_TO_FIX)}")
    print("=" * 60)
    print()
    print("NOTA: Corrección automática de signatures completa")
    print("Corrección manual necesaria para lógica interna")

if __name__ == "__main__":
    main()
