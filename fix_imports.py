"""
Corrige imports faltantes en agentes con shim
"""

from pathlib import Path
import re

AGENTS = [
    "leadscoringia.py",
    "campaignoptimizeria.py",
    "contactqualityia.py",
    "attributionmodelia.py",
    "socialpostgeneratoria.py"
]

def fix_imports(file_path: Path):
    """Asegura que Dict y Any estén importados"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Verificar si ya tiene los imports necesarios
    has_dict = 'Dict' in content
    has_any = 'Any' in content
    has_typing_import = re.search(r'from typing import', content)
    
    if has_typing_import and not (has_dict and has_any):
        # Ya tiene import de typing, agregar Dict y Any si faltan
        typing_line = has_typing_import.group(0)
        
        # Extraer lo que ya está importado
        match = re.search(r'from typing import\s+(.*?)(?:\n|$)', content)
        if match:
            current_imports = match.group(1).strip()
            
            # Construir nuevos imports
            imports_list = [x.strip() for x in current_imports.split(',')]
            
            if not has_dict and 'Dict' not in imports_list:
                imports_list.insert(0, 'Dict')
            if not has_any and 'Any' not in imports_list:
                imports_list.insert(1, 'Any')
            
            new_import_line = f"from typing import {', '.join(imports_list)}"
            content = content.replace(match.group(0), new_import_line)
    
    elif not has_typing_import:
        # No tiene import de typing, agregarlo al inicio
        lines = content.split('\n')
        
        # Buscar después de los imports estándar
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
        
        lines.insert(insert_pos, 'from typing import Dict, Any, List, Optional')
        content = '\n'.join(lines)
    
    # Solo guardar si hubo cambios
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    agents_dir = Path("agents/marketing")
    
    print("=" * 60)
    print("CORREGIR IMPORTS")
    print("=" * 60)
    print()
    
    fixed = 0
    
    for agent_file in AGENTS:
        file_path = agents_dir / agent_file
        
        if not file_path.exists():
            print(f"⚠  {agent_file} - No encontrado")
            continue
        
        print(f"→ {agent_file}...", end=" ")
        
        try:
            if fix_imports(file_path):
                print("✓ Imports corregidos")
                fixed += 1
            else:
                print("○ Ya tenía imports correctos")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"Archivos corregidos: {fixed}/5")
    print("=" * 60)

if __name__ == "__main__":
    main()
