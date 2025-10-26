# =====================================================================================
# NADAKKI AI SUITE – WordPress Integration Auto Monitor v2.0
# =====================================================================================
# Este script realiza chequeos automáticos cada hora a los 3 endpoints principales:
#   /api/v1/wp/auth
#   /api/v1/wp/agents
#   /api/v1/wp/evaluate
# y guarda los resultados en logs diarios dentro de logs\wp_monitor\
# =====================================================================================

# --- CONFIGURACIÓN ---
$BaseUrl = "http://127.0.0.1:8000/api/v1/wp"
$Headers = @{ "X-Token" = "nadakki-secure" }
$LogRoot = "logs\wp_monitor"
$IntervalMinutes = 60  # Frecuencia de chequeo (puedes cambiarlo a 15 o 30 si lo prefieres)

# --- CREAR CARPETA DE LOGS SI NO EXISTE ---
if (-not (Test-Path $LogRoot)) {
    New-Item -ItemType Directory -Path $LogRoot | Out-Null
}

# --- FUNCIÓN PARA GUARDAR RESULTADOS ---
function Log-Result($endpoint, $status, $latency, $message) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $dateFile = (Get-Date).ToString("yyyy-MM-dd")
    $logFile = "$LogRoot\monitor_$dateFile.log"
    $line = "$timestamp | $endpoint | $status | ${latency}ms | $message"
    Add-Content -Path $logFile -Value $line
    Write-Host $line -ForegroundColor Cyan
}

# --- FUNCIÓN PRINCIPAL DE TEST ---
function Run-Check {
    Write-Host "`n🧠 Ejecutando chequeo de integración WordPress <-> Nadakki AI Suite" -ForegroundColor Yellow
    $start = Get-Date

    # 1️⃣ AUTH
    try {
        $s = Get-Date
        $r = Invoke-RestMethod -Uri "$BaseUrl/auth" -Method POST -Headers $Headers -Body (@{source="WordPress"} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
        $t = [math]::Round(((Get-Date) - $s).TotalMilliseconds, 2)
        Log-Result "/auth" "OK" $t $r.status
    } catch { Log-Result "/auth" "ERROR" 0 $_.Exception.Message }

    # 2️⃣ AGENTS
    try {
        $s = Get-Date
        $r = Invoke-RestMethod -Uri "$BaseUrl/agents" -Method GET -Headers $Headers -TimeoutSec 10
        $t = [math]::Round(((Get-Date) - $s).TotalMilliseconds, 2)
        Log-Result "/agents" "OK" $t "$($r.agents_count) agentes activos"
    } catch { Log-Result "/agents" "ERROR" 0 $_.Exception.Message }

    # 3️⃣ EVALUATE
    try {
        $s = Get-Date
        $body = @{agent_id="lead_scoring"; data=@{cliente="prueba";score=720}} | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "$BaseUrl/evaluate" -Method POST -Headers $Headers -Body $body -ContentType "application/json" -TimeoutSec 10
        $t = [math]::Round(((Get-Date) - $s).TotalMilliseconds, 2)
        Log-Result "/evaluate" "OK" $t "Agent $($r.agent)"
    } catch { Log-Result "/evaluate" "ERROR" 0 $_.Exception.Message }

    $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
    Write-Host "`n✅ Chequeo completado en $duration segundos" -ForegroundColor Green
    Write-Host "------------------------------------------------------------------"
}

# --- BUCLE INFINITO ---
Write-Host "`n🚀 Monitoreo automático iniciado. Se ejecutará cada $IntervalMinutes minutos." -ForegroundColor Cyan
Write-Host "Presiona CTRL + C para detenerlo.`n" -ForegroundColor DarkGray

while ($true) {
    Run-Check
    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
