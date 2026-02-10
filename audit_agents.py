#!/usr/bin/env python3
import json, ast
from pathlib import Path
from collections import defaultdict
from datetime import datetime

AGENTS_ROOT = Path.cwd() / 'agents'

def safe_read(fp):
    for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            return fp.read_text(encoding=enc)
        except:
            pass
    return ''

def extract_class_names(content):
    try:
        tree = ast.parse(content)
    except:
        return []
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({
                'name': node.name,
                'methods': methods,
                'has_execute': 'execute' in methods or 'run' in methods,
                'line': node.lineno
            })
    return classes

def extract_functions(content):
    try:
        tree = ast.parse(content)
    except:
        return []
    
    functions = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                'name': node.name,
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'line': node.lineno
            })
    return functions

def extract_imports(content):
    try:
        tree = ast.parse(content)
    except:
        return []
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return imports

def classify_agent(content, classes, functions):
    has_execute_fn = any(f['name'] in ['execute', 'run'] for f in functions)
    has_execute_method = any(c['has_execute'] for c in classes)
    has_class = len(classes) > 0
    lines = content.count('\n') + 1
    
    if has_execute_fn or has_execute_method:
        status = 'active'
    elif has_class and lines > 50:
        status = 'configured'
    else:
        status = 'template'
    
    likely_agent = has_execute_fn or (has_class and lines > 50)
    
    return {
        'status': status,
        'likely_agent': likely_agent,
        'has_execute': has_execute_fn or has_execute_method,
        'has_class': has_class,
        'lines': lines,
        'signals': {
            'top_level_execute': has_execute_fn,
            'class_execute': has_execute_method,
            'class_present': has_class,
            'size': 'large' if lines > 200 else 'medium' if lines > 80 else 'small'
        }
    }

print('\n' + '='*100)
print('NADAKKI AI SUITE — AUDITORÍA FORENSE COMPLETA')
print('='*100)

print('\n[SCAN] Procesando archivos...')
all_agents = {}
by_module = defaultdict(lambda: {'agents': [], 'total_files': 0})
count = 0

for fp in sorted(AGENTS_ROOT.rglob('*.py')):
    if any(x in str(fp) for x in ['__pycache__', '.git', '.venv', '.pytest']):
        continue
    
    content = safe_read(fp)
    if not content.strip():
        continue
    
    rel_path = fp.relative_to(AGENTS_ROOT).as_posix()
    module = rel_path.split('/')[0]
    
    classes = extract_class_names(content)
    functions = extract_functions(content)
    imports = extract_imports(content)
    
    classification = classify_agent(content, classes, functions)
    
    agent_record = {
        'file_path': rel_path,
        'filename': fp.name,
        'module': module,
        'classes': classes,
        'functions': [{'name': f['name'], 'async': f['is_async']} for f in functions],
        'imports_count': len(imports),
        'ai_imports': [imp for imp in imports if any(ai in imp.lower() for ai in ['openai', 'anthropic', 'langchain', 'gpt', 'claude', 'llm', 'embedding', 'vector'])],
        'status': classification['status'],
        'likely_agent': classification['likely_agent'],
        'has_execute': classification['has_execute'],
        'lines': classification['lines'],
        'signals': classification['signals'],
        'primary_class': classes[0]['name'] if classes else None,
        'confidence': 'HIGH' if classification['likely_agent'] else 'MEDIUM' if classification['has_class'] else 'LOW'
    }
    
    all_agents[rel_path] = agent_record
    
    if classification['likely_agent']:
        by_module[module]['agents'].append({
            'file': fp.name,
            'path': rel_path,
            'class': classes[0]['name'] if classes else 'N/A',
            'status': classification['status'],
            'lines': classification['lines']
        })
    
    by_module[module]['total_files'] += 1
    count += 1

print(f'✅ {count} archivos procesados')

print('\n[REPORT] Generando reportes...')

audit_detailed = {
    'generated_at': datetime.now().isoformat(),
    'summary': {
        'total_files': count,
        'total_modules': len(by_module),
        'total_agents': sum(1 for a in all_agents.values() if a['likely_agent']),
        'by_status': {
            'active': sum(1 for a in all_agents.values() if a['status'] == 'active'),
            'configured': sum(1 for a in all_agents.values() if a['status'] == 'configured'),
            'template': sum(1 for a in all_agents.values() if a['status'] == 'template')
        }
    },
    'agents': all_agents
}

audit_summary = {
    'generated_at': datetime.now().isoformat(),
    'modules': {}
}

EXPECTED = {
    'marketing': 44, 'legal': 33, 'contabilidad': 21, 'logistica': 23,
    'presupuesto': 13, 'rrhh': 10, 'educacion': 9, 'investigacion': 9,
    'ventascrm': 9, 'regtech': 8, 'recuperacion': 5, 'originacion': 10, 'otros': 20
}

for module in sorted(by_module.keys()):
    agents_in_mod = by_module[module]['agents']
    expected_count = EXPECTED.get(module, 0)
    real_count = len(agents_in_mod)
    
    audit_summary['modules'][module] = {
        'expected': expected_count,
        'real': real_count,
        'difference': real_count - expected_count,
        'status': 'OK' if real_count >= expected_count else 'MISSING' if real_count > 0 else 'EMPTY',
        'total_files': by_module[module]['total_files'],
        'agents': agents_in_mod
    }

Path('audit_reports').mkdir(exist_ok=True)

with open('audit_reports/audit_report_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(audit_detailed, f, ensure_ascii=False, indent=2)

with open('audit_reports/audit_summary_by_module.json', 'w', encoding='utf-8') as f:
    json.dump(audit_summary, f, ensure_ascii=False, indent=2)

print(f'✅ audit_reports/audit_report_detailed.json')
print(f'✅ audit_reports/audit_summary_by_module.json')

print('\n' + '='*100)
print('RESUMEN EJECUTIVO')
print('='*100)

print(f'\n📊 ESTADÍSTICAS GLOBALES:')
print(f'  Total archivos: {count}')
print(f'  Total módulos: {len(by_module)}')
print(f'  Total agentes: {audit_detailed["summary"]["total_agents"]}')
print(f'\n📈 DISTRIBUCIÓN POR STATUS:')
for status, cnt in audit_detailed["summary"]["by_status"].items():
    print(f'  {status:15} {cnt:3}')

print(f'\n🏆 TOP 10 MÓDULOS POR AGENTES:')
sorted_mods = sorted(audit_summary['modules'].items(), key=lambda x: x[1]['real'], reverse=True)
for mod, data in sorted_mods[:10]:
    icon = '✅' if data['status'] == 'OK' else '⚠️' if data['real'] > 0 else '❌'
    print(f'  {icon} {mod:20} {data["real"]:3} agentes ({data["total_files"]:3} archivos) - {data["status"]}')

print('\n' + '='*100 + '\n')
