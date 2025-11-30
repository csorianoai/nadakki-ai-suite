# ============================================================
# MONITOR ENTERPRISE v4.6 – QUANTUM SENTINEL EDITION
# ============================================================

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx, asyncio, time, os, json, platform, threading
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACIÓN BASE
# ============================================================

router = APIRouter(prefix="/monitor/v4")
BASE_URL = "http://127.0.0.1:8000"

ENDPOINTS_REALES = [
    ("/health", "Health Check", "🫀 Sistema Base"),
    ("/docs", "API Docs", "📚 Documentación Swagger"),
    ("/api/v1/wp/agents", "WP Agents", "🌐 WordPress Integration"),
]

BASE_PATH = Path(__file__).resolve().parent
LOG_DIR = BASE_PATH / "logs" / "alerts"
DATA_DIR = BASE_PATH / "exports"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 🔔 CONFIGURAR TU TOKEN Y CHAT_ID DE TELEGRAM AQUÍ
TELEGRAM_TOKEN = "TU_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TU_CHAT_ID"

# ============================================================
# FRONTEND FUTURISTA – Quantum Sentinel Dashboard
# ============================================================

@router.get("/", response_class=HTMLResponse)
async def monitor_dashboard(_: Request):
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>🚀 NADAKKI QUANTUM SENTINEL 4.6</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
        <style>
            body {background: linear-gradient(135deg, #0a0a1a, #15152b);color: #fff;
                  font-family: 'Rajdhani', sans-serif;margin: 0;padding: 0;overflow-x: hidden;}
            h1 {font-family: 'Orbitron';text-align: center;font-size: 3rem;
                background: linear-gradient(90deg, #00f3ff, #b967ff);
                -webkit-background-clip: text;-webkit-text-fill-color: transparent;
                text-shadow: 0 0 25px rgba(0,243,255,0.5);}
            .grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
                   gap:1.5rem;padding:2rem;}
            .card {background:rgba(42,42,74,0.7);border:1px solid #2a2a4a;border-radius:12px;
                   text-align:center;padding:1.5rem;box-shadow:0 0 20px rgba(0,243,255,0.1);}
            .value {font-family:'Orbitron';font-size:2rem;}
            .latency{color:#00ff88}.success{color:#00f3ff}.uptime{color:#ff6b35}
            table{width:100%;border-collapse:collapse;margin-top:1rem}
            th,td{padding:10px;border-bottom:1px solid rgba(255,255,255,0.1);text-align:left}
            th{color:#b967ff;font-family:'Orbitron';letter-spacing:1px;text-transform:uppercase}
            .status-online{background:linear-gradient(45deg,#00ff88,#00cc6a);
                           color:#000;padding:.4rem .8rem;border-radius:6px;}
            .status-offline{background:linear-gradient(45deg,#ff4757,#ff3742);
                            color:#fff;padding:.4rem .8rem;border-radius:6px;}
            .refresh{display:block;margin:1rem auto;background:linear-gradient(45deg,#00f3ff,#b967ff);
                     border:none;color:#000;padding:1rem 2rem;border-radius:50px;font-family:'Orbitron';
                     font-weight:700;cursor:pointer;box-shadow:0 0 25px rgba(0,243,255,0.3);}
        </style>
    </head>
    <body>
        <h1>🛰️ NADAKKI QUANTUM SENTINEL</h1>
        <div class="grid" id="statsGrid"></div>
        <div style="margin:2rem;">
            <canvas id="quantumChart" height="300"></canvas>
            <table id="endpointsTable"><thead><tr><th>Servicio</th><th>Estado</th><th>Latencia</th></tr></thead><tbody></tbody></table>
        </div>
        <button class="refresh" onclick="loadQuantum()">⚡ REFRESH QUANTUM</button>
        <script>
            let chart,dataPoints=[];
            async function loadQuantum(){
                const r=await fetch('/monitor/v4/data');
                const d=await r.json();
                document.getElementById('statsGrid').innerHTML=
                  `<div class='card'><div class='value latency'>${d.avg_latency}ms</div><div>Latencia</div></div>
                   <div class='card'><div class='value success'>${d.success_rate}%</div><div>Éxito</div></div>
                   <div class='card'><div class='value'>${d.active_endpoints}/${d.total_endpoints}</div><div>Activos</div></div>
                   <div class='card'><div class='value uptime'>${d.uptime}%</div><div>Uptime</div></div>`;
                const tb=document.querySelector('#endpointsTable tbody');
                tb.innerHTML=d.endpoints.map(e=>`<tr>
                    <td>${e.name}</td>
                    <td><span class='${e.success?"status-online":"status-offline"}'>
                    ${e.success?"OPERATIONAL":"OFFLINE"}</span></td>
                    <td>${e.latency}ms</td></tr>`).join('');
                dataPoints.push(d.avg_latency); if(dataPoints.length>10)dataPoints.shift();
                const ctx=document.getElementById('quantumChart').getContext('2d');
                if(chart)chart.destroy();
                chart=new Chart(ctx,{type:'line',
                    data:{labels:dataPoints.map((_,i)=>i+1),
                        datasets:[{label:'Latencia',data:dataPoints,borderColor:'#00f3ff',
                                   backgroundColor:'rgba(0,243,255,0.1)',borderWidth:3,tension:0.4,fill:true}]},
                    options:{plugins:{legend:{labels:{color:'#00f3ff'}}},
                        scales:{x:{ticks:{color:'#a0a0c0'}},y:{ticks:{color:'#a0a0c0'}}}}});
            }
            loadQuantum(); setInterval(loadQuantum,10000);
        </script>
    </body></html>
    """
    return HTMLResponse(html)

# ============================================================
# BACKEND – Data, Export, Alert & Notifications
# ============================================================

@router.get("/data", response_class=JSONResponse)
async def monitor_data():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[check_endpoint(client, ep[0], ep[1], ep[2]) for ep in ENDPOINTS_REALES])

    ok = [r for r in results if r["success"]]
    avg = round(sum(r["latency"] for r in ok)/len(ok),2) if ok else 0
    success_rate = round((len(ok)/len(ENDPOINTS_REALES))*100,2)
    uptime = round((success_rate/100)*99.9,2)

    # Alertas
    alerts = [r for r in results if not r["success"] or (r["latency"] > 3000 and r["latency"] != -1)]
    if alerts:
        log_alert(alerts)
        send_notifications(alerts)

    # Exportar JSON para Power BI
    export_data({
        "timestamp": datetime.now().isoformat(),
        "avg_latency": avg,
        "success_rate": success_rate,
        "uptime": uptime,
        "active_endpoints": len(ok),
        "total_endpoints": len(ENDPOINTS_REALES),
        "endpoints": results
    })

    return {
        "timestamp": datetime.now().isoformat(),
        "avg_latency": avg,
        "success_rate": success_rate,
        "uptime": uptime,
        "active_endpoints": len(ok),
        "total_endpoints": len(ENDPOINTS_REALES),
        "endpoints": results
    }

# ============================================================
# FUNCIONES DE SOPORTE
# ============================================================

async def check_endpoint(client, path, name, desc):
    url = BASE_URL + path
    t0 = time.perf_counter()
    try:
        resp = await client.get(url, timeout=5.0)
        latency = round((time.perf_counter()-t0)*1000,2)
        return {"name": f"{desc}", "path": path, "status": resp.status_code,
                "latency": latency, "success": resp.status_code==200}
    except Exception as e:
        return {"name": f"{desc}", "path": path, "status": "ERROR",
                "latency": -1, "success": False, "error": str(e)}

def log_alert(alerts):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"alerts_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{now}] ⚠️ {len(alerts)} ALERTAS DETECTADAS\n")
        for a in alerts:
            f.write(f" - {a['name']} ({a['path']}) => {a['status']} / {a['latency']} ms\n")
    print(f"⚠️ ALERTA DETECTADA ({len(alerts)} eventos) — revisa {log_file}")

def export_data(data):
    """Guarda export JSON compatible con Power BI"""
    file = DATA_DIR / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Exportación JSON actualizada: {file}")

def send_notifications(alerts):
    """Envía alertas a Telegram y Windows Toast"""
    alert_msg = f"⚠️ {len(alerts)} alerta(s) en Nadakki Quantum Sentinel:\n" + \
                "\n".join([f"{a['name']} ({a['path']}) → {a['status']} [{a['latency']} ms]" for a in alerts])
    threading.Thread(target=notify_telegram, args=(alert_msg,)).start()
    if platform.system() == "Windows":
        threading.Thread(target=notify_windows, args=(alert_msg,)).start()

def notify_telegram(message):
    """Notifica por Telegram usando bot API"""
    if TELEGRAM_TOKEN == "TU_TELEGRAM_BOT_TOKEN":
        print("⚠️ Telegram Bot no configurado, omitiendo notificación.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        httpx.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        print("📨 Notificación enviada a Telegram.")
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {e}")

def notify_windows(message):
    """Muestra notificación tipo Toast en Windows"""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast("⚠️ Nadakki Alert", message, duration=10, threaded=True)
        print("🔔 Notificación Windows enviada.")
    except Exception as e:
        print(f"❌ Error Toast Windows: {e}")

print("✅ NADAKKI QUANTUM SENTINEL v4.6 ACTIVADO")
print("📊 Dashboard: http://127.0.0.1:8000/monitor/v4/")
print("🔔 Notificaciones activas (Telegram + Windows)")
print("📈 Export JSON Power BI: /exports/metrics_YYYYMMDD.json")
