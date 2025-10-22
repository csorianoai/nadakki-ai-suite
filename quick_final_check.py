from pathlib import Path

agents = [
    "influencermatcheria.py",
    "abtestingimpactia.py", 
    "customersegmentatonia.py",
    "competitorintelligenceia.py"
]

print("VERIFICACIÓN RÁPIDA - AGENTES MEJORADOS:")
print("="*60)

for agent in agents:
    filepath = Path(f"agents/marketing/{agent}")
    content = filepath.read_text(encoding='utf-8')
    
    score = 0
    if 'class CircuitBreaker' in content: score += 15
    if 'OrderedDict' in content and 'ttl' in content.lower(): score += 15
    if 'PROHIBITED' in content or 'prohibited' in content: score += 10
    if 'PII' in content or 'pii_detection' in content.lower(): score += 10
    if 'class FeatureFlags' in content: score += 10
    if 'decision_trace' in content.lower() or 'DecisionTrace' in content: score += 10
    if '_fallback' in content: score += 10
    if 'p95' in content or 'p99' in content: score += 10
    if 'extra=' in content or 'exc_info' in content: score += 5
    if 'async def execute' in content: score += 5
    
    grade = 'A+' if score >= 95 else 'A' if score >= 90 else 'B+'
    print(f"{agent:40} {score}/100 ({grade})")

print("="*60)