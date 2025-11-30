# ════════════════════════════════════════════════════════
# NADAKKI AI SUITE - PHASE 3: SLA PERFORMANCE TEST
# Autor: César Soriano
# Fecha: 2025-10-23
# Objetivo: Medir latencia promedio y estado HTTP de endpoints FastAPI
# ════════════════════════════════════════════════════════

Write-Host "`nINICIANDO PHASE 3 - SLA PERFORMANCE TEST..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "logs/performance"
if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }
$logFile = "$reportDir/sla_report_$timestamp.log"

# Configuración de endpoints
$baseURL = "http://127.0.0.1:8000"
$endpoints = @(
    "/health",
    "/api/admin/tenants",
    "/api/marketing/lead-scoring",
    "/api/marketing/customer-segmentation"
)

# Función de medición
function Measure-Latency {
    param($url)
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        $sw.Stop()
        $ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
        return [PSCustomObject]@{
            URL       = $url
            Status    = $response.StatusCode
            Latency   = $ms
            Timestamp = (Get-Date).ToString("HH:mm:ss")
        }
    } catch {
        return [PSCustomObject]@{
            URL       = $url
            Status    = "ERROR"
            Latency   = -1
            Timestamp = (Get-Date).ToString("HH:mm:ss")
        }
    }
}

# Ejecutar mediciones
Write-Host "`nEjecutando pruebas de latencia..." -ForegroundColor Yellow
$results = @()
foreach ($ep in $endpoints) {
    $url = "$baseURL$ep"
    $measure = Measure-Latency -url $url
    $results += $measure
    Write-Host ("{0,-45} {1,10} {2,10} ms" -f $ep, $measure.Status, $measure.Latency) -ForegroundColor Green
    Add-Content $logFile ("[{0}] {1} - Status: {2} - {3} ms" -f $measure.Timestamp, $ep, $measure.Status, $measure.Latency)
}

# Calcular promedios
$valid = $results | Where-Object { $_.Latency -gt 0 }
if ($valid.Count -gt 0) {
    $avg = [math]::Round(($valid | Measure-Object -Property Latency -Average).Average, 2)
    Add-Content $logFile "`n--- RESUMEN FINAL ---"
    Add-Content $logFile "Promedio general: $avg ms"
    Add-Content $logFile "Endpoints probados: $($valid.Count)"
    Write-Host "`nPromedio de latencia: $avg ms" -ForegroundColor Cyan
    if ($avg -le 3000) {
        Write-Host "SLA Cumplido (< 3000 ms)" -ForegroundColor Green
    } else {
        Write-Host "SLA Excedido (> 3000 ms)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nNo se pudieron medir latencias válidas." -ForegroundColor Red
}

Write-Host ""
Write-Host "PHASE 3 COMPLETADA." -ForegroundColor Green
Write-Host ("Log guardado en: " + $logFile) -ForegroundColor Cyan

