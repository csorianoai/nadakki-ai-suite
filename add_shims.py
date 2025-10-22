"""
Script para agregar shim a 5 agentes críticos
"""

import os
from pathlib import Path

# Configuración por agente
AGENTS_CONFIG = {
    "leadscoringia.py": {
        "model_class": "Lead",
        "is_async": True,
        "import_line": "from schemas.canonical import Lead"
    },
    "campaignoptimizeria.py": {
        "model_class": "Campaign",
        "is_async": True,
        "import_line": "from schemas.canonical import Campaign"
    },
    "contactqualityia.py": {
        "model_class": "ContactQualityInput",
        "is_async": True,
        "import_line": "from schemas.canonical import ContactQualityInput"
    },
    "attributionmodelia.py": {
        "model_class": "AttributionInput",
        "is_async": True,
        "import_line": "from schemas.canonical import AttributionInput"
    },
    "socialpostgeneratoria.py": {
        "model_class": "SocialPostInput",
        "is_async": True,
        "import_line": "from schemas.canonical import SocialPostInput"
    }
}

def add_shim_to_agent(file_path: Path, config: dict):
    """Agrega shim de compatibilidad a un agente"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene shim
    if "execute_dict" in content:
        print(f"  ⊙ Ya tiene shim")
        return False
    
    # Agregar import de compatibilidad si no existe
    if "from agents.agent_compat import" not in content:
        compat_import = "from agents.agent_compat import coerce_to_model\n"
        
        # Buscar dónde insertar (después de imports)
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
        
        lines.insert(insert_pos, compat_import)
        content = '\n'.join(lines)
    
    # Agregar shim al final (antes del último bloque si existe)
    model_class = config["model_class"]
    is_async = config["is_async"]
    
    if is_async:
        shim_code = f'''

# === COMPATIBILITY SHIM ===
# Agregado para soportar dict sin romper diseño original

async def execute_dict(self, data: Dict[str, Any]):
    """
    Wrapper de compatibilidad: acepta dict, convierte a modelo, llama execute original
    """
    input_model = coerce_to_model({model_class}, data)
    return await self.execute(input_model)
'''
    else:
        shim_code = f'''

# === COMPATIBILITY SHIM ===
# Agregado para soportar dict sin romper diseño original

def execute_dict(self, data: Dict[str, Any]):
    """
    Wrapper de compatibilidad: acepta dict, convierte a modelo, llama execute original
    """
    input_model = coerce_to_model({model_class}, data)
    return self.execute(input_model)
'''
    
    # Agregar shim antes de las últimas líneas (create_agent_instance, etc)
    if "def create_agent_instance" in content:
        parts = content.rsplit("def create_agent_instance", 1)
        content = parts[0] + shim_code + "\n\ndef create_agent_instance" + parts[1]
    else:
        content += shim_code
    
    # Backup
    backup_path = file_path.with_suffix('.py.shimbackup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        with open(file_path, 'r', encoding='utf-8') as orig:
            f.write(orig.read())
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    agents_dir = Path("agents/marketing")
    
    print("=" * 60)
    print("AGREGAR SHIM DE COMPATIBILIDAD")
    print("=" * 60)
    print()
    
    updated = 0
    
    for agent_file, config in AGENTS_CONFIG.items():
        file_path = agents_dir / agent_file
        
        if not file_path.exists():
            print(f"⚠  {agent_file} - No encontrado")
            continue
        
        print(f"→ {agent_file}...", end=" ")
        
        try:
            if add_shim_to_agent(file_path, config):
                print("✓ Shim agregado")
                updated += 1
            else:
                print("○ Ya tenía shim")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"Agentes actualizados: {updated}/5")
    print("=" * 60)
    print()
    
    if updated > 0:
        print("✓ Shims agregados exitosamente")
        print("✓ Diseño original preservado")
        print("✓ Backups creados (.shimbackup)")
        print()
        print("PRÓXIMO: Actualizar canonical.py para usar execute_dict")
    else:
        print("Todos los agentes ya tenían shim")

if __name__ == "__main__":
    main()
