# certification_dashboard.py
"""
Dashboard visual de certificación de agentes operativos
"""

import json
from pathlib import Path
from datetime import datetime
import webbrowser

def generate_html_dashboard():
    """Genera dashboard HTML interactivo"""
    
    print("🎨 GENERANDO DASHBOARD VISUAL DE CERTIFICACIÓN")
    print("="*60)
    
    # Leer datos de certificación
    cert_dir = Path("certifications")
    if not cert_dir.exists():
        print("❌ No hay datos de certificación")
        return
    
    # Encontrar reporte consolidado
    report_file = cert_dir / "consolidated_certification_report.json"
    if not report_file.exists():
        print("❌ No se encontró reporte consolidado")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Generar HTML
    html_content = f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NADAKKI - Dashboard de Certificación Operativa</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            padding: 30px 0; 
            border-bottom: 2px solid #3b82f6;
            margin-bottom: 30px;
        }}
        .header h1 {{ 
            font-size: 2.8rem; 
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }}
        .header .subtitle {{ 
            font-size: 1.2rem; 
            color: #94a3b8;
            margin-bottom: 20px;
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; 
            margin-bottom: 40px;
        }}
        .stat-card {{ 
            background: rgba(30, 41, 59, 0.7);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #334155;
            transition: transform 0.3s, border-color 0.3s;
        }}
        .stat-card:hover {{ 
            transform: translateY(-5px);
            border-color: #3b82f6;
        }}
        .stat-card h3 {{ 
            font-size: 0.9rem; 
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-value {{ 
            font-size: 2.5rem; 
            font-weight: bold;
            color: #60a5fa;
        }}
        .stat-card.enterprise {{ border-left: 4px solid #10b981; }}
        .stat-card.certified {{ border-left: 4px solid #3b82f6; }}
        .stat-card.average {{ border-left: 4px solid #8b5cf6; }}
        .stat-card.total {{ border-left: 4px solid #f59e0b; }}
        
        .agents-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .agent-card {{ 
            background: rgba(30, 41, 59, 0.7);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
        }}
        .agent-header {{ 
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .agent-name {{ 
            font-size: 1.3rem;
            font-weight: bold;
            color: #e2e8f0;
        }}
        .agent-score {{ 
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .progress-bar {{ 
            height: 10px;
            background: #334155;
            border-radius: 5px;
            margin: 15px 0;
            overflow: hidden;
        }}
        .progress-fill {{ 
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            border-radius: 5px;
        }}
        .capabilities {{ 
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        .capability {{ 
            background: #1e293b;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            border: 1px solid #475569;
        }}
        .capability.true {{ border-color: #10b981; color: #10b981; }}
        .capability.false {{ border-color: #ef4444; color: #ef4444; }}
        
        .level-badge {{ 
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-top: 10px;
        }}
        .level-5 {{ background: linear-gradient(90deg, #8b5cf6, #ec4899); }}
        .level-4 {{ background: linear-gradient(90deg, #3b82f6, #8b5cf6); }}
        .level-3 {{ background: linear-gradient(90deg, #10b981, #3b82f6); }}
        .level-2 {{ background: linear-gradient(90deg, #f59e0b, #10b981); }}
        .level-1 {{ background: linear-gradient(90deg, #ef4444, #f59e0b); }}
        .level-0 {{ background: #64748b; }}
        
        .footer {{ 
            text-align: center;
            padding: 20px;
            color: #94a3b8;
            font-size: 0.9rem;
            border-top: 1px solid #334155;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 NADAKKI OPERATIVE</h1>
            <div class="subtitle">Sistema de Certificación de Agentes Autónomos</div>
            <div>Última actualización: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <h3>Agentes Totales</h3>
                <div class="stat-value">{data["statistics"]["total_agents"]}</div>
                <div class="stat-desc">Sistema completo</div>
            </div>
            
            <div class="stat-card certified">
                <h3>Certificados (≥60)</h3>
                <div class="stat-value">{data["statistics"]["certified"]}</div>
                <div class="stat-desc">Listos para producción</div>
            </div>
            
            <div class="stat-card enterprise">
                <h3>Enterprise Ready (≥80)</h3>
                <div class="stat-value">{data["statistics"]["enterprise_ready"]}</div>
                <div class="stat-desc">Nivel elite</div>
            </div>
            
            <div class="stat-card average">
                <h3>Puntuación Promedio</h3>
                <div class="stat-value">{data["statistics"]["average_score"]:.1f}</div>
                <div class="stat-desc">/100 puntos</div>
            </div>
        </div>
        
        <div class="agents-grid">
'''
    
    # Agregar tarjetas de agentes
    agents_data = data.get("agents", {})
    for agent_name, agent_data in agents_data.items():
        score = agent_data["certification_score"]
        level = agent_data.get("certification_level", "ANALYTICAL")
        level_num = {"ANALYTICAL": 0, "OPERATIVE_BASIC": 1, "OPERATIVE_ADV": 2, 
                    "AUTONOMOUS": 3, "SELF_LEARNING": 4, "ENTERPRISE_ELITE": 5}.get(level, 0)
        
        html_content += f'''
            <div class="agent-card">
                <div class="agent-header">
                    <div class="agent-name">{agent_name}</div>
                    <div class="agent-score">{score:.1f}/100</div>
                </div>
                
                <div class="level-badge level-{level_num}">
                    {level} • Nivel {level_num}
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {score}%"></div>
                </div>
                
                <div>Estado: <strong>{agent_data.get("status", "UNKNOWN")}</strong></div>
                <div>{agent_data.get("level_description", "")}</div>
                
                <div class="capabilities">
'''
        
        # Agregar capacidades
        capabilities = agent_data.get("capabilities", {})
        for cap_name, cap_value in list(capabilities.items())[:6]:  # Mostrar primeras 6
            html_content += f'''
                    <div class="capability {str(cap_value).lower()}">
                        {cap_name}: {str(cap_value).upper()}
                    </div>
'''
        
        html_content += '''
                </div>
            </div>
'''
    
    # Cerrar HTML
    html_content += '''
        </div>
        
        <div class="footer">
            <p>NADAKKI AI Suite • Sistema Operative Elite v4.0</p>
            <p>© 2024-2026 • Todos los agentes certificados y listos para producción</p>
        </div>
    </div>
    
    <script>
        // Actualizar en tiempo real
        setTimeout(() => location.reload(), 30000); // Cada 30 segundos
        
        // Efectos de hover
        document.querySelectorAll('.agent-card').forEach(card => {{
            card.addEventListener('click', function() {{
                const agentName = this.querySelector('.agent-name').textContent;
                alert('Detalles de ' + agentName + '\\nPuntuación: ' + 
                      this.querySelector('.agent-score').textContent);
            }});
        }});
    </script>
</body>
</html>
'''
    
    # Guardar HTML
    dashboard_file = cert_dir / "certification_dashboard.html"
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard generado: {dashboard_file}")
    
    # Abrir en navegador
    try:
        webbrowser.open(f'file://{dashboard_file.absolute()}')
        print("🌐 Abriendo dashboard en navegador...")
    except:
        print("⚠️ No se pudo abrir automáticamente. Abre manualmente el archivo HTML.")
    
    return dashboard_file

if __name__ == "__main__":
    generate_html_dashboard()
