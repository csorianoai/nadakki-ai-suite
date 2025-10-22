# filepath: audit_all_updated.py
"""Auditoría completa de agentes actualizados con análisis de mejoras"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Scores ANTERIORES (del audit original)
PREVIOUS_SCORES = {
    "emailautomationia.py": 25,
    "campaignoptimizeria.py": 25,
    "leadscoringia.py": 25,
    "influencermatcheria.py": 25,
    "abtestingimpactia.py": 15,
    "socialpostgeneratoria.py": 15,
}

def analyze_agent_file(filepath: Path) -> Dict:
    """Analiza un archivo de agente y retorna score detallado"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    score = 0
    features = []
    missing = []
    
    # ========== FEATURES CORE (70 puntos) ==========
    
    # Circuit Breaker (15 pts)
    if 'class CircuitBreaker' in content and 'can_execute' in content:
        score += 15
        features.append("✓ Circuit Breaker completo")
    elif 'circuit_breaker' in content.lower():
        score += 8
        features.append("⚠ Circuit Breaker parcial")
        missing.append("Circuit Breaker incompleto")
    else:
        missing.append("Circuit Breaker ausente")
    
    # Cache con TTL (15 pts)
    if 'ttl' in content.lower() and 'cache' in content.lower() and 'OrderedDict' in content:
        score += 15
        features.append("✓ Cache LRU con TTL")
    elif 'cache' in content.lower():
        score += 7
        features.append("⚠ Cache básico")
        missing.append("TTL en cache faltante")
    else:
        missing.append("Cache ausente")
    
    # Compliance (10 pts)
    if 'compliance' in content.lower() or 'Compliance' in content:
        if 'prohibited' in content.lower() or 'forbidden' in content.lower():
            score += 10
            features.append("✓ Compliance engine")
        else:
            score += 5
            features.append("⚠ Compliance básico")
            missing.append("Reglas de compliance incompletas")
    else:
        missing.append("Compliance ausente")
    
    # PII Detection (10 pts)
    if 'PII' in content or 'pii' in content.lower():
        if 'mask' in content.lower() or 'detect' in content.lower():
            score += 10
            features.append("✓ PII detection/masking")
        else:
            score += 5
            features.append("⚠ PII básico")
    else:
        missing.append("PII detection ausente")
    
    # Feature Flags (10 pts)
    if 'class FeatureFlags' in content or 'FeatureFlag' in content:
        score += 10
        features.append("✓ Feature flags")
    else:
        missing.append("Feature flags ausentes")
    
    # Audit Trail (10 pts)
    if 'audit' in content.lower() and 'trace' in content.lower():
        if 'decision_trace' in content.lower():
            score += 10
            features.append("✓ Audit trail completo")
        else:
            score += 5
            features.append("⚠ Audit parcial")
    else:
        missing.append("Audit trail ausente")
    
    # ========== FEATURES ADICIONALES (30 puntos) ==========
    
    # Fallback mode (10 pts)
    if 'fallback' in content.lower() or 'Fallback' in content:
        if '_fallback' in content or 'generate_fallback' in content:
            score += 10
            features.append("✓ Fallback mode")
        else:
            score += 5
            features.append("⚠ Fallback parcial")
    else:
        missing.append("Fallback mode ausente")
    
    # Métricas avanzadas (10 pts)
    if 'get_metrics' in content and 'latency' in content.lower():
        if 'p95' in content.lower() or 'p99' in content.lower() or 'percentile' in content.lower():
            score += 10
            features.append("✓ Métricas avanzadas (p95/p99)")
        else:
            score += 7
            features.append("✓ Métricas básicas")
            missing.append("Percentiles (p95/p99) faltantes")
    else:
        score += 3
        features.append("⚠ Métricas mínimas")
        missing.append("Sistema de métricas incompleto")
    
    # Logging estructurado (5 pts)
    if 'logging' in content and 'logger' in content:
        if 'extra=' in content or 'exc_info=' in content:
            score += 5
            features.append("✓ Logging estructurado")
        else:
            score += 3
            features.append("⚠ Logging básico")
    else:
        missing.append("Logging ausente")
    
    # Async/await (5 pts)
    if 'async def execute' in content or 'async def run' in content:
        score += 5
        features.append("✓ Async/await")
    else:
        missing.append("Async/await ausente")
    
    # ========== BONIFICACIONES (pueden sumar hasta 10 pts extra) ==========
    
    # Versión enterprise
    if 'v3.2.0' in content or 'VERSION = "3.2.0"' in content:
        score += 3
        features.append("✓ Versión 3.2.0")
    
    # Production ready marker
    if 'READY FOR PRODUCTION' in content:
        score += 3
        features.append("✓ Production-ready")
    
    # Documentación robusta
    if content.count('"""') >= 4 and len(content) > 10000:
        score += 2
        features.append("✓ Documentación completa")
    
    # Type hints completos
    if content.count('->') >= 10 and 'from typing import' in content:
        score += 2
        features.append("✓ Type hints")
    
    # Análisis de calidad del código
    lines = content.count('\n')
    size = len(content)
    
    return {
        'score': min(100, score),
        'features': features,
        'missing': missing,
        'lines': lines,
        'size': size
    }

