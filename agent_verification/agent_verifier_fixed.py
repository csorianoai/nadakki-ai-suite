import json, ast, os, re, sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_agent_file(file_path):
    """Analiza un archivo Python y determina su categoría"""
    results = {
        "file_path": str(file_path),
        "filename": os.path.basename(file_path),
        "size_bytes": os.path.getsize(file_path),
        "lines": 0,
        "categories": [],
        "score": 0,
        "issues": [],
        "recommendation": "",
        "structure_analysis": {}
    }
    
    # Leer contenido
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            try:
                with open(file_path, 'r', encoding='cp1252') as f:
                    content = f.read()
            except:
                return {**results, "error": "Cannot read file"}
    
    results["lines"] = len(content.splitlines())
    
    # Análisis de patrones básicos
    patterns = {
        "has_class_def": bool(re.search(r'^class\s+\w+', content, re.MULTILINE)),
        "has_def_execute": bool(re.search(r'def\s+execute\s*\(', content)),
        "has_def_run": bool(re.search(r'def\s+run\s*\(', content)),
        "has_async_def": bool(re.search(r'async\s+def', content)),
        "has_init_method": bool(re.search(r'def\s+__init__\s*\(', content)),
        "has_imports": bool(re.search(r'^import\s+|^from\s+', content, re.MULTILINE)),
        "has_openai_import": bool(re.search(r'import\s+openai|from\s+openai', content)),
        "has_langchain_import": bool(re.search(r'import\s+langchain|from\s+langchain', content)),
        "has_agent_string": bool(re.search(r'agent|Agent', content)),
        "has_api_calls": bool(re.search(r'requests\.|httpx\.|aiohttp\.', content)),
        "has_try_except": bool(re.search(r'try:|except\s+', content)),
        "has_docstring": bool(re.search(r'\"\"\"|\'\'\'', content)),
        "has_logging": bool(re.search(r'import\s+logging|logger\.|log\.', content)),
        "has_config": bool(re.search(r'config|Config|settings|Settings', content)),
        "lines_of_code": len([l for l in content.splitlines() if l.strip() and not l.strip().startswith('#')])
    }
    
    results["structure_analysis"] = patterns
    
    # Análisis AST más detallado
    try:
        tree = ast.parse(content)
        
        # Contar elementos
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        async_function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)])
        method_count = 0
        execute_methods = []
        run_methods = []
        
        # Analizar clases
        classes_info = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": [],
                    "has_init": False,
                    "has_execute": False,
                    "has_run": False,
                    "method_count": 0
                }
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = item.name
                        class_info["methods"].append(method_name)
                        class_info["method_count"] += 1
                        method_count += 1
                        
                        if method_name == "__init__":
                            class_info["has_init"] = True
                        if method_name == "execute":
                            class_info["has_execute"] = True
                            execute_methods.append(f"{node.name}.{method_name}")
                        if method_name == "run":
                            class_info["has_run"] = True
                            run_methods.append(f"{node.name}.{method_name}")
                
                classes_info.append(class_info)
        
        # Funciones a nivel de módulo
        module_functions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                module_functions.append(node.name)
        
        results["ast_analysis"] = {
            "class_count": class_count,
            "function_count": function_count,
            "async_function_count": async_function_count,
            "method_count": method_count,
            "classes": classes_info,
            "module_functions": module_functions,
            "execute_methods": execute_methods,
            "run_methods": run_methods,
            "has_any_execute": len(execute_methods) > 0 or len(run_methods) > 0
        }
        
    except SyntaxError as e:
        results["ast_analysis"] = {"error": f"Syntax error: {str(e)}"}
        results["issues"].append("syntax_error")
    
    # CALIFICACIÓN Y CATEGORIZACIÓN
    score = 0
    categories = []
    
    # Criterio 1: Estructura básica
    if patterns["has_class_def"]:
        score += 10
        categories.append("has_class")
    
    if patterns["has_def_execute"] or patterns["has_def_run"]:
        score += 25
        categories.append("has_execute_method")
    
    if patterns["has_init_method"]:
        score += 10
        categories.append("has_constructor")
    
    # Criterio 2: Complejidad y tamaño
    if results["lines"] > 100:
        score += 15
        categories.append("substantial_size")
    elif results["lines"] > 50:
        score += 10
        categories.append("moderate_size")
    elif results["lines"] > 20:
        score += 5
        categories.append("small_size")
    
    # Criterio 3: Importaciones relevantes
    if patterns["has_openai_import"]:
        score += 15
        categories.append("uses_openai")
    
    if patterns["has_langchain_import"]:
        score += 10
        categories.append("uses_langchain")
    
    # Criterio 4: Características avanzadas
    if patterns["has_async_def"]:
        score += 5
        categories.append("async_capable")
    
    if patterns["has_api_calls"]:
        score += 10
        categories.append("api_integration")
    
    if patterns["has_try_except"]:
        score += 5
        categories.append("error_handling")
    
    if patterns["has_logging"]:
        score += 5
        categories.append("has_logging")
    
    if patterns["has_docstring"]:
        score += 5
        categories.append("documented")
    
    # Criterio 5: Nombre sugerente
    if patterns["has_agent_string"]:
        score += 5
        categories.append("agent_named")
    
    # Máximo score posible: 100
    results["score"] = min(score, 100)
    results["categories"] = categories
    
    # DETERMINAR CATEGORÍA FINAL
    if "has_execute_method" in categories and results["lines"] > 50:
        if score >= 60:
            results["final_category"] = "AGENTE_OPERATIVO"
            results["recommendation"] = "Listo para producción"
        elif score >= 40:
            results["final_category"] = "AGENTE_CONFIGURADO"
            results["recommendation"] = "Necesita validación"
        else:
            results["final_category"] = "AGENTE_BASICO"
            results["recommendation"] = "Requiere desarrollo"
    
    elif "has_class" in categories:
        if results["lines"] > 30:
            results["final_category"] = "ESQUELETO_AGENTE"
            results["recommendation"] = "Implementar métodos de ejecución"
        else:
            results["final_category"] = "CLASE_VACIA"
            results["recommendation"] = "Considerar eliminación"
    
    elif results["lines"] > 10:
        results["final_category"] = "UTILIDAD_SCRIPT"
        results["recommendation"] = "Mantener como utilidad"
    
    else:
        results["final_category"] = "ARCHIVO_MINIMO"
        results["recommendation"] = "Eliminar si no es necesario"
    
    # Verificar si es solo un template/placeholder
    placeholder_indicators = [
        "TODO", "FIXME", "IMPLEMENTAR", "PENDIENTE",
        "pass", "# ...", "# implement", "# add code"
    ]
    
    placeholder_count = sum(1 for indicator in placeholder_indicators if indicator.upper() in content.upper())
    if placeholder_count > 3 and results["lines"] < 30:
        results["final_category"] = "TEMPLATE_PLACEHOLDER"
        results["recommendation"] = "Eliminar (placeholder sin implementar)"
        results["issues"].append("mostly_placeholder_code")
    
    return results

