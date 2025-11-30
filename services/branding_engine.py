"""
Branding Engine - Genera dashboards white-label dinámicos
Componente 3/3 del sistema multi-tenant
"""

import sqlite3
from pathlib import Path
import json
from typing import Dict, Optional

class BrandingEngine:
    """
    Motor de branding para dashboards white-label
    Genera interfaces personalizadas para cada tenant
    """
    
    def __init__(self, db_path: str = "tenants.db"):
        self.db_path = db_path
    
    def get_tenant_branding(self, tenant_id: str) -> Optional[Dict]:
        """Obtiene configuración de branding de un tenant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.institution_name,
                b.primary_color, 
                b.secondary_color, 
                b.logo_url,
                t.plan
            FROM tenants t
            LEFT JOIN tenant_branding b ON t.tenant_id = b.tenant_id
            WHERE t.tenant_id = ?
        """, (tenant_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        institution_name, primary_color, secondary_color, logo_url, plan = row
        
        return {
            "institution_name": institution_name,
            "primary_color": primary_color or "#1e40af",
            "secondary_color": secondary_color or "#3b82f6", 
            "logo_url": logo_url or f"https://ui-avatars.com/api/?name={institution_name.replace(' ', '+')}",
            "plan": plan
        }
    
    def generate_dashboard_html(self, tenant_id: str) -> str:
        """
        Genera dashboard HTML completo con branding del tenant
        """
        branding = self.get_tenant_branding(tenant_id)
        
        if not branding:
            return "<html><body><h1>Tenant no encontrado</h1></body></html>"
        
        # CSS dinámico basado en branding
        css = f"""
        <style>
            :root {{
                --primary-color: {branding['primary_color']};
                --secondary-color: {branding['secondary_color']};
            }}
            .header {{ background: linear-gradient(135deg, {branding['primary_color']}, {branding['secondary_color']}); }}
            .card {{ border-left: 4px solid {branding['primary_color']}; }}
            .btn-primary {{ background: {branding['primary_color']}; }}
        </style>
        """
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{branding['institution_name']} - Nadakki AI</title>
    {css}
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ color: white; padding: 2rem; display: flex; align-items: center; gap: 1rem; }}
        .logo {{ width: 50px; height: 50px; background: white; border-radius: 8px; padding: 5px; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .card {{ background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card-title {{ font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem; color: #333; }}
        .metric {{ font-size: 2rem; font-weight: bold; color: #1e40af; }}
        .btn-primary {{ color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <img src="{branding['logo_url']}" alt="Logo" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
        <div>
            <h1 style="margin: 0;">{branding['institution_name']}</h1>
            <p style="margin: 0; opacity: 0.9;">Powered by Nadakki AI | {branding['plan'].upper()} Plan</p>
        </div>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-title">📊 Uso del Mes</div>
                <div class="metric" id="usage-metric">0</div>
                <div>evaluaciones realizadas</div>
                <button class="btn-primary" style="margin-top: 1rem; width: 100%;" onclick="viewUsage()">
                    Ver Detalles
                </button>
            </div>
            
            <div class="card">
                <div class="card-title">⚡ Nueva Evaluación</div>
                <p>Evalúa solicitantes en <3 segundos con 40 agentes AI</p>
                <button class="btn-primary" style="margin-top: 1rem; width: 100%;" onclick="newEvaluation()">
                    Iniciar Evaluación
                </button>
            </div>
            
            <div class="card">
                <div class="card-title">📈 Reportes</div>
                <p>Genera reportes detallados de riesgo y fraude</p>
                <button class="btn-primary" style="margin-top: 1rem; width: 100%;" onclick="generateReports()">
                    Crear Reportes
                </button>
            </div>
        </div>
    </div>

    <script>
        const tenantId = '{tenant_id}';
        
        // Simular carga de datos
        setTimeout(() => {{
            document.getElementById('usage-metric').textContent = '1,247';
        }}, 1000);
        
        function viewUsage() {{
            alert('Mostrando uso para: ' + tenantId);
        }}
        
        function newEvaluation() {{
            alert('Iniciando evaluación para: ' + tenantId);
        }}
        
        function generateReports() {{
            alert('Generando reportes para: ' + tenantId);
        }}
    </script>
</body>
</html>
        """
        
        return html_template
    
    def save_dashboard(self, tenant_id: str, output_dir: str = "dashboards"):
        """Guarda dashboard como archivo HTML"""
        Path(output_dir).mkdir(exist_ok=True)
        
        html = self.generate_dashboard_html(tenant_id)
        file_path = Path(output_dir) / f"{tenant_id}_dashboard.html"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(file_path)

# Prueba del Branding Engine
if __name__ == "__main__":
    print("🎨 BRANDING ENGINE - COMPONENTE 3/3")
    print("=" * 50)
    
    engine = BrandingEngine()
    
    # Probar con tenants
    test_tenants = ["credicefi_b27fa331", "banco-popular-rd", "banreservas-rd"]
    
    for tenant in test_tenants:
        print(f"\n--- Generando dashboard para {tenant} ---")
        
        branding = engine.get_tenant_branding(tenant)
        if branding:
            print(f"✅ Branding: {branding['institution_name']}")
            dashboard_path = engine.save_dashboard(tenant)
            print(f"📁 Dashboard: {dashboard_path}")
        else:
            print(f"⚠️  Tenant no encontrado: {tenant}")
    
    print(f"\n✅ Branding Engine - COMPONENTE 3/3 LISTO")
