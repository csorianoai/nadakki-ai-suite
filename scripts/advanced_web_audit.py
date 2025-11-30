import ast
import os
from pathlib import Path
import json
import codecs

def detect_framework(file_path):
    """Detectar framework web usado en el archivo"""
    try:
        # Manejar BOM (Byte Order Mark)
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Detectar y remover BOM
        if raw_content.startswith(codecs.BOM_UTF8):
            content = raw_content.decode('utf-8-sig')
        else:
            content = raw_content.decode('utf-8')
        
        framework_indicators = {
            'Flask': ['from flask', 'import flask', 'Flask(', 'flask.Flask('],
            'FastAPI': ['from fastapi', 'import fastapi', 'FastAPI(', 'fastapi.FastAPI('],
            'Django': ['from django', 'import django', 'Django'],
            'Blueprint': ['Blueprint(', 'flask.Blueprint('],
            'APIRouter': ['APIRouter(', 'fastapi.APIRouter(']
        }
        
        detected = []
        for framework, indicators in framework_indicators.items():
            if any(indicator in content.lower() for indicator in indicators):
                detected.append(framework)
        
        return detected, content
        
    except Exception as e:
        return [], ""

def find_web_frameworks():
    """Buscar frameworks web en todo el proyecto"""
    print("🔍 BUSCANDO FRAMEWORKS WEB...")
    
    framework_files = {}
    excluded_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}
    
    for py_file in Path('.').rglob('*.py'):
        # Excluir directorios de entorno virtual y cache
        if any(excluded in str(py_file) for excluded in excluded_dirs):
            continue
            
        frameworks, content = detect_framework(py_file)
        if frameworks:
            framework_files[str(py_file)] = {
                'frameworks': frameworks,
                'size': py_file.stat().st_size
            }
    
    return framework_files

def extract_routes_advanced():
    """Extraer rutas de forma avanzada (maneja BOM y múltiples frameworks)"""
    print("🕵️  EXTRAYENDO RUTAS CON MANEJO DE BOM...")
    
    all_routes = []
    excluded_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}
    
    for py_file in Path('.').rglob('*.py'):
        # Excluir directorios no relevantes
        if any(excluded in str(py_file) for excluded in excluded_dirs):
            continue
            
        try:
            # Manejar BOM
            with open(py_file, 'rb') as f:
                raw_content = f.read()
            
            if raw_content.startswith(codecs.BOM_UTF8):
                content = raw_content.decode('utf-8-sig')
            else:
                content = raw_content.decode('utf-8')
            
            # Buscar patrones de rutas manualmente (más robusto que AST con BOM)
            routes_in_file = extract_routes_manual(content, str(py_file))
            all_routes.extend(routes_in_file)
            
        except Exception as e:
            print(f"   ⚠️  Error en {py_file}: {e}")
            continue
    
    return all_routes

def extract_routes_manual(content, file_path):
    """Extraer rutas manualmente buscando patrones"""
    routes = []
    
    # Patrones para Flask
    flask_patterns = [
        (".route('/", "Flask"),
        ('.route("/', "Flask"),
        ("@app.route('/", "Flask"),
        ('@app.route("/', "Flask"),
        ("@bp.route('/", "Flask"),
        ('@bp.route("/', "Flask")
    ]
    
    # Patrones para FastAPI
    fastapi_patterns = [
        (".get('/", "FastAPI"),
        ('.get("/', "FastAPI"),
        (".post('/", "FastAPI"),
        ('.post("/', "FastAPI"),
        (".put('/", "FastAPI"),
        ('.put("/', "FastAPI"),
        (".delete('/", "FastAPI"),
        ('.delete("/', "FastAPI")
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # Buscar patrones de Flask
        for pattern, framework in flask_patterns:
            if pattern in line_clean:
                # Extraer la ruta
                start_idx = line_clean.find(pattern) + len(pattern) - 1
                end_idx = line_clean.find("'", start_idx + 1)
                if end_idx == -1:
                    end_idx = line_clean.find('"', start_idx + 1)
                
                if end_idx != -1:
                    route_path = line_clean[start_idx:end_idx]
                    
                    # Buscar nombre de función (línea siguiente)
                    func_name = "unknown"
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('def '):
                            func_name = next_line[4:next_line.find('(')]
                    
                    routes.append({
                        'route': route_path,
                        'function': func_name,
                        'file': file_path,
                        'framework': framework,
                        'methods': ['GET']  # default para Flask
                    })
        
        # Buscar patrones de FastAPI
        for pattern, framework in fastapi_patterns:
            if pattern in line_clean:
                # Extraer la ruta
                start_idx = line_clean.find(pattern) + len(pattern) - 1
                end_idx = line_clean.find("'", start_idx + 1)
                if end_idx == -1:
                    end_idx = line_clean.find('"', start_idx + 1)
                
                if end_idx != -1:
                    route_path = line_clean[start_idx:end_idx]
                    http_method = pattern.split('.')[1].upper()  # get -> GET, post -> POST
                    
                    # Buscar nombre de función
                    func_name = "unknown"
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('def '):
                            func_name = next_line[4:next_line.find('(')]
                    
                    routes.append({
                        'route': route_path,
                        'function': func_name,
                        'file': file_path,
                        'framework': framework,
                        'methods': [http_method]
                    })
    
    return routes

def comprehensive_web_audit():
    """Auditoría web completa"""
    print("🎯 INICIANDO AUDITORÍA WEB COMPREHENSIVA...")
    print("===========================================")
    
    # 1. Detectar frameworks
    framework_files = find_web_frameworks()
    
    print(f"📊 FRAMEWORKS DETECTADOS: {len(framework_files)} archivos")
    for file_path, info in list(framework_files.items())[:10]:  # Mostrar primeros 10
        print(f"   📍 {file_path} -> {info['frameworks']}")
    
    # 2. Extraer rutas
    all_routes = extract_routes_advanced()
    
    print(f"\n🛣️  RUTAS ENCONTRADAS: {len(all_routes)}")
    for i, route in enumerate(all_routes, 1):
        methods = ', '.join(route['methods'])
        print(f"   {i:2d}. {route['framework']}: {route['route']} -> {route['function']} [{methods}]")
    
    # 3. Guardar resultados
    Path("out").mkdir(exist_ok=True)
    
    results = {
        'frameworks_found': framework_files,
        'routes_found': all_routes,
        'summary': {
            'total_routes': len(all_routes),
            'framework_files': len(framework_files),
            'frameworks': list(set([fw for file_info in framework_files.values() for fw in file_info['frameworks']]))
        }
    }
    
    with open("out/web_framework_audit.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: out/web_framework_audit.json")
    
    # 4. Mostrar resumen ejecutivo
    print(f"\n📈 RESUMEN EJECUTIVO:")
    print(f"   • Archivos con frameworks: {len(framework_files)}")
    print(f"   • Rutas totales: {len(all_routes)}")
    print(f"   • Frameworks detectados: {results['summary']['frameworks']}")
    
    return results

if __name__ == "__main__":
    results = comprehensive_web_audit()
    
    if results['summary']['total_routes'] > 0:
        print(f"\n🎯 LISTO PARA PHASE 1: Consolidar {len(results['routes_found'])} rutas")
    else:
        print(f"\n🔍 ANÁLISIS: No se encontraron rutas web tradicionales")
        print("   Posibles escenarios:")
        print("   1. Usas un framework diferente (FastAPI, Django, etc.)")
        print("   2. La aplicación está en archivos no analizados")
        print("   3. Arquitectura basada en agentes sin rutas web tradicionales")
