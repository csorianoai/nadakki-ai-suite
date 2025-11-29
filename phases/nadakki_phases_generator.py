#!/usr/bin/env python3
import os
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path.cwd()
PHASES_DIR = PROJECT_ROOT / "phases"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PHASES_CONFIG = [
    {"id": 83, "slug": "webhook_processing", "nombre": "Webhook Processing", "tipo": "backend", "lenguaje": "python", "descripcion": "Sistema de procesamiento de webhooks", "componentes": ["webhook_manager.py"], "tecnologias": ["FastAPI", "Redis"]},
    {"id": 84, "slug": "payment_processing", "nombre": "Payment Processing", "tipo": "backend", "lenguaje": "python", "descripcion": "Integracion Stripe", "componentes": ["stripe_service.py"], "tecnologias": ["Stripe API"]},
    {"id": 85, "slug": "notifications", "nombre": "Notifications", "tipo": "backend", "lenguaje": "python", "descripcion": "Email y SMS", "componentes": ["email_service.py"], "tecnologias": ["SendGrid"]},
    {"id": 86, "slug": "auth_ui", "nombre": "Auth UI", "tipo": "frontend", "lenguaje": "react", "descripcion": "Login con Auth0", "componentes": ["LoginPage.jsx"], "tecnologias": ["React"]},
    {"id": 87, "slug": "dashboard", "nombre": "Dashboard", "tipo": "frontend", "lenguaje": "react", "descripcion": "Panel de control", "componentes": ["Dashboard.jsx"], "tecnologias": ["React"]},
    {"id": 88, "slug": "analytics", "nombre": "Analytics Engine", "tipo": "backend", "lenguaje": "python", "descripcion": "Motor de analisis", "componentes": ["analytics_engine.py"], "tecnologias": ["Pandas"]},
    {"id": 89, "slug": "reporting", "nombre": "Advanced Reporting", "tipo": "backend", "lenguaje": "python", "descripcion": "Generacion de reportes", "componentes": ["report_generator.py"], "tecnologias": ["ReportLab"]},
    {"id": 90, "slug": "admin_panel", "nombre": "Admin Panel", "tipo": "frontend", "lenguaje": "react", "descripcion": "Panel administrativo", "componentes": ["AdminPanel.jsx"], "tecnologias": ["React"]},
    {"id": 91, "slug": "compliance", "nombre": "Compliance Module", "tipo": "backend", "lenguaje": "python", "descripcion": "AML, KYC, GDPR", "componentes": ["compliance_checker.py"], "tecnologias": ["FastAPI"]},
    {"id": 92, "slug": "marketplace", "nombre": "Integration Marketplace", "tipo": "backend", "lenguaje": "python", "descripcion": "Marketplace de integraciones", "componentes": ["integration_manager.py"], "tecnologias": ["FastAPI"]},
    {"id": 93, "slug": "mobile_api", "nombre": "Mobile API", "tipo": "backend", "lenguaje": "python", "descripcion": "API para movil", "componentes": ["mobile_api.py"], "tecnologias": ["FastAPI"]},
    {"id": 94, "slug": "monitoring", "nombre": "Monitoring & Alerts", "tipo": "infraestructura", "lenguaje": "yaml", "descripcion": "Prometheus y Grafana", "componentes": ["prometheus.yml"], "tecnologias": ["Prometheus"]},
    {"id": 95, "slug": "backup_dr", "nombre": "Backup & DR", "tipo": "infraestructura", "lenguaje": "python", "descripcion": "Backup y recuperacion", "componentes": ["backup_manager.py"], "tecnologias": ["AWS"]},
    {"id": 96, "slug": "ci_cd_pipeline", "nombre": "CI/CD", "tipo": "infraestructura", "lenguaje": "yaml", "descripcion": "GitHub Actions", "componentes": ["ci-cd.yml"], "tecnologias": ["GitHub Actions"]},
    {"id": 97, "slug": "terraform", "nombre": "IaC", "tipo": "infraestructura", "lenguaje": "terraform", "descripcion": "Terraform AWS", "componentes": ["main.tf"], "tecnologias": ["Terraform"]},
]

class PhasesGenerator:
    def __init__(self):
        self.phases_dir = PHASES_DIR
        self.results = []
    
    def generate_all_phases(self):
        print(f"\n{'='*80}")
        print(f"🚀 NADAKKI PHASES GENERATOR - INICIANDO")
        print(f"{'='*80}\n")
        
        self.phases_dir.mkdir(exist_ok=True)
        
        for phase in PHASES_CONFIG:
            try:
                self._generate_phase(phase)
                self.results.append({"id": phase["id"], "nombre": phase["nombre"], "status": "✅"})
            except Exception as e:
                self.results.append({"id": phase["id"], "nombre": phase["nombre"], "status": f"❌ {e}"})
        
        self._print_summary()
    
    def _generate_phase(self, phase):
        phase_dir = self.phases_dir / f"{phase['id']}_{phase['slug']}"
        phase_dir.mkdir(exist_ok=True)
        
        print(f"📁 FASE {phase['id']}: {phase['nombre']}")
        
        readme = f"""# {phase['nombre']} - Fase {phase['id']}

Descripcion: {phase['descripcion']}

Timestamp: {TIMESTAMP}

## Tecnologias
{', '.join(phase['tecnologias'])}

## Componentes
{chr(10).join(f"- {c}" for c in phase['componentes'])}

## Checklist
- [ ] Implementar funcionalidad
- [ ] Tests unitarios
- [ ] Documentacion
- [ ] Deploy

Generado automaticamente por NADAKKI Phases Generator
"""
        (phase_dir / "README.md").write_text(readme)
        print(f"   - README.md")
        
        config = json.dumps(phase, indent=2, ensure_ascii=False)
        (phase_dir / "config.json").write_text(config)
        print(f"   - config.json")
        
        (phase_dir / ".gitkeep").touch()
        print(f"   Completada\n")
    
    def _print_summary(self):
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL")
        print(f"{'='*80}\n")
        
        for result in self.results:
            print(f"   Fase {result['id']:2d} - {result['nombre']:30s} {result['status']}")
        
        completed = sum(1 for r in self.results if "✅" in r["status"])
        total = len(self.results)
        percentage = (completed/total)*100
        
        print(f"\n   Completadas: {completed}/{total} ({percentage:.0f}%)")
        print(f"   Ubicacion: {self.phases_dir}\n")

if __name__ == "__main__":
    generator = PhasesGenerator()
    generator.generate_all_phases()
    print("GENERACION EXITOSA!\n")