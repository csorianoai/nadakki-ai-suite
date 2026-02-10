import json
from pathlib import Path

audit_file = Path('audit_reports/audit_report_detailed.json')
with open(audit_file, 'r', encoding='utf-8') as f:
    audit = json.load(f)

findings = {
    'generated_at': audit['generated_at'],
    'by_module': {},
    'summary': {
        'total_files': audit['summary']['total_files'],
        'total_modules': audit['summary']['total_modules'],
        'claimed_agents': audit['summary']['total_agents'],
        'active_operativo': 0,
        'configured_standby': 0,
        'template_incomplete': 0,
    }
}

for module_path, agent in audit['agents'].items():
    module_name = agent['module']
    
    if module_name not in findings['by_module']:
        findings['by_module'][module_name] = {
            'total_files': 0,
            'active_operativo': [],
            'configured_standby': [],
            'template_incomplete': []
        }
    
    findings['by_module'][module_name]['total_files'] += 1
    
    has_execute = agent['has_execute']
    status = agent['status']
    lines = agent['lines']
    classes = agent['classes']
    
    if has_execute:
        findings['by_module'][module_name]['active_operativo'].append({
            'file': agent['filename'],
            'path': agent['file_path'],
            'class': agent['primary_class']
        })
        findings['summary']['active_operativo'] += 1
    
    elif status == 'configured' and len(classes) > 0 and lines >= 50:
        findings['by_module'][module_name]['configured_standby'].append({
            'file': agent['filename'],
            'path': agent['file_path'],
            'class': agent['primary_class']
        })
        findings['summary']['configured_standby'] += 1
    
    else:
        findings['by_module'][module_name]['template_incomplete'].append({
            'file': agent['filename'],
            'path': agent['file_path']
        })
        findings['summary']['template_incomplete'] += 1

Path('forensic_analysis').mkdir(exist_ok=True)
with open('forensic_analysis/active_agents_only.json', 'w', encoding='utf-8') as f:
    json.dump(findings, f, ensure_ascii=False, indent=2)

print('\n' + '='*120)
print('NADAKKI AI SUITE — ANÁLISIS FORENSE')
print('='*120)

print(f'\n🔍 RECUENTO REAL:')
print(f'  Total archivos: {findings["summary"]["total_files"]}')
print(f'  ACTIVOS OPERATIVOS (execute): {findings["summary"]["active_operativo"]} ✅')
print(f'  Configured (sin execute):     {findings["summary"]["configured_standby"]} ⚠️')
print(f'  Templates/Incompletos:        {findings["summary"]["template_incomplete"]} 🔴')
print(f'\n📊 DISCREPANCIA:')
print(f'  Audit reportó: {audit["summary"]["total_agents"]} agentes')
print(f'  Realmente activos: {findings["summary"]["active_operativo"]} agentes')
print(f'  DIFERENCIA: {audit["summary"]["total_agents"] - findings["summary"]["active_operativo"]} INFLACIÓN')

print(f'\n🏆 TOP 10 MÓDULOS POR ACTIVOS:')
sorted_mods = sorted(findings['by_module'].items(), key=lambda x: len(x[1]['active_operativo']), reverse=True)
for mod, data in sorted_mods[:10]:
    activos = len(data['active_operativo'])
    total = data['total_files']
    print(f'  {mod:20} {activos:3} activos / {total:3} archivos')

print('\n' + '='*120)
print('✅ active_agents_only.json generado')
print('='*120 + '\n')
