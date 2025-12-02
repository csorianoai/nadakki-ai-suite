# scripts/advanced_marketing_audit.py
import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar src al path para importar AgentFactory
sys.path.append('src')

try:
    from Core.agent_factory import get_agent_factory
except ImportError as e:
    print(f"❌ No se puede importar AgentFactory: {e}")
    sys.exit(1)

def analyze_marketing_agents():
    """Analiza agentes de marketing usando AgentFactory real"""
    
    print("🎯 AUDITORÍA AVANZADA DE MARKETING CON AGENTFACTORY")
    print("=" * 60)
    
    # Obtener AgentFactory
    factory = get_agent_factory()
    status = factory.get_agent_status()
    
    print(f"📊 ESTADO GENERAL:")
    print(f"   • Agentes en registry: {status['total_registry']}")
    print(f"   • Agentes cargados: {status['loaded_agents']}")
    print(f"   • Tasa de éxito: {status['success_rate']}")
    
    # Obtener agentes de marketing
    marketing_agents = factory.get_ecosystem_agents('marketing')
    all_marketing_files = list(Path('agents/marketing').glob('*.py'))
    
    print(f"\n🎪 AGENTES DE MARKETING:")
    print(f"   • En directorio: {len(all_marketing_files)} archivos")
    print(f"   • Cargados en Factory: {len(marketing_agents)} agentes")
    
    # Generar reporte detallado
    report_lines = []
    report_lines.append("# 🎯 AUDITORÍA MARKETING CON AGENTFACTORY")
    report_lines.append(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## 📊 RESUMEN")
    report_lines.append(f"- Total archivos: {len(all_marketing_files)}")
    report_lines.append(f"- Agentes cargados: {len(marketing_agents)}")
    report_lines.append(f"- Tasa de carga: {status['success_rate']}")
    report_lines.append("")
    report_lines.append("## 🔍 DETALLE POR AGENTE")
    report_lines.append("")
    report_lines.append("| Agente | Estado | Ecosistema | Líneas |")
    report_lines.append("|--------|--------|------------|--------|")
    
    # Analizar cada archivo en marketing
    for agent_file in all_marketing_files:
        if agent_file.name == '__init__.py':
            continue
            
        agent_name = agent_file.stem
        agent_data = marketing_agents.get(agent_name, {})
        
        # Contar líneas
        with open(agent_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
        
        # Determinar estado
        if agent_data:
            status_icon = "🟢 VINCULADO"
            ecosystem = agent_data.get('ecosystem', 'marketing')
        else:
            status_icon = "🟡 NO VINCULADO"
            ecosystem = 'marketing'
        
        report_lines.append(f"| {agent_name} | {status_icon} | {ecosystem} | {line_count} |")
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = f"reports/marketing_agentfactory_audit_{timestamp}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ Reporte guardado: {report_path}")
    
    # Mostrar resumen en consola
    print(f"\n📋 RESUMEN FINAL:")
    linked_count = len(marketing_agents)
    total_count = len([f for f in all_marketing_files if f.name != '__init__.py'])
    
    print(f"   🟢 VINCULADOS: {linked_count}/{total_count} ({(linked_count/total_count*100):.1f}%)")
    print(f"   🟡 NO VINCULADOS: {total_count - linked_count}/{total_count}")
    
    # Mostrar algunos agentes vinculados
    if marketing_agents:
        print(f"\n🎪 EJEMPLOS DE AGENTES VINCULADOS:")
        for agent_name in list(marketing_agents.keys())[:5]:
            print(f"   ✅ {agent_name}")
    
    return len(marketing_agents)

if __name__ == "__main__":
    analyze_marketing_agents()
