"""
Script temporal de validación de agentes
"""
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar y contar agentes
import glob

marketing_path = os.path.dirname(__file__)
agent_files = glob.glob(os.path.join(marketing_path, "*ia.py"))

print(f"\n{'='*60}")
print(f"MARKETING CORE - AGENTES DETECTADOS")
print(f"{'='*60}\n")

valid_agents = []
import_errors = []

for agent_file in sorted(agent_files):
    agent_name = os.path.basename(agent_file)[:-3]  # Remove .py
    
    try:
        # Intentar importar
        module = __import__(f"agents.marketing.{agent_name}", fromlist=[agent_name])
        
        # Buscar clases que terminen en IA
        agent_classes = [name for name in dir(module) if name.endswith('IA') and not name.startswith('_')]
        
        if agent_classes:
            valid_agents.append((agent_name, agent_classes[0]))
            print(f"✓ {agent_name:35} → {agent_classes[0]}")
        else:
            print(f"⚠ {agent_name:35} → Sin clase *IA")
            
    except Exception as e:
        import_errors.append((agent_name, str(e)))
        print(f"✗ {agent_name:35} → Error: {str(e)[:40]}")

print(f"\n{'='*60}")
print(f"RESUMEN:")
print(f"  • Total archivos: {len(agent_files)}")
print(f"  • Agentes válidos: {len(valid_agents)}")
print(f"  • Errores de import: {len(import_errors)}")
print(f"{'='*60}\n")

if import_errors:
    print("\nERRORES DETALLADOS:")
    for name, error in import_errors:
        print(f"\n{name}:")
        print(f"  {error}")
