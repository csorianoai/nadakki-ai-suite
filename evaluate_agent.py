"""
Sistema de Evaluación Individual de Agentes
Estándar 110/100 - Calidad Superior
"""

import sys
import os
import json
import time
import asyncio
import inspect
import traceback
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Colores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class AgentEvaluator:
    """Evaluador individual de agentes con criterios de calidad 110%"""
    
    def __init__(self, agent_id: str, agent_file: str):
        self.agent_id = agent_id
        self.agent_file = agent_file
        self.results = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "scores": {},
            "total_score": 0,
            "grade": "",
            "passed": False,
            "issues": [],
            "recommendations": []
        }
    
    def print_header(self):
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}EVALUACIÓN INDIVIDUAL: {self.agent_id}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
    
    def evaluate_imports(self, content: str) -> int:
        """Evalúa calidad de imports (10 pts)"""
        score = 0
        issues = []
        
        # Verificar imports básicos
        if 'from typing import' in content:
            score += 3
        else:
            issues.append("Falta import de typing")
        
        # Dict, Any presentes
        if 'Dict' in content and 'Any' in content:
            score += 2
        else:
            issues.append("Falta Dict o Any en imports")
        
        # Import de logging
        if 'import logging' in content:
            score += 2
        else:
            issues.append("Falta logging")
        
        # Imports organizados
        lines = content.split('\n')[:30]
        import_lines = [l for l in lines if l.startswith('import ') or l.startswith('from ')]
        if len(import_lines) > 0:
            score += 3
        
        self.results["scores"]["imports"] = score
        self.results["issues"].extend(issues)
        
        return score
    
    def evaluate_structure(self, content: str) -> int:
        """Evalúa estructura del código (15 pts)"""
        score = 0
        
        # Docstring presente
        if '"""' in content[:500]:
            score += 5
        
        # Clase principal definida
        if 'class ' in content and 'IA' in content:
            score += 5
        
        # Método __init__
        if 'def __init__' in content:
            score += 3
        
        # Método execute
        if 'def execute' in content or 'async def execute' in content:
            score += 2
        
        self.results["scores"]["structure"] = score
        return score
    
    def evaluate_error_handling(self, content: str) -> int:
        """Evalúa manejo de errores (15 pts)"""
        score = 0
        
        # Try-except presente
        try_count = content.count('try:')
        if try_count >= 2:
            score += 8
        elif try_count == 1:
            score += 5
        
        # Logging de errores
        if 'logger.error' in content or 'logger.warning' in content:
            score += 4
        
        # Validaciones de input
        if 'raise ValueError' in content or 'raise TypeError' in content:
            score += 3
        
        self.results["scores"]["error_handling"] = score
        return score
    
    def evaluate_typing(self, content: str) -> int:
        """Evalúa type hints (10 pts)"""
        score = 0
        
        # Type hints en funciones
        if '-> ' in content:
            score += 5
        
        # Parámetros tipados
        if ': str' in content or ': Dict' in content or ': int' in content:
            score += 5
        
        self.results["scores"]["typing"] = score
        return score
    
    def evaluate_documentation(self, content: str) -> int:
        """Evalúa documentación (15 pts)"""
        score = 0
        
        # Docstrings en métodos
        docstring_count = content.count('"""')
        if docstring_count >= 6:
            score += 10
        elif docstring_count >= 3:
            score += 7
        elif docstring_count >= 1:
            score += 4
        
        # Comentarios útiles
        comment_lines = [l for l in content.split('\n') if l.strip().startswith('#')]
        if len(comment_lines) >= 10:
            score += 5
        elif len(comment_lines) >= 5:
            score += 3
        
        self.results["scores"]["documentation"] = score
        return score
    
    def evaluate_tenant_handling(self, content: str) -> int:
        """Evalúa manejo de tenant_id (10 pts)"""
        score = 0
        
        # Acepta tenant_id en __init__
        if 'tenant_id' in content:
            score += 5
        
        # Valida tenant_id
        if 'self.tenant_id' in content:
            score += 5
        
        self.results["scores"]["tenant_handling"] = score
        return score
    
    def evaluate_performance(self, content: str) -> int:
        """Evalúa consideraciones de performance (10 pts)"""
        score = 0
        
        # Caché implementado
        if 'cache' in content.lower() or '@lru_cache' in content:
            score += 5
        
        # Async cuando apropiado
        if 'async def' in content:
            score += 3
        
        # Evita operaciones costosas innecesarias
        if 'time.' in content or 'perf_counter' in content:
            score += 2
        
        self.results["scores"]["performance"] = score
        return score
    
    def evaluate_compliance(self, content: str) -> int:
        """Evalúa compliance y seguridad (15 pts)"""
        score = 0
        
        # Compliance mencionado
        if 'compliance' in content.lower():
            score += 5
        
        # Validaciones de seguridad
        if 'validate' in content.lower():
            score += 5
        
        # No hay hardcoded secrets
        if 'password' not in content.lower() and 'api_key' not in content.lower():
            score += 5
        else:
            self.results["issues"].append("Posible secret hardcoded")
        
        self.results["scores"]["compliance"] = score
        return score
    
    async def test_execution(self, agent_class, tenant_id: str) -> int:
        """Prueba ejecución real del agente (20 pts - BONUS)"""
        score = 0
        
        try:
            # Crear instancia
            agent = agent_class(tenant_id=tenant_id)
            score += 5
            
            # Verificar métodos
            if hasattr(agent, 'execute'):
                score += 5
            
            if hasattr(agent, 'execute_dict'):
                score += 5
            
            # Ejecutar con datos dummy
            test_data = {"id": "TEST-001", "data": {"test": "value"}}
            
            try:
                if hasattr(agent, 'execute_dict'):
                    if inspect.iscoroutinefunction(agent.execute_dict):
                        result = await agent.execute_dict(test_data)
                    else:
                        result = agent.execute_dict(test_data)
                    score += 5
                elif hasattr(agent, 'execute'):
                    if inspect.iscoroutinefunction(agent.execute):
                        result = await agent.execute(test_data)
                    else:
                        result = agent.execute(test_data)
                    score += 3
            except Exception as e:
                self.results["issues"].append(f"Ejecución falló: {str(e)}")
        
        except Exception as e:
            self.results["issues"].append(f"No se pudo instanciar: {str(e)}")
        
        self.results["scores"]["execution"] = score
        return score
    
    def calculate_final_score(self):
        """Calcula score final y grade"""
        total = sum(self.results["scores"].values())
        self.results["total_score"] = total
        
        # Grading
        if total >= 100:
            self.results["grade"] = "A+ (EXCELENTE)"
            self.results["passed"] = True
        elif total >= 90:
            self.results["grade"] = "A (MUY BUENO)"
            self.results["passed"] = True
        elif total >= 80:
            self.results["grade"] = "B (BUENO)"
            self.results["passed"] = True
        elif total >= 70:
            self.results["grade"] = "C (ACEPTABLE)"
            self.results["passed"] = False
        else:
            self.results["grade"] = "F (NECESITA TRABAJO)"
            self.results["passed"] = False
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en scores"""
        recs = []
        
        scores = self.results["scores"]
        
        if scores.get("imports", 0) < 8:
            recs.append("Mejorar organización de imports")
        
        if scores.get("error_handling", 0) < 12:
            recs.append("Agregar más manejo de errores robusto")
        
        if scores.get("documentation", 0) < 12:
            recs.append("Mejorar documentación y docstrings")
        
        if scores.get("typing", 0) < 8:
            recs.append("Agregar type hints completos")
        
        if scores.get("execution", 0) < 15:
            recs.append("Verificar que execute() funcione correctamente")
        
        self.results["recommendations"] = recs
    
    def print_results(self):
        """Imprime resultados de forma visual"""
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}RESULTADOS: {self.agent_id}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
        
        # Scores por categoría
        print(f"{Colors.YELLOW}SCORES POR CATEGORÍA:{Colors.RESET}\n")
        
        for category, score in self.results["scores"].items():
            max_scores = {
                "imports": 10,
                "structure": 15,
                "error_handling": 15,
                "typing": 10,
                "documentation": 15,
                "tenant_handling": 10,
                "performance": 10,
                "compliance": 15,
                "execution": 20
            }
            max_score = max_scores.get(category, 10)
            percentage = (score / max_score) * 100
            
            color = Colors.GREEN if percentage >= 80 else Colors.YELLOW if percentage >= 60 else Colors.RED
            bar = "█" * int(percentage / 5)
            
            print(f"  {category.replace('_', ' ').title():.<30} {color}{score}/{max_score}{Colors.RESET} {bar}")
        
        # Score total
        total = self.results["total_score"]
        grade = self.results["grade"]
        
        print(f"\n{Colors.CYAN}{'─' * 70}{Colors.RESET}")
        
        if total >= 100:
            color = Colors.GREEN
            emoji = "🌟"
        elif total >= 90:
            color = Colors.GREEN
            emoji = "✅"
        elif total >= 80:
            color = Colors.YELLOW
            emoji = "⚠️"
        else:
            color = Colors.RED
            emoji = "❌"
        
        print(f"\n{color}{Colors.BOLD}  {emoji} SCORE TOTAL: {total}/120 - {grade}{Colors.RESET}\n")
        
        # Issues
        if self.results["issues"]:
            print(f"{Colors.RED}ISSUES ENCONTRADOS:{Colors.RESET}")
            for issue in self.results["issues"]:
                print(f"  • {issue}")
            print()
        
        # Recomendaciones
        if self.results["recommendations"]:
            print(f"{Colors.YELLOW}RECOMENDACIONES:{Colors.RESET}")
            for rec in self.results["recommendations"]:
                print(f"  → {rec}")
            print()
        
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

async def evaluate_agent(agent_file: str, agent_id: str):
    """Evalúa un agente individual"""
    
    evaluator = AgentEvaluator(agent_id, agent_file)
    evaluator.print_header()
    
    # Leer archivo
    file_path = Path("agents/marketing") / agent_file
    
    if not file_path.exists():
        print(f"{Colors.RED}✗ Archivo no encontrado: {agent_file}{Colors.RESET}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"{Colors.YELLOW}Evaluando código estático...{Colors.RESET}\n")
    
    # Evaluaciones
    evaluator.evaluate_imports(content)
    evaluator.evaluate_structure(content)
    evaluator.evaluate_error_handling(content)
    evaluator.evaluate_typing(content)
    evaluator.evaluate_documentation(content)
    evaluator.evaluate_tenant_handling(content)
    evaluator.evaluate_performance(content)
    evaluator.evaluate_compliance(content)
    
    # Evaluación de ejecución
    print(f"{Colors.YELLOW}Probando ejecución real...{Colors.RESET}\n")
    
    try:
        # Importar agente
        import importlib.util
        spec = importlib.util.spec_from_file_location("agent_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Encontrar clase del agente
        agent_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and name.endswith('IA'):
                agent_class = obj
                break
        
        if agent_class:
            await evaluator.test_execution(agent_class, "eval-test-tenant")
        else:
            evaluator.results["issues"].append("No se encontró clase del agente")
    
    except Exception as e:
        evaluator.results["issues"].append(f"Error importando: {str(e)}")
    
    # Calcular final
    evaluator.calculate_final_score()
    evaluator.generate_recommendations()
    
    # Mostrar resultados
    evaluator.print_results()
    
    # Guardar reporte
    report_file = f"evaluation_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(evaluator.results, f, indent=2, default=str)
    
    print(f"{Colors.CYAN}📄 Reporte guardado: {report_file}{Colors.RESET}\n")
    
    return evaluator.results

async def main():
    import sys
    
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Uso: python evaluate_agent.py <agent_file> <agent_id>{Colors.RESET}")
        print(f"\nEjemplo: python evaluate_agent.py leadscoringia.py lead_scoring")
        return
    
    agent_file = sys.argv[1]
    agent_id = sys.argv[2] if len(sys.argv) > 2 else agent_file.replace('.py', '')
    
    await evaluate_agent(agent_file, agent_id)

if __name__ == "__main__":
    asyncio.run(main())
