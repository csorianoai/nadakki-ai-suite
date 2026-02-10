#!/usr/bin/env python3
import json, ast
from pathlib import Path
from collections import defaultdict
from datetime import datetime

AGENTS_ROOT = Path.cwd() / 'agents'

def safe_read(fp):
    for enc in ['utf-8','latin-1','cp1252','iso-8859-1']:
        try:
            return fp.read_text(encoding=enc)
        except:
            pass
    return ''

def get_meta(fp, content):
    try:
        tree = ast.parse(content)
    except:
        tree = ast.Module(body=[], type_ignores=[])
    
    lines = content.count('\n') + 1
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({'name': node.name, 'methods': methods, 'has_execute': 'execute' in methods or 'run' in methods})
    
    functions = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    has_exec = 'execute' in functions or 'run' in functions or any(c['has_execute'] for c in classes)
    
    return {
        'filename': fp.name,
        'lines': lines,
        'classes': classes,
        'functions': functions,
        'has_execute': has_exec,
        'has_class': len(classes) > 0,
        'likely_agent': has_exec or (len(classes) > 0 and lines > 50)
    }

print('\n[SCANNING] Leyendo archivos...')
inv = defaultdict(list)
count = 0

for fp in sorted(AGENTS_ROOT.rglob('*.py')):
    if any(x in str(fp) for x in ['__pycache__', '.git', '.venv']):
        continue
    
    content = safe_read(fp)
    if not content.strip():
        continue
    
    rel = fp.relative_to(AGENTS_ROOT).as_posix()
    mod = rel.split('/')[0]
    
    meta = get_meta(fp, content)
    meta['rel_path'] = rel
    
    inv[mod].append(meta)
    count += 1

print(f'[OK] {count} archivos leidos')

reg = {
    'version': '3.0',
    'generated_at': datetime.now().isoformat(),
    'modules': {}
}

total_ag = 0

for mod in sorted(inv.keys()):
    files = inv[mod]
    
    reg['modules'][mod] = {
        'file_count': len(files),
        'agent_count_estimated': sum(1 for f in files if f['likely_agent']),
        'files': {}
    }
    
    for meta in files:
        stem = Path(meta['filename']).stem
        
        reg['modules'][mod]['files'][stem] = {
            'filename': meta['filename'],
            'rel_path': meta['rel_path'],
            'lines': meta['lines'],
            'classes': meta['classes'],
            'functions': meta['functions'],
            'has_execute': meta['has_execute'],
            'likely_agent': meta['likely_agent'],
            'status': 'active' if meta['has_execute'] else 'configured' if meta['has_class'] else 'template',
            'reviewed': False,
            'notes': ''
        }
        
        if meta['likely_agent']:
            total_ag += 1

reg['statistics'] = {
    'total_files': count,
    'total_modules': len(reg['modules']),
    'total_agents_estimated': total_ag,
    'by_status': {
        'active': sum(1 for m in reg['modules'].values() for f in m['files'].values() if f['status'] == 'active'),
        'configured': sum(1 for m in reg['modules'].values() for f in m['files'].values() if f['status'] == 'configured'),
        'template': sum(1 for m in reg['modules'].values() for f in m['files'].values() if f['status'] == 'template')
    }
}

Path('final_inventory').mkdir(exist_ok=True)

with open('final_inventory/agents_registry_final.json', 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False, indent=2)

print(f'[DONE] {count} archivos, {total_ag} agentes, {len(reg["modules"])} modulos')
print(f'[SAVED] final_inventory/agents_registry_final.json')