def main():
    agents_root = Path(os.getcwd()) / "agents"
    output_dir = Path(os.getcwd()) / "agent_verification"
    
    all_results = []
    categories_summary = defaultdict(list)
    
    print("ANALIZANDO archivos en:", agents_root)
    
    # Encontrar todos los archivos Python
    python_files = list(agents_root.rglob("*.py"))
    print(f"ENCONTRADOS {len(python_files)} archivos .py")
    
    for i, file_path in enumerate(python_files, 1):
        # Saltar caché y virtualenvs
        if any(x in str(file_path) for x in ['__pycache__', '.git', '.venv', 'venv']):
            continue
        
        rel_path = file_path.relative_to(agents_root)
        print(f"  [{i}/{len(python_files)}] Analizando: {rel_path}")
        analysis = analyze_agent_file(file_path)
        
        # Agregar información adicional
        analysis["relative_path"] = str(rel_path)
        analysis["module"] = analysis["relative_path"].split(os.sep)[0] if os.sep in analysis["relative_path"] else "root"
        
        all_results.append(analysis)
        categories_summary[analysis["final_category"]].append(analysis)
    
    # Generar resumen por categoría
    summary_stats = {}
    for category, files in categories_summary.items():
        summary_stats[category] = {
            "count": len(files),
            "total_lines": sum(f["lines"] for f in files),
            "avg_score": sum(f["score"] for f in files) / len(files) if files else 0,
            "files": [f["relative_path"] for f in files]
        }
    
    # Generar reporte completo
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "agents_root": str(agents_root),
            "total_files_analyzed": len(all_results),
            "analysis_criteria": {
                "AGENTE_OPERATIVO": "Tiene método execute/run, >50 líneas, score ≥ 60",
                "AGENTE_CONFIGURADO": "Tiene clase y estructura, score 40-59",
                "AGENTE_BASICO": "Tiene método execute pero pocas características",
                "ESQUELETO_AGENTE": "Clase sin método execute, >30 líneas",
                "CLASE_VACIA": "Clase pequeña sin funcionalidad",
                "UTILIDAD_SCRIPT": "Funciones sin clases",
                "ARCHIVO_MINIMO": "Código mínimo o vacío",
                "TEMPLATE_PLACEHOLDER": "Template con placeholders"
            }
        },
        "summary_by_category": summary_stats,
        "detailed_analysis": all_results,
        "recommendations": {
            "keep": ["AGENTE_OPERATIVO", "AGENTE_CONFIGURADO", "UTILIDAD_SCRIPT"],
            "review": ["AGENTE_BASICO", "ESQUELETO_AGENTE"],
            "delete": ["CLASE_VACIA", "ARCHIVO_MINIMO", "TEMPLATE_PLACEHOLDER"]
        }
    }
    
    # Guardar reporte completo
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "detailed_verification_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Guardar archivos por categoría
    for category, files in categories_summary.items():
        category_dir = output_dir / "by_category" / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        category_report = {
            "category": category,
            "count": len(files),
            "files": files
        }
        
        category_path = category_dir / f"{category}_files.json"
        with open(category_path, 'w', encoding='utf-8') as f:
            json.dump(category_report, f, indent=2, ensure_ascii=False)
    
    print(f"\nREPORTE guardado en: {report_path}")
    
    # Imprimir resumen en consola
    print("\n" + "="*80)
    print("RESUMEN DE CATEGORIZACION")
    print("="*80)
    
    keep_count = 0
    review_count = 0
    delete_count = 0
    
    for category in sorted(summary_stats.keys()):
        count = summary_stats[category]["count"]
        avg_score = summary_stats[category]["avg_score"]
        
        if category in report["recommendations"]["keep"]:
            color = "GREEN"
            keep_count += count
            symbol = "[KEEP]"
        elif category in report["recommendations"]["review"]:
            color = "YELLOW"
            review_count += count
            symbol = "[REVIEW]"
        else:
            color = "RED"
            delete_count += count
            symbol = "[DELETE]"
        
        print(f"{symbol} {category:<25} {count:>3} archivos (score avg: {avg_score:.1f})")
    
    print("\n" + "="*80)
    print(f"RECOMENDACIONES:")
    print(f"   [KEEP] MANTENER: {keep_count} archivos")
    print(f"   [REVIEW] REVISAR: {review_count} archivos")
    print(f"   [DELETE] ELIMINAR: {delete_count} archivos")
    
    # Generar lista de acciones
    print("\n" + "="*80)
    print("ACCIONES RECOMENDADAS:")
    
    # Para archivos a eliminar
    if delete_count > 0:
        print(f"\nARCHIVOS PARA ELIMINAR (total: {delete_count}):")
        for category in report["recommendations"]["delete"]:
            if category in summary_stats:
                files = summary_stats[category]["files"][:10]  # Mostrar primeros 10
                for file in files:
                    print(f"   [DELETE] {file}")
                if len(summary_stats[category]["files"]) > 10:
                    print(f"   ... y {len(summary_stats[category]['files']) - 10} mas")
    
    # Para archivos a revisar
    if review_count > 0:
        print(f"\nARCHIVOS PARA REVISAR (total: {review_count}):")
        for category in report["recommendations"]["review"]:
            if category in summary_stats:
                print(f"   [REVIEW] {category}: {summary_stats[category]['count']} archivos")
                for file in summary_stats[category]["files"][:5]:
                    print(f"      - {file}")
    
    return len(all_results), keep_count, review_count, delete_count

if __name__ == "__main__":
    total, keep, review, delete = main()
    print(f"\nOK:{total}:{keep}:{review}:{delete}")
