#!/usr/bin/env python3
"""
Script maestro para corregir TODOS los coordinators
Nadakki AI Suite - Corrección masiva de imports
"""
import os
import re
from pathlib import Path

def get_class_name_from_file(file_path):
    """Extrae el nombre real de la clase desde un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Buscar patrón: class NombreClase:
            match = re.search(r'^class\s+(\w+):', content, re.MULTILINE)
            if match:
                return match.group(1)
    except:
        pass
    return None

def fix_coordinator(coordinator_path, ecosystem_path):
    """Corrige un coordinator específico"""
    print(f"🔧 Corrigiendo {coordinator_path}...")
    
    try:
        # Leer coordinator actual
        with open(coordinator_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar todos los agentes en el ecosistema
        ecosystem_dir = Path(ecosystem_path)
        agents = []
        
        for py_file in ecosystem_dir.glob("*.py"):
            if py_file.name.startswith(('__init__', 'coordinator')):
                continue
                
            agent_name = py_file.stem
            class_name = get_class_name_from_file(py_file)
            
            if class_name:
                agents.append({
                    'file': agent_name,
                    'class': class_name
                })
        
        # Crear nuevos imports
        new_imports = []
        for agent in agents:
            new_imports.append(f"from .{agent['file']} import {agent['class']}")
        
        # Reemplazar sección de imports
        # Buscar líneas que empiecen con "from ." en el coordinator
        lines = content.split('\n')
        new_lines = []
        skip_imports = False
        imports_replaced = False
        
        for line in lines:
            if line.strip().startswith('# Imports de agentes') or line.strip().startswith('from .'):
                if not imports_replaced:
                    new_lines.append('# Imports de agentes - CORREGIDOS AUTOMÁTICAMENTE')
                    new_lines.extend(new_imports)
                    new_lines.append('')
                    imports_replaced = True
                skip_imports = True
                continue
            elif skip_imports and (line.strip() == '' or line.strip().startswith('from .')):
                continue
            else:
                skip_imports = False
                
            # Reemplazar referencias a clases en el código
            updated_line = line
            for agent in agents:
                # Buscar patrones comunes de nombres incorrectos
                incorrect_patterns = [
                    f"{agent['file'].title()}Analyzer",
                    f"{agent['file'].title()}Engine", 
                    f"{agent['file'].title()}System",
                    f"{agent['file'].title()}Optimizer",
                    f"{agent['file'].title()}Monitor",
                    f"{agent['file'].title()}Core",
                    f"{agent['file'].title()}Validator",
                    f"{''.join(word.capitalize() for word in agent['file'].split('_'))}Engine",
                    f"{''.join(word.capitalize() for word in agent['file'].split('_'))}System",
                    f"{''.join(word.capitalize() for word in agent['file'].split('_'))}Analyzer"
                ]
                
                for incorrect in incorrect_patterns:
                    updated_line = updated_line.replace(incorrect, agent['class'])
            
            new_lines.append(updated_line)
        
        # Escribir archivo corregido
        with open(coordinator_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ {coordinator_path} corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo {coordinator_path}: {e}")
        return False

def main():
    """Función principal - corrige todos los coordinators"""
    print("🚀 INICIANDO CORRECCIÓN MASIVA DE COORDINATORS")
    print("=" * 60)
    
    base_path = Path("agents")
    ecosystems = [
        'originacion', 'decision', 'vigilancia', 'recuperacion',
        'compliance', 'operacional', 'experiencia', 'inteligencia',
        'fortaleza', 'legal', 'marketing', 'contabilidad', 
        'presupuesto', 'rrhh', 'ventascrm', 'logistica', 
        'investigacion', 'educacion', 'regtech'
    ]
    
    corrected = 0
    failed = 0
    
    for ecosystem in ecosystems:
        ecosystem_path = base_path / ecosystem
        coordinator_path = ecosystem_path / f"{ecosystem}_coordinator.py"
        
        if coordinator_path.exists():
            if fix_coordinator(coordinator_path, ecosystem_path):
                corrected += 1
            else:
                failed += 1
        else:
            print(f"⚠️ Coordinator no encontrado: {coordinator_path}")
    
    print("=" * 60)
    print(f"📊 RESUMEN:")
    print(f"✅ Coordinators corregidos: {corrected}")
    print(f"❌ Fallos: {failed}")
    print(f"🎯 Ejecuta: python -m agents.registry")
    print("=" * 60)

if __name__ == "__main__":
    main()