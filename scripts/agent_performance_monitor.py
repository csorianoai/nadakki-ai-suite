import json
import os
from datetime import datetime

base_path = r"C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
log_dir = os.path.join(base_path, "logs")
report_dir = os.path.join(base_path, "reports")
os.makedirs(report_dir, exist_ok=True)

# Buscar el último archivo de auditoría
files = [f for f in os.listdir(log_dir) if f.startswith("marketing_audit_") and f.endswith(".json")]
latest = max(files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f))) if files else None

if not latest:
    print("❌ No se encontró archivo de auditoría marketing_audit_*.json")
    exit(1)

# Abrir con soporte para BOM
with open(os.path.join(log_dir, latest), "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Calcular puntuaciones simuladas por agente
report_lines = []
summary = {"OPTIMAL": 0, "REVIEW": 0, "REDESIGN": 0}
report_lines.append(f"# 🧠 Nadakki Marketing AI - Auditoría {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("| Agente | Estado | Score | Acción sugerida |")
report_lines.append("|---------|---------|--------|----------------|")

for item in data:
    score = round(0.7 + (hash(item['Endpoint']) % 30) / 100, 2)  # Score simulado entre 0.7–1.0
    status = "OPTIMAL" if score >= 0.85 else "REVIEW" if score >= 0.75 else "REDESIGN"
    summary[status] += 1
    action = {
        "OPTIMAL": "✅ Mantener agente",
        "REVIEW": "⚙️ Revisar datasets / prompts",
        "REDESIGN": "🧠 Rediseñar agente IA"
    }[status]
    report_lines.append(f"| {item['Endpoint']} | {item['Status']} | {score} | {action} |")

# Resumen visual
report_lines.append("\n## 📊 Resumen de salud de agentes")
report_lines.append(f"- 🟢 OPTIMAL: {summary['OPTIMAL']}")
report_lines.append(f"- 🟡 REVIEW: {summary['REVIEW']}")
report_lines.append(f"- 🔴 REDESIGN: {summary['REDESIGN']}")

# Guardar reporte final
report_path = os.path.join(report_dir, f"agent_performance_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"✅ Reporte generado: {report_path}")
print(f"💡 Ábrelo con: notepad \"{report_path}\"")
