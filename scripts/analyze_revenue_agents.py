import json
import os
from pathlib import Path

class RevenueAnalyzer:
    def __init__(self, inventory_path):
        self.inventory_path = Path(inventory_path)
        self.load_inventory()
        
        self.revenue_map = {
            "premium_agents": [],
            "free_agents": [], 
            "revenue_critical_routes": [],
            "monetization_opportunities": [],
            "summary": {}
        }
    
    def load_inventory(self):
        """Carga el inventario generado"""
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            self.inventory = json.load(f)
        print(f"📁 Inventario cargado: {self.inventory_path}")
    
    def analyze_agent_monetization(self):
        """Analiza qué agentes pueden generar ingresos"""
        agents = self.inventory.get("agents_analysis", {})
        
        print(f"🔍 Analizando {len(agents)} agentes para monetización...")
        
        for agent_name, agent_data in agents.items():
            score = self._calculate_revenue_score(agent_name, agent_data)
            
            agent_info = {
                "agent": agent_name,
                "file_path": agent_data.get("file_path", ""),
                "revenue_score": score,
                "size_kb": agent_data.get("size_kb", 0),
                "has_class": agent_data.get("has_class", False),
                "has_evaluate_method": agent_data.get("has_evaluate_method", False),
                "has_tests": agent_data.get("has_tests", False)
            }
            
            if score >= 8:
                agent_info.update({
                    "pricing_tier": "enterprise",
                    "estimated_mrr": 500,
                    "priority": "CRITICAL"
                })
                self.revenue_map["premium_agents"].append(agent_info)
            elif score >= 6:
                agent_info.update({
                    "pricing_tier": "professional", 
                    "estimated_mrr": 200,
                    "priority": "HIGH"
                })
                self.revenue_map["premium_agents"].append(agent_info)
            elif score >= 4:
                agent_info.update({
                    "pricing_tier": "starter",
                    "estimated_mrr": 50,
                    "priority": "MEDIUM" 
                })
                self.revenue_map["premium_agents"].append(agent_info)
            else:
                self.revenue_map["free_agents"].append(agent_info)
    
    def _calculate_revenue_score(self, agent_name, agent_data):
        """Calcula score de revenue basado en múltiples factores"""
        score = 0
        
        # Factor 1: Términos clave en el nombre
        premium_keywords = ["credit", "risk", "scoring", "fraud", "compliance", "sentinel", "evaluate", "analyzer"]
        for keyword in premium_keywords:
            if keyword in agent_name.lower():
                score += 2
                break
        
        # Factor 2: Complejidad técnica
        if agent_data.get("has_class", False):
            score += 1
        if agent_data.get("has_evaluate_method", False):
            score += 2
        if agent_data.get("size_kb", 0) > 10:  # Agentes más grandes = más complejos
            score += 1
        
        # Factor 3: Estado de desarrollo
        if agent_data.get("has_tests", False):
            score += 2
        
        # Factor 4: Ubicación del archivo (agents/ vs otros)
        file_path = agent_data.get("file_path", "").lower()
        if "agent" in file_path or "core" in file_path or "engine" in file_path:
            score += 1
        
        return min(score, 10)
    
    def analyze_revenue_routes(self):
        """Identifica rutas que pueden generar ingresos"""
        flask_routes = self.inventory.get("backend_analysis", {}).get("flask", {})
        fastapi_routes = self.inventory.get("backend_analysis", {}).get("fastapi", {})
        
        revenue_keywords = ["payment", "billing", "subscription", "premium", "upgrade", "checkout", "invoice", "plan"]
        
        # Analizar rutas Flask
        for file_path, route_data in flask_routes.items():
            for route in route_data.get("routes", []):
                route_str = str(route).lower()
                if any(keyword in route_str for keyword in revenue_keywords):
                    self.revenue_map["revenue_critical_routes"].append({
                        "framework": "flask",
                        "file_path": file_path,
                        "route": route
                    })
        
        # Analizar rutas FastAPI
        for file_path, route_data in fastapi_routes.items():
            for route in route_data.get("routes", []):
                route_str = str(route).lower()
                if any(keyword in route_str for keyword in revenue_keywords):
                    self.revenue_map["revenue_critical_routes"].append({
                        "framework": "fastapi", 
                        "file_path": file_path,
                        "route": route
                    })
    
    def generate_revenue_report(self):
        """Genera reporte de revenue completo"""
        print("💰 Analizando potencial de revenue...")
        
        self.analyze_agent_monetization()
        self.analyze_revenue_routes()
        
        # Calcular métricas resumen
        total_estimated_mrr = sum(
            agent.get("estimated_mrr", 0) 
            for agent in self.revenue_map["premium_agents"]
        )
        
        premium_count = len(self.revenue_map["premium_agents"])
        free_count = len(self.revenue_map["free_agents"])
        total_agents = premium_count + free_count
        
        self.revenue_map["summary"] = {
            "total_premium_agents": premium_count,
            "total_free_agents": free_count,
            "estimated_total_mrr": total_estimated_mrr,
            "monetization_coverage": f"{(premium_count / total_agents * 100):.1f}%" if total_agents > 0 else "0%",
            "premium_agents_by_tier": {
                "enterprise": len([a for a in self.revenue_map["premium_agents"] if a.get("pricing_tier") == "enterprise"]),
                "professional": len([a for a in self.revenue_map["premium_agents"] if a.get("pricing_tier") == "professional"]),
                "starter": len([a for a in self.revenue_map["premium_agents"] if a.get("pricing_tier") == "starter"])
            }
        }
        
        output_file = Path(__file__).parent / "out" / "revenue_analysis.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.revenue_map, f, indent=2, ensure_ascii=False)
            
        print(f"✅ ANÁLISIS DE REVENUE GENERADO: {output_file}")
        print(f"📊 RESULTADOS REVENUE:")
        print(f"   - Agentes Premium: {premium_count}")
        print(f"   - Agentes Free: {free_count}")
        print(f"   - MRR Estimado: ${total_estimated_mrr}/mes")
        print(f"   - Cobertura Monetización: {self.revenue_map['summary']['monetization_coverage']}")
        
        # Mostrar agentes premium encontrados
        if premium_count > 0:
            print(f"   - Agentes CRÍTICOS encontrados:")
            for agent in self.revenue_map["premium_agents"]:
                if agent["priority"] == "CRITICAL":
                    print(f"     * {agent['agent']} (${agent['estimated_mrr']}/mes)")
        
        return self.revenue_map

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    import sys
    
    # Ruta automática al inventario
    inventory_path = Path(__file__).parent / "out" / "inventory_analysis.json"
    
    if not inventory_path.exists():
        print(f"❌ No se encuentra el archivo de inventario: {inventory_path}")
        print("   Primero ejecuta: python generate_inventory.py")
        sys.exit(1)
    
    analyzer = RevenueAnalyzer(inventory_path)
    report = analyzer.generate_revenue_report()
    print("🎉 Análisis de revenue completado!")
