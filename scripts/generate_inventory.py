import os
import json
import ast
from pathlib import Path
from datetime import datetime

class CodebaseInventory:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.inventory = {
            "summary": {},
            "backend_analysis": {"flask": {}, "fastapi": {}},
            "agents_analysis": {},
            "revenue_critical_paths": [],
            "code_debt_analysis": {}
        }
    
    def analyze_repo_structure(self):
        """Analiza la estructura completa del repositorio"""
        total_size = 0
        file_count = 0
        
        print("🔍 Escaneando estructura del repositorio...")
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size
                
                # Analizar por tipo de archivo
                ext = file_path.suffix.lower()
                if ext in ['.py', '.js', '.ts', '.json', '.md', '.html', '.css', '.sql']:
                    self._analyze_file_content(file_path)
        
        self.inventory["summary"] = {
            "total_size_gb": round(total_size / (1024**3), 2),
            "file_count": file_count,
            "analysis_timestamp": str(datetime.now())
        }
        print(f"📊 Analizados {file_count} archivos, {round(total_size / (1024**3), 2)} GB")
    
    def _analyze_file_content(self, file_path):
        """Analiza contenido de archivos críticos"""
        try:
            relative_path = str(file_path.relative_to(self.repo_path))
            
            if file_path.suffix.lower() == '.py':
                self._analyze_python_file(file_path, relative_path)
            elif file_path.name.lower() == 'package.json':
                self._analyze_package_json(file_path, relative_path)
            elif file_path.name.lower() in ['app.py', 'main.py', 'server.py', 'application.py']:
                self._identify_backend_routes(file_path, relative_path)
            elif 'agent' in file_path.stem.lower():
                self._analyze_agent_file(file_path, relative_path)
                
        except Exception as e:
            pass  # Ignorar errores en archivos problemáticos
    
    def _analyze_python_file(self, file_path, relative_path):
        """Análisis específico para archivos Python"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detectar si es agente
            if 'agent' in file_path.stem.lower() or 'Agent' in content or 'class Agent' in content:
                self._analyze_agent(file_path, relative_path, content)
            
            # Detectar Flask
            if '@app.route' in content or 'from flask' in content or 'import flask' in content:
                if relative_path not in self.inventory["backend_analysis"]["flask"]:
                    self.inventory["backend_analysis"]["flask"][relative_path] = {
                        "routes": self._extract_flask_routes(content),
                        "size_kb": round(file_path.stat().st_size / 1024, 2)
                    }
            
            # Detectar FastAPI
            if 'FastAPI' in content or 'from fastapi' in content or '@app.get' in content or '@app.post' in content:
                if relative_path not in self.inventory["backend_analysis"]["fastapi"]:
                    self.inventory["backend_analysis"]["fastapi"][relative_path] = {
                        "routes": self._extract_fastapi_routes(content),
                        "size_kb": round(file_path.stat().st_size / 1024, 2)
                    }
                    
        except Exception as e:
            pass
    
    def _analyze_agent(self, file_path, relative_path, content):
        """Analiza un archivo de agente"""
        agent_name = file_path.stem
        self.inventory["agents_analysis"][agent_name] = {
            "file_path": relative_path,
            "size_kb": round(file_path.stat().st_size / 1024, 2),
            "has_class": 'class ' in content,
            "has_evaluate_method": 'def evaluate' in content or 'def run' in content,
            "has_tests": 'test' in file_path.parent.name.lower() or 'test_' in file_path.name.lower(),
            "lines_of_code": len(content.splitlines())
        }
    
    def _extract_flask_routes(self, content):
        """Extrae rutas Flask del contenido"""
        routes = []
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if '@app.route' in line:
                route_info = {"decorator": line.strip()}
                if i + 1 < len(lines):
                    route_info["function"] = lines[i + 1].strip()
                routes.append(route_info)
        return routes
    
    def _extract_fastapi_routes(self, content):
        """Extrae rutas FastAPI del contenido"""
        routes = []
        lines = content.splitlines()
        for line in lines:
            if any(dec in line for dec in ['@app.get', '@app.post', '@app.put', '@app.delete', '@app.patch']):
                routes.append({"decorator": line.strip()})
        return routes
    
    def _analyze_package_json(self, file_path, relative_path):
        """Analiza package.json para dependencias"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            self.inventory["dependencies"] = {
                "dependencies": package_data.get("dependencies", {}),
                "devDependencies": package_data.get("devDependencies", {}),
                "scripts": package_data.get("scripts", {})
            }
        except Exception as e:
            pass
    
    def generate_report(self):
        """Genera reporte final"""
        output_file = self.repo_path / "scripts" / "out" / "inventory_analysis.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calcular métricas resumen
        flask_routes_count = sum(len(data["routes"]) for data in self.inventory["backend_analysis"]["flask"].values())
        fastapi_routes_count = sum(len(data["routes"]) for data in self.inventory["backend_analysis"]["fastapi"].values())
        
        self.inventory["summary"]["flask_routes_count"] = flask_routes_count
        self.inventory["summary"]["fastapi_routes_count"] = fastapi_routes_count
        self.inventory["summary"]["agents_count"] = len(self.inventory["agents_analysis"])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.inventory, f, indent=2, ensure_ascii=False)
        
        print(f"✅ INVENTARIO GENERADO: {output_file}")
        print(f"📊 RESULTADOS:")
        print(f"   - Archivos totales: {self.inventory['summary']['file_count']}")
        print(f"   - Tamaño total: {self.inventory['summary']['total_size_gb']} GB")
        print(f"   - Rutas Flask: {flask_routes_count}")
        print(f"   - Rutas FastAPI: {fastapi_routes_count}") 
        print(f"   - Agentes identificados: {self.inventory['summary']['agents_count']}")
        
        return self.inventory

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    import sys
    
    # Usar el directorio padre del script como repositorio
    repo_path = Path(__file__).parent.parent
    
    print(f"🔍 Analizando repositorio: {repo_path}")
    inventory = CodebaseInventory(repo_path)
    inventory.analyze_repo_structure()
    report = inventory.generate_report()
    print("🎉 Análisis de inventario completado!")
