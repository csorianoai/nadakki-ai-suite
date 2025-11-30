"""
NADAKKI AI SUITE - Monitor Dashboard v2.5 (Quantum Dark)
--------------------------------------------------------
Visual mejorado + Integración HTML para WordPress.
Incluye:
- Barras con gradiente
- Animaciones suaves
- Resumen de salud global
- Gráficos modernos con sombras y colores contrastantes
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
LOG_DIR = Path("logs/wp_monitor")
OUTPUT_HTML = LOG_DIR / "dashboard.html"

# ==========================================================
# LECTURA DE LOGS
# ==========================================================
def read_logs():
    data = []
    for file in sorted(LOG_DIR.glob("monitor_*.log")):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    parts = line.strip().split("|")
                    timestamp = parts[0].strip()
                    endpoint = parts[1].strip()
                    status = parts[2].strip()
                    latency = float(parts[3].replace("ms", "").strip())
                    message = parts[4].strip() if len(parts) > 4 else ""
                    data.append([timestamp, endpoint, status, latency, message])
                except Exception:
                    continue
    return pd.DataFrame(data, columns=["timestamp", "endpoint", "status", "latency", "message"])

# ==========================================================
# GENERAR DASHBOARD
# ==========================================================
def generate_dashboard(df: pd.DataFrame):
    if df.empty:
        OUTPUT_HTML.write_text("<h2>No se encontraron datos de monitoreo.</h2>", encoding="utf-8")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["ok"] = df["status"].eq("OK").astype(int)
    df["error"] = df["status"].eq("ERROR").astype(int)

    avg_latency = df["latency"].mean()
    uptime = (df["ok"].sum() / len(df)) * 100

    # ===== Estado de salud global =====
    if uptime >= 95:
        health_color, health_status = "#00ffa3", "ÓPTIMO"
    elif uptime >= 80:
        health_color, health_status = "#f7d33c", "ADVERTENCIA"
    else:
        health_color, health_status = "#ff4b4b", "CRÍTICO"

    stats = (
        df.groupby("endpoint")
        .agg(
            total=("status", "count"),
            ok=("ok", "sum"),
            error=("error", "sum"),
            avg_latency=("latency", "mean"),
        )
        .reset_index()
    )

    # ======================================================
    # HTML VISUAL QUANTUM
    # ======================================================
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>📊 Nadakki AI Suite - Monitor Quantum</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                background: radial-gradient(circle at 20% 20%, #0a0f1a, #05080d);
                color: #e6edf3;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 25px;
                overflow-x: hidden;
            }}
            h1 {{
                color: #58a6ff;
                text-align: center;
                font-weight: 600;
                font-size: 1.8rem;
                text-shadow: 0 0 8px rgba(88,166,255,0.6);
            }}
            .summary {{
                background: linear-gradient(135deg, #111a2b, #0b1220);
                border: 1px solid #1c2a3b;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 25px;
                box-shadow: 0 0 12px rgba(0, 255, 145, 0.15);
                text-align: center;
            }}
            .health {{
                color: {health_color};
                font-weight: bold;
                font-size: 1.3em;
            }}
            canvas {{
                margin: 20px auto;
                display: block;
                max-width: 800px;
                background-color: #0b0f16;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,255,145,0.08);
                padding: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 30px;
                font-size: 0.9em;
                box-shadow: 0 0 8px rgba(255,255,255,0.05);
            }}
            th, td {{
                border: 1px solid #1e2633;
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: #111a2b;
                color: #58a6ff;
                text-transform: uppercase;
            }}
            .ok {{ color: #00ffa3; }}
            .error {{ color: #ff4b4b; }}
        </style>
    </head>
    <body>
        <h1>📡 Nadakki AI Suite – Dashboard Quantum</h1>

        <div class="summary">
            <p><b>Promedio de Latencia:</b> {avg_latency:.2f} ms |
               <b>Uptime Global:</b> {uptime:.1f}% |
               <b>Estado del Sistema:</b> <span class="health">{health_status}</span></p>
            <p>Entradas Analizadas: {len(df)} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <canvas id="latencyChart" height="130"></canvas>

        <table>
            <thead>
                <tr>
                    <th>Endpoint</th>
                    <th>Solicitudes</th>
                    <th>Éxitos</th>
                    <th>Errores</th>
                    <th>Latencia Promedio (ms)</th>
                </tr>
            </thead>
            <tbody>
                {''.join(
                    f"<tr><td>{r.endpoint}</td>"
                    f"<td>{r.total}</td>"
                    f"<td class='ok'>{r.ok}</td>"
                    f"<td class='error'>{r.error}</td>"
                    f"<td>{r.avg_latency:.2f}</td></tr>"
                    for r in stats.itertuples()
                )}
            </tbody>
        </table>

        <script>
        const ctx = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {list(stats['endpoint'])},
                datasets: [{{
                    label: 'Latencia Promedio (ms)',
                    data: {list(stats['avg_latency'])},
                    backgroundColor: [
                        'rgba(0,255,163,0.8)',
                        'rgba(88,166,255,0.8)',
                        'rgba(255,75,75,0.8)',
                        'rgba(247,211,60,0.8)',
                        'rgba(0,255,255,0.8)'
                    ],
                    borderColor: '#0ff',
                    borderWidth: 1,
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#aaa' }}
                    }},
                    title: {{
                        display: true,
                        text: 'Latencias Promedio por Endpoint',
                        color: '#58a6ff',
                        font: {{ size: 16, weight: 'bold' }}
                    }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#ccc' }} }},
                    y: {{ ticks: {{ color: '#ccc' }}, beginAtZero: true }}
                }}
            }}
        }});
        </script>
    </body>
    </html>
    """

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard Quantum generado: {OUTPUT_HTML.absolute()}")

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    if not LOG_DIR.exists():
        print("❌ No se encontró el directorio de logs.")
    else:
        df = read_logs()
        generate_dashboard(df)
