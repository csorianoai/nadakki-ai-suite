import os
from pathlib import Path

# Renombrar coordinators problemáticos temporalmente
coordinators_to_disable = [
    'decision_coordinator.py',
    'vigilancia_coordinator.py', 
    'recuperacion_coordinator.py',
    'compliance_coordinator.py'
]

base_path = Path('agents')
ecosystems = ['decision', 'vigilancia', 'recuperacion', 'compliance']

for ecosystem in ecosystems:
    coordinator_path = base_path / ecosystem / f'{ecosystem}_coordinator.py'
    backup_path = base_path / ecosystem / f'{ecosystem}_coordinator.py.backup'
    
    if coordinator_path.exists():
        coordinator_path.rename(backup_path)
        print(f"✅ Disabled {coordinator_path}")

print("🔧 Ejecuta: python -m agents.registry")