def calculate_grade(score: int) -> Tuple[str, str]:
    """Calcula letra y emoji según score"""
    if score >= 95:
        return "A+", "🟢"
    elif score >= 90:
        return "A", "🟢"
    elif score >= 85:
        return "A-", "🟢"
    elif score >= 80:
        return "B+", "🟡"
    elif score >= 75:
        return "B", "🟡"
    elif score >= 70:
        return "B-", "🟡"
    elif score >= 60:
        return "C", "🟠"
    else:
        return "F", "🔴"

def print_score_bar(score: int, max_width: int = 50):
    """Imprime barra de progreso visual"""
    filled = int((score / 100) * max_width)
    bar = "█" * filled + "░" * (max_width - filled)
    return f"[{bar}] {score}/100"

def main():
    agents_dir = Path("agents/marketing")
    
    # Agentes a auditar
    agents_to_check = [
        "emailautomationia.py",
        "campaignoptimizeria.py",
        "leadscoringia.py",
        "influencermatcheria.py",
        "abtestingimpactia.py",
        "socialpostgeneratoria.py",
    ]
    
    results = []
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " AUDITORÍA COMPLETA DE AGENTES ACTUALIZADOS ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    total_old_score = 0
    total_new_score = 0
    
    for agent_name in agents_to_check:
        filepath = agents_dir / agent_name
        
        if not filepath.exists():
            print(f"❌ {agent_name}: No encontrado\n")
            continue
        
        analysis = analyze_agent_file(filepath)
        old_score = PREVIOUS_SCORES.get(agent_name, 0)
        new_score = analysis['score']
        improvement = new_score - old_score
        improvement_pct = (improvement / max(1, old_score)) * 100
        
        grade, emoji = calculate_grade(new_score)
        
        total_old_score += old_score
        total_new_score += new_score
        
        results.append({
            'name': agent_name,
            'old': old_score,
            'new': new_score,
            'improvement': improvement,
            'grade': grade,
            'emoji': emoji,
            'analysis': analysis
        })
        
        # Header del agente
        print("┌" + "─" * 78 + "┐")
        print(f"│ {emoji} {agent_name.upper():<73} │")
        print("├" + "─" * 78 + "┤")
        
        # Scores
        print(f"│ Score ANTERIOR: {old_score:>3}/100 │ Score ACTUAL: {new_score:>3}/100 │ Mejora: {improvement:+3} pts ({improvement_pct:+6.0f}%) │")
        print(f"│ Calificación: {grade:>3} {emoji}                                                    │")
        print("│ " + print_score_bar(new_score, 72) + " │")
        print("├" + "─" * 78 + "┤")
        
        # Metadata
        print(f"│ Tamaño: {analysis['lines']:>5} líneas, {analysis['size']:>7} chars │ Features: {len(analysis['features']):>2} │ Missing: {len(analysis['missing']):>2} │")
        print("├" + "─" * 78 + "┤")
        
        # Features implementados
        if analysis['features']:
            print("│ FEATURES IMPLEMENTADOS:".ljust(79) + "│")
            for feature in analysis['features'][:8]:
                print(f"│   {feature:<74} │")
        
        # Missing features
        if analysis['missing'] and new_score < 100:
            print("│ PARA LLEGAR A 100/100:".ljust(79) + "│")
            for miss in analysis['missing'][:5]:
                print(f"│   ❌ {miss:<71} │")
        
        print("└" + "─" * 78 + "┘")
        print()
    
    # RESUMEN GENERAL
    print("╔" + "═" * 78 + "╗")
    print("║" + " RESUMEN GENERAL ".center(78) + "║")
    print("╠" + "═" * 78 + "╣")
    
    avg_old = total_old_score / len(results)
    avg_new = total_new_score / len(results)
    avg_improvement = avg_new - avg_old
    avg_improvement_pct = (avg_improvement / max(1, avg_old)) * 100
    
    print(f"║ Agentes auditados: {len(results):<62} ║")
    print(f"║ Score promedio ANTERIOR: {avg_old:>5.1f}/100                                          ║")
    print(f"║ Score promedio ACTUAL:   {avg_new:>5.1f}/100                                          ║")
    print(f"║ Mejora promedio:         {avg_improvement:+5.1f} puntos ({avg_improvement_pct:+6.0f}%)                           ║")
    print("╠" + "═" * 78 + "╣")
    
    # Distribución
    grades_count = {}
    for r in results:
        grades_count[r['grade']] = grades_count.get(r['grade'], 0) + 1
    
    print("║ DISTRIBUCIÓN DE CALIFICACIONES:                                               ║")
    for grade in ["A+", "A", "A-", "B+", "B", "B-", "C", "F"]:
        count = grades_count.get(grade, 0)
        if count > 0:
            emoji = calculate_grade(95 if grade == "A+" else 90)[1]
            print(f"║   {emoji} {grade:>3}: {count} agente(s)                                                      ║")
    
    print("╠" + "═" * 78 + "╣")
    
    # Top 3
    top3 = sorted(results, key=lambda x: x['new'], reverse=True)[:3]
    print("║ TOP 3 AGENTES:                                                                 ║")
    for i, r in enumerate(top3, 1):
        print(f"║   {i}. {r['emoji']} {r['name']:<40} Score: {r['new']}/100 ({r['grade']}) ║")
    
    print("╠" + "═" * 78 + "╣")
    
    # Necesitan trabajo
    need_work = [r for r in results if r['new'] < 95]
    if need_work:
        print("║ AGENTES QUE AÚN NO ESTÁN EN 95+:                                              ║")
        for r in need_work:
            gap = 95 - r['new']
            print(f"║   {r['emoji']} {r['name']:<40} Gap: {gap} puntos         ║")
    else:
        print("║ 🎉 ¡TODOS LOS AGENTES ESTÁN EN 95+! EXCELENTE TRABAJO                         ║")
    
    print("╚" + "═" * 78 + "╝")
    print()
    
    # RECOMENDACIONES
    if any(r['new'] < 100 for r in results):
        print("💡 RECOMENDACIONES PARA LLEGAR A 100/100:")
        print("   1. Agregar percentiles (p95/p99) en get_metrics()")
        print("   2. Implementar logging estructurado con extra={} en todos los logs")
        print("   3. Agregar type hints completos en todas las funciones")
        print("   4. Documentar cada método con docstrings detallados")
        print("   5. Agregar unit tests específicos por agente")

if __name__ == "__main__":
    main()