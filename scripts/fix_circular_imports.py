# scripts/fix_circular_imports.py
import ast
from pathlib import Path
import re

def analyze_imports(file_path):
    """Analiza imports en un archivo Python"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {file_path}: {e}")
        return []

def find_circular_imports():
    """Encuentra posibles importaciones circulares"""
    agents_dir = Path("agents")
    circular_candidates = []
    
    for ecosystem in agents_dir.iterdir():
        if ecosystem.is_dir():
            coordinator_file = ecosystem / f"{ecosystem.name}_coordinator.py"
            if coordinator_file.exists():
                imports = analyze_imports(coordinator_file)
                
                # Buscar imports que puedan ser circulares
                for imp in imports:
                    if f"agents.{ecosystem.name}" in imp:
                        circular_candidates.append({
                            'file': coordinator_file,
                            'circular_import': imp
                        })
    
    return circular_candidates

def generate_fix_suggestions():
    """Genera sugerencias para corregir importaciones circulares"""
    circular_issues = find_circular_imports()
    
    if not circular_issues:
        print("✅ No se encontraron importaciones circulares evidentes")
        return
    
    print("🔍 POSIBLES IMPORTACIONES CIRCULARES ENCONTRADAS:")
    for issue in circular_issues:
        print(f"   • {issue['file']}")
        print(f"     Importa: {issue['circular_import']}")
        print(f"     Sugerencia: Usar importación diferida o refactorizar")
        print()

if __name__ == "__main__":
    generate_fix_suggestions()
