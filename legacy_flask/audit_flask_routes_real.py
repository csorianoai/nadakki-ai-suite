import ast
import os
from pathlib import Path
import json

def find_flask_apps():
    """Buscar TODAS las aplicaciones Flask en el proyecto"""
    flask_apps = []
    possible_names = [
        "app.py", "application.py", "main.py", "server.py", 
        "wsgi.py", "run.py", "index.py"
    ]
    
    # Buscar en directorios comunes
    search_dirs = [
        ".", "api", "backend", "src", "app", "apps", 
        "dashboard", "web", "server"
    ]
    
    for search_dir in search_dirs:
        if Path(search_dir).exists():
            for py_file in Path(search_dir).rglob("*.py"):
                if py_file.name in possible_names:
                    flask_apps.append(py_file)
    
    # Si no encontramos con nombres específicos, buscar por contenido
    if not flask_apps:
        for py_file in Path(".").rglob("*.py"):
            if py_file.stat().st_size > 0:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'Flask(' in content or 'flask.Flask(' in content:
                            flask_apps.append(py_file)
                except:
                    continue
    
    return flask_apps

def extract_routes_from_file(file_path):
    """Extraer rutas de un archivo Python"""
    routes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    route_info = extract_route_info(decorator, file_path, node.name)
                    if route_info:
                        routes.append(route_info)
        
        return routes
        
    except Exception as e:
        print(f"   ⚠️  Error analizando {file_path}: {e}")
        return []

def extract_route_info(decorator, file_path, function_name):
    """Extraer información de ruta de decorador"""
    if isinstance(decorator, ast.Call):
        # Caso: @app.route('/path')
        if (isinstance(decorator.func, ast.Attribute) and 
            decorator.func.attr == 'route'):
            
            if decorator.args:
                route_path = decorator.args[0].value if hasattr(decorator.args[0], 'value') else str(decorator.args[0])
                
                # Extraer métodos HTTP si existen
                methods = ['GET']  # default
                for keyword in decorator.keywords:
                    if keyword.arg == 'methods' and isinstance(keyword.value, ast.List):
                        methods = [elt.value for elt in keyword.value.elts]
                
                return {
                    "route": route_path,
                    "function": function_name,
                    "file": str(file_path),
                    "methods": methods
                }
    
    return None

def audit_flask_routes_comprehensive():
    """Auditoría completa de rutas Flask"""
    print("🔍 INICIANDO AUDITORÍA FLASK COMPLETA...")
    
    # Encontrar todas las apps Flask
    flask_apps = find_flask_apps()
    
    if not flask_apps:
        print("❌ No se encontraron aplicaciones Flask")
        return []
    
    print(f"✅ Aplicaciones Flask encontradas: {len(flask_apps)}")
    for app in flask_apps:
        print(f"   📍 {app}")
    
    # Extraer rutas de todas las apps
    all_routes = []
    for app in flask_apps:
        print(f"🔍 Analizando: {app}")
        routes = extract_routes_from_file(app)
        all_routes.extend(routes)
        print(f"   ✅ {len(routes)} rutas encontradas")
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN TOTAL: {len(all_routes)} rutas Flask encontradas")
    
    for i, route in enumerate(all_routes, 1):
        methods = ', '.join(route['methods'])
        print(f"   {i:2d}. {route['route']} -> {route['function']} [{methods}]")
    
    # Guardar resultados
    Path("out").mkdir(exist_ok=True)
    with open("out/flask_routes_comprehensive.json", 'w', encoding='utf-8') as f:
        json.dump(all_routes, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados guardados en: out/flask_routes_comprehensive.json")
    return all_routes

if __name__ == "__main__":
    routes = audit_flask_routes_comprehensive()
    if routes:
        print(f"\n🎯 LISTO PARA PHASE 1: Consolidar {len(routes)} rutas Flask")
    else:
        print("\n⚠️  No se encontraron rutas Flask. Revisar estructura del proyecto.")